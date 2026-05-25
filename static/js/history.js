/**
 * Prediction History Page Logic.
 * Handles fetching, filtering, paginating, deleting, detail modal, and CSV export.
 */

document.addEventListener('DOMContentLoaded', () => {
    // Auth
    const user = requireAuth();
    if (user) {
    }

    // Sidebar
    const menuToggle = document.getElementById('menu-toggle');
    const sidebar = document.getElementById('sidebar');
    if (menuToggle && sidebar) {
        menuToggle.addEventListener('click', () => sidebar.classList.toggle('active'));
    }
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) logoutBtn.addEventListener('click', async () => { await logout(); });

    // State
    let currentType = 'all';
    let currentPage = 1;
    const perPage = 20;

    // DOM refs
    const historyList = document.getElementById('history-list');
    const emptyState = document.getElementById('empty-state');
    const loadingState = document.getElementById('loading-state');
    const paginationBar = document.getElementById('pagination-bar');
    const modal = document.getElementById('detail-modal');
    const modalBody = document.getElementById('modal-body');
    const modalTitle = document.getElementById('modal-title');
    const modalClose = document.getElementById('modal-close');

    // Filter tabs
    document.querySelectorAll('.filter-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            document.querySelectorAll('.filter-tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            currentType = tab.dataset.type;
            currentPage = 1;
            loadHistory();
        });
    });

    // Export CSV
    document.getElementById('export-btn').addEventListener('click', () => {
        const token = getToken();
        // Open a download link
        const a = document.createElement('a');
        a.href = `/api/history/export`;
        // We need to fetch with auth header, can't just link
        fetch('/api/history/export', {
            headers: { 'Authorization': `Bearer ${token}` }
        })
        .then(res => res.blob())
        .then(blob => {
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'smart_agri_history.csv';
            document.body.appendChild(a);
            a.click();
            a.remove();
            URL.revokeObjectURL(url);
        })
        .catch(() => alert('Failed to export CSV.'));
    });

    // Modal close
    modalClose.addEventListener('click', () => modal.classList.remove('visible'));
    modal.addEventListener('click', (e) => {
        if (e.target === modal) modal.classList.remove('visible');
    });

    // Type label map
    const typeLabels = {
        'crop_recommendation': 'Crop',
        'disease_detection': 'Disease',
        'yield_prediction': 'Yield',
        'fertilizer_recommendation': 'Fertilizer'
    };

    // Load history from API
    async function loadHistory() {
        historyList.innerHTML = '';
        paginationBar.innerHTML = '';
        emptyState.style.display = 'none';
        loadingState.style.display = 'block';

        const params = new URLSearchParams({
            type: currentType,
            page: currentPage,
            per_page: perPage
        });

        const res = await apiGet(`/history?${params.toString()}`);
        loadingState.style.display = 'none';

        if (!res || !res.success) {
            emptyState.style.display = 'block';
            return;
        }

        const items = res.data.history || [];
        const pagination = res.data.pagination || {};

        if (items.length === 0) {
            emptyState.style.display = 'block';
            return;
        }

        // Render cards
        items.forEach(item => {
            const card = document.createElement('div');
            card.className = 'history-card';

            const iconBg = hexToRGBA(item.badge_color || '#16a34a', 0.1);
            const typeLabel = typeLabels[item.prediction_type] || item.prediction_type;
            const dateStr = item.created_at ? formatDate(item.created_at) : 'Unknown date';

            card.innerHTML = `
                <div class="history-icon" style="background: ${iconBg}; color: ${item.badge_color};">
                    <i class="fas ${item.icon || 'fa-question-circle'}"></i>
                </div>
                <div class="history-body">
                    <span class="history-type" style="background: ${iconBg}; color: ${item.badge_color};">${typeLabel}</span>
                    <div class="history-summary">${item.summary || 'N/A'}</div>
                    <div class="history-date"><i class="fas fa-clock"></i> ${dateStr}</div>
                </div>
                <div class="history-actions">
                    <button class="btn-icon view-btn" title="View Details" data-id="${item.id}">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn-icon delete btn-delete" title="Delete" data-id="${item.id}">
                        <i class="fas fa-trash-alt"></i>
                    </button>
                </div>
            `;

            // View details
            card.querySelector('.view-btn').addEventListener('click', () => showModal(item));

            // Delete
            card.querySelector('.btn-delete').addEventListener('click', async (e) => {
                e.stopPropagation();
                if (!confirm('Delete this prediction record?')) return;

                const delRes = await apiDelete(`/history/${item.id}`);
                if (delRes && delRes.success) {
                    card.style.transition = 'opacity 0.3s, transform 0.3s';
                    card.style.opacity = '0';
                    card.style.transform = 'translateX(50px)';
                    setTimeout(() => {
                        card.remove();
                        // Check if list is now empty
                        if (historyList.children.length === 0) {
                            emptyState.style.display = 'block';
                        }
                    }, 300);
                } else {
                    alert('Failed to delete.');
                }
            });

            historyList.appendChild(card);
        });

        // Render pagination
        renderPagination(pagination);
    }

    function renderPagination(pg) {
        if (pg.total_pages <= 1) return;

        const prev = document.createElement('button');
        prev.className = 'page-btn';
        prev.innerHTML = '<i class="fas fa-chevron-left"></i>';
        prev.disabled = pg.page <= 1;
        prev.addEventListener('click', () => { currentPage--; loadHistory(); });
        paginationBar.appendChild(prev);

        for (let i = 1; i <= pg.total_pages; i++) {
            if (pg.total_pages > 7 && Math.abs(i - pg.page) > 2 && i !== 1 && i !== pg.total_pages) {
                // Show ellipsis
                if (i === pg.page - 3 || i === pg.page + 3) {
                    const dots = document.createElement('span');
                    dots.textContent = '...';
                    dots.style.padding = '0 6px';
                    dots.style.color = 'var(--gray-400)';
                    paginationBar.appendChild(dots);
                }
                continue;
            }
            const btn = document.createElement('button');
            btn.className = `page-btn ${i === pg.page ? 'active' : ''}`;
            btn.textContent = i;
            btn.addEventListener('click', () => { currentPage = i; loadHistory(); });
            paginationBar.appendChild(btn);
        }

        const next = document.createElement('button');
        next.className = 'page-btn';
        next.innerHTML = '<i class="fas fa-chevron-right"></i>';
        next.disabled = pg.page >= pg.total_pages;
        next.addEventListener('click', () => { currentPage++; loadHistory(); });
        paginationBar.appendChild(next);
    }

    function showModal(item) {
        const typeLabel = typeLabels[item.prediction_type] || item.prediction_type;
        modalTitle.textContent = `${typeLabel} — Details`;

        let html = '';
        const dateStr = item.created_at ? formatDate(item.created_at) : 'N/A';

        html += detailRow('Prediction Type', typeLabel);
        html += detailRow('Date', dateStr);

        const raw = item.raw_output || {};

        if (item.prediction_type === 'crop_recommendation') {
            html += detailRow('Recommended Crop', item.recommended_crop || 'N/A');
            html += detailRow('Confidence', (item.confidence_score ? item.confidence_score.toFixed(1) + '%' : 'N/A'));
            const inp = raw.input || {};
            if (inp.N !== undefined) html += detailRow('N / P / K', `${inp.N} / ${inp.P} / ${inp.K}`);
            const info = raw.info || {};
            if (info.season) html += detailRow('Season', info.season);
            if (info.tips) html += detailRow('Tips', info.tips);
        }
        else if (item.prediction_type === 'disease_detection') {
            html += detailRow('Disease', item.disease_name || 'N/A');
            html += detailRow('Confidence', (item.confidence_score ? item.confidence_score.toFixed(1) + '%' : 'N/A'));
            if (item.remedy) html += detailRow('Remedy', item.remedy);
        }
        else if (item.prediction_type === 'yield_prediction') {
            html += detailRow('Crop', item.crop_name || raw.crop || 'N/A');
            html += detailRow('Predicted Yield', `${item.predicted_yield_kg || 0} kg`);
            if (raw.yield_per_ha) html += detailRow('Yield per Ha', `${raw.yield_per_ha} kg/ha`);
        }
        else if (item.prediction_type === 'fertilizer_recommendation') {
            html += detailRow('Fertilizer', raw.fertilizer || 'N/A');
            html += detailRow('Confidence', (raw.confidence ? raw.confidence + '%' : 'N/A'));
            const info = raw.info || {};
            if (info.quantity_kg_per_acre) html += detailRow('Dosage', `${info.quantity_kg_per_acre} kg/acre`);
            if (info.application_method) html += detailRow('Application', info.application_method);
            if (info.warning) html += detailRow('⚠️ Warning', info.warning);
        }
        
        html += `<div style="margin-top: 1.5rem; text-align: center;">
            <button class="btn btn-primary" onclick="downloadReport('${item.prediction_type}', ${item.id})">
                <i class="fas fa-file-pdf"></i> Download PDF Report
            </button>
        </div>`;

        modalBody.innerHTML = html;
        modal.classList.add('visible');
    }

    function detailRow(label, value) {
        return `<div class="detail-row-modal">
            <span class="detail-label-m">${label}</span>
            <span class="detail-value-m">${value}</span>
        </div>`;
    }

    function formatDate(isoStr) {
        try {
            const d = new Date(isoStr);
            return d.toLocaleDateString('en-IN', {
                day: 'numeric', month: 'short', year: 'numeric',
                hour: '2-digit', minute: '2-digit'
            });
        } catch { return isoStr; }
    }

    function hexToRGBA(hex, alpha) {
        const r = parseInt(hex.slice(1, 3), 16);
        const g = parseInt(hex.slice(3, 5), 16);
        const b = parseInt(hex.slice(5, 7), 16);
        return `rgba(${r},${g},${b},${alpha})`;
    }

    // Initial load
    loadHistory();
});
