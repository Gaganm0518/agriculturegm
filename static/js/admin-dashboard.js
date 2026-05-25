/**
 * Admin Dashboard JS
 * Handles fetching stats, rendering charts, and managing users.
 */

document.addEventListener('DOMContentLoaded', async () => {
    // 1. Verify Authentication & Admin Role
    const path = window.location.pathname;
    if (!path.includes('admin-dashboard')) return; // Only run on admin dashboard page

    const user = requireAuth();
    if (!user) return; // redirect happens in requireAuth

    if (user.role !== 'admin') {
        alert("Access Denied: You do not have administrator privileges.");
        window.location.href = '/dashboard.html';
        return;
    }

    // Display admin content and name
    document.getElementById('admin-content').style.display = 'block';

    // Sidebar & Logout logic
    document.getElementById('menu-toggle')?.addEventListener('click', () => {
        document.getElementById('sidebar').classList.toggle('active');
    });
    document.getElementById('logout-btn')?.addEventListener('click', async () => {
        await logout();
    });

    // 2. State for Users Table
    let currentPage = 1;
    const perPage = 10;
    let totalPages = 1;

    // 3. Init Dashboard Data
    await loadStats();
    await loadUsers();

    // 4. Load Stats & Render Charts
    async function loadStats() {
        try {
            const res = await apiGet('/admin/stats');
            if (!res || !res.success) return;

            const data = res.data;

            // Update KPI cards
            document.getElementById('stat-total-users').textContent = data.total_users || 0;
            document.getElementById('stat-total-preds').textContent = data.total_predictions || 0;
            document.getElementById('stat-today').textContent = data.predictions_today || 0;
            document.getElementById('stat-weekly').textContent = data.active_users_weekly || 0;

            renderTrendChart(data.trend_chart || []);
            renderTypeChart(data.distribution || {});

        } catch (error) {
            console.error("Failed to load admin stats", error);
        }
    }

    // 5. Load Users Table
    async function loadUsers() {
        try {
            const res = await apiGet(`/admin/users?page=${currentPage}&per_page=${perPage}`);
            if (!res || !res.success) return;

            const users = res.data.users || [];
            totalPages = res.data.pagination.total_pages || 1;
            document.getElementById('page-info').textContent = `Page ${currentPage} of ${totalPages}`;

            const tbody = document.getElementById('user-table-body');
            tbody.innerHTML = '';

            if (users.length === 0) {
                tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;">No users found.</td></tr>';
                return;
            }

            users.forEach(u => {
                const tr = document.createElement('tr');
                
                const dateStr = u.created_at ? new Date(u.created_at).toLocaleDateString() : 'N/A';
                const roleClass = u.role === 'admin' ? 'role-admin' : 'role-farmer';

                tr.innerHTML = `
                    <td><strong>${u.name}</strong></td>
                    <td>${u.email}</td>
                    <td><span class="role-badge ${roleClass}">${u.role}</span></td>
                    <td>${u.predictions_count || 0}</td>
                    <td>${dateStr}</td>
                    <td>
                        <button class="action-btn edit-btn" data-id="${u.id}" data-name="${u.name}" data-role="${u.role}" title="Edit Role">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="action-btn delete delete-btn" data-id="${u.id}" title="Delete User">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                `;
                tbody.appendChild(tr);
            });

            // Attach event listeners to buttons
            document.querySelectorAll('.edit-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const id = e.currentTarget.dataset.id;
                    const name = e.currentTarget.dataset.name;
                    const role = e.currentTarget.dataset.role;
                    openEditModal(id, name, role);
                });
            });

            document.querySelectorAll('.delete-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const id = e.currentTarget.dataset.id;
                    deleteUser(id);
                });
            });

            // Update pagination buttons
            document.getElementById('prev-page').disabled = currentPage <= 1;
            document.getElementById('next-page').disabled = currentPage >= totalPages;

        } catch (error) {
            console.error("Failed to load users", error);
        }
    }

    // Pagination listeners
    document.getElementById('prev-page').addEventListener('click', () => {
        if (currentPage > 1) { currentPage--; loadUsers(); }
    });
    document.getElementById('next-page').addEventListener('click', () => {
        if (currentPage < totalPages) { currentPage++; loadUsers(); }
    });

    // 6. User Actions
    function openEditModal(id, name, role) {
        document.getElementById('edit-user-id').value = id;
        document.getElementById('edit-user-name').value = name;
        document.getElementById('edit-user-role').value = role;
        document.getElementById('edit-modal').classList.add('active');
    }

    document.getElementById('edit-user-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const id = document.getElementById('edit-user-id').value;
        const role = document.getElementById('edit-user-role').value;

        const res = await apiPut(`/admin/users/${id}`, { role: role });
        if (res && res.success) {
            document.getElementById('edit-modal').classList.remove('active');
            loadUsers(); // Refresh table
        } else {
            alert(res.error || "Failed to update user.");
        }
    });

    async function deleteUser(id) {
        if (!confirm("WARNING: Are you sure you want to permanently delete this user and all their prediction history? This action cannot be undone.")) {
            return;
        }

        const res = await apiDelete(`/admin/users/${id}`);
        if (res && res.success) {
            loadUsers();
            loadStats();
        } else {
            alert(res.error || "Failed to delete user.");
        }
    }

    // 7. Chart.js Rendering
    function renderTrendChart(dataArray) {
        const ctx = document.getElementById('trendChart').getContext('2d');
        const labels = dataArray.map(d => {
            const parts = d.date.split('-');
            return `${parts[1]}/${parts[2]}`; // MM/DD
        });
        const values = dataArray.map(d => d.count);

        new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Predictions',
                    data: values,
                    borderColor: '#16a34a',
                    backgroundColor: 'rgba(22, 163, 74, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.3,
                    pointBackgroundColor: '#16a34a'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: { beginAtZero: true, ticks: { stepSize: 1 } }
                }
            }
        });
    }

    function renderTypeChart(dist) {
        const ctx = document.getElementById('typeChart').getContext('2d');
        
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Crop Recs', 'Disease', 'Yield', 'Fertilizer'],
                datasets: [{
                    data: [dist.crop || 0, dist.disease || 0, dist.yield || 0, dist.fertilizer || 0],
                    backgroundColor: [
                        '#16a34a', // green
                        '#dc2626', // red
                        '#f59e0b', // amber
                        '#2563eb'  // blue
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom' }
                },
                cutout: '70%'
            }
        });
    }
});
