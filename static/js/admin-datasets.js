/**
 * Admin Datasets & Models JS
 */

document.addEventListener('DOMContentLoaded', async () => {
    // 1. Verify Admin Auth
    const path = window.location.pathname;
    if (!path.includes('admin-datasets')) return; // Only run on admin datasets page

    const user = requireAuth();
    if (!user) return;
    if (user.role !== 'admin') {
        window.location.href = '/dashboard.html';
        return;
    }

    document.getElementById('admin-content').style.display = 'block';

    // Sidebar & Logout
    document.getElementById('menu-toggle')?.addEventListener('click', () => {
        document.getElementById('sidebar').classList.toggle('active');
    });
    document.getElementById('logout-btn')?.addEventListener('click', async () => {
        await logout();
    });

    // 2. Load Datasets
    window.loadDatasets = loadDatasets; // expose globally for the refresh button
    async function loadDatasets() {
        const grid = document.getElementById('dataset-grid');
        grid.innerHTML = '<p>Loading...</p>';

        try {
            const res = await apiGet('/admin/datasets');
            if (res && res.success) {
                const datasets = res.data || [];
                if (datasets.length === 0) {
                    grid.innerHTML = '<p style="color: var(--gray-500);">No CSV datasets found in /datasets/ folder.</p>';
                    return;
                }

                grid.innerHTML = '';
                datasets.forEach(ds => {
                    const sizeMB = (ds.size_bytes / (1024 * 1024)).toFixed(2);
                    const dateStr = new Date(ds.last_updated).toLocaleDateString();
                    
                    const card = document.createElement('div');
                    card.className = 'dataset-card';
                    card.innerHTML = `
                        <h4><i class="fas fa-file-csv" style="color: var(--primary-green);"></i> ${ds.name}</h4>
                        <div class="meta"><i class="fas fa-database"></i> ${ds.rows.toLocaleString()} rows</div>
                        <div class="meta"><i class="fas fa-hdd"></i> ${sizeMB} MB</div>
                        <div class="meta"><i class="fas fa-clock"></i> Updated: ${dateStr}</div>
                    `;
                    grid.appendChild(card);
                });
            } else {
                grid.innerHTML = `<p style="color: red;">Failed to load datasets: ${res?.error || 'Unknown error'}</p>`;
            }
        } catch (err) {
            grid.innerHTML = '<p style="color: red;">Network error loading datasets.</p>';
        }
    }

    await loadDatasets();

    // 3. Upload Dataset
    document.getElementById('upload-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const fileInput = document.getElementById('dataset-file');
        const statusDiv = document.getElementById('upload-status');
        
        if (!fileInput.files || fileInput.files.length === 0) return;

        const file = fileInput.files[0];
        const formData = new FormData();
        formData.append('file', file);

        const btn = document.getElementById('upload-btn');
        const originalText = btn.innerHTML;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Uploading...';
        btn.disabled = true;
        statusDiv.style.color = 'var(--gray-600)';
        statusDiv.textContent = 'Uploading...';

        try {
            const token = getToken();
            const response = await fetch(`${API_BASE_URL}/admin/datasets/upload`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` },
                body: formData
            });
            const data = await response.json();

            if (data.success) {
                statusDiv.style.color = 'green';
                statusDiv.textContent = 'Upload successful!';
                fileInput.value = '';
                await loadDatasets(); // refresh list
            } else {
                statusDiv.style.color = 'red';
                statusDiv.textContent = data.error || 'Upload failed.';
            }
        } catch (err) {
            statusDiv.style.color = 'red';
            statusDiv.textContent = 'Network error during upload.';
        } finally {
            btn.innerHTML = originalText;
            btn.disabled = false;
            setTimeout(() => { statusDiv.textContent = ''; }, 5000);
        }
    });

    // 4. Retraining Logic
    const activeJobs = {};

    window.triggerRetrain = async function(modelType) {
        if (!confirm(`Are you sure you want to retrain the ${modelType} model? This may take several minutes and will consume server resources.`)) {
            return;
        }

        try {
            const res = await apiPost(`/admin/retrain/${modelType}`, {});
            if (res && res.success) {
                const jobId = res.data.job_id;
                startPolling(modelType, jobId);
            } else {
                alert(`Failed to start training: ${res?.error}`);
            }
        } catch (err) {
            alert('Network error trying to start training.');
        }
    };

    function startPolling(modelType, jobId) {
        // Show progress UI
        const progContainer = document.getElementById(`prog-${modelType}`);
        const statusText = document.getElementById(`status-text-${modelType}`);
        const logWindow = document.getElementById(`log-${modelType}`);
        const barFill = document.getElementById(`bar-${modelType}`);
        
        progContainer.style.display = 'block';
        statusText.textContent = 'Starting job...';
        logWindow.textContent = 'Initializing background process...';
        barFill.style.width = '10%';
        barFill.style.animation = 'pulse 1.5s infinite';

        activeJobs[modelType] = setInterval(async () => {
            try {
                const res = await apiGet(`/admin/retrain/status/${jobId}`);
                if (res && res.success) {
                    const job = res.data;
                    
                    // Update logs
                    if (job.log_tail && job.log_tail.length > 0) {
                        logWindow.textContent = job.log_tail.join('');
                        logWindow.scrollTop = logWindow.scrollHeight;
                    }

                    if (job.status === 'completed') {
                        clearInterval(activeJobs[modelType]);
                        statusText.textContent = 'Training Completed';
                        barFill.style.width = '100%';
                        barFill.style.animation = 'none';
                        barFill.style.background = '#16a34a'; // green
                        
                        if (job.accuracy && job.accuracy !== 'N/A') {
                            document.getElementById(`acc-${modelType}`).textContent = job.accuracy;
                        }
                        document.getElementById(`trained-${modelType}`).textContent = new Date().toLocaleDateString();
                    } 
                    else if (job.status === 'failed') {
                        clearInterval(activeJobs[modelType]);
                        statusText.textContent = 'Training Failed';
                        statusText.style.color = '#dc2626';
                        barFill.style.animation = 'none';
                        barFill.style.background = '#dc2626';
                        logWindow.textContent += `\n\nERROR: ${job.error}`;
                        logWindow.scrollTop = logWindow.scrollHeight;
                    }
                    else if (job.status === 'running') {
                        statusText.textContent = 'Training in progress...';
                        barFill.style.width = '60%';
                    }
                }
            } catch (err) {
                console.error("Polling error", err);
            }
        }, 3000); // poll every 3 seconds
    }
});
