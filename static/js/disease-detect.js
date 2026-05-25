/**
 * Logic for Disease Detection Page
 * Handles drag & drop, file validation, API submission, and UI updates.
 */

document.addEventListener('DOMContentLoaded', () => {
    // Auth Check
    const user = requireAuth();
    if (user) {
    }

    // Sidebar Toggle
    const menuToggle = document.getElementById('menu-toggle');
    const sidebar = document.getElementById('sidebar');
    if (menuToggle && sidebar) {
        menuToggle.addEventListener('click', () => {
            sidebar.classList.toggle('active');
        });
    }

    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', async () => {
            await logout();
        });
    }

    // DOM Elements
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const previewContainer = document.getElementById('preview-container');
    const imagePreview = document.getElementById('image-preview');
    const fileName = document.getElementById('file-name');
    const removeBtn = document.getElementById('remove-btn');
    const detectBtn = document.getElementById('detect-btn');
    const uploadError = document.getElementById('upload-error');
    const uploadForm = document.getElementById('upload-form');
    
    const uploadSection = document.getElementById('upload-section');
    const resultsSection = document.getElementById('results-section');
    const loadingOverlay = document.getElementById('loading-overlay');

    let selectedFile = null;

    // --- Drag and Drop Logic ---

    // Click to browse
    dropZone.addEventListener('click', () => {
        fileInput.click();
    });

    // Drag over
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    ['dragleave', 'dragend'].forEach(type => {
        dropZone.addEventListener(type, (e) => {
            dropZone.classList.remove('dragover');
        });
    });

    // Drop
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        
        if (e.dataTransfer.files.length) {
            handleFile(e.dataTransfer.files[0]);
        }
    });

    // File input change
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length) {
            handleFile(e.target.files[0]);
        }
    });

    // Handle File Selection
    function handleFile(file) {
        uploadError.style.display = 'none';
        
        // Validate type
        const validTypes = ['image/jpeg', 'image/png', 'image/jpg'];
        if (!validTypes.includes(file.type)) {
            showError('Please upload a valid JPG or PNG image.');
            return;
        }

        // Validate size (max 5MB)
        const maxSize = 5 * 1024 * 1024;
        if (file.size > maxSize) {
            showError('File is too large. Maximum size is 5MB.');
            return;
        }

        selectedFile = file;

        // Show preview
        const reader = new FileReader();
        reader.onload = (e) => {
            imagePreview.src = e.target.result;
            fileName.textContent = `${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)`;
            dropZone.style.display = 'none';
            previewContainer.style.display = 'block';
            detectBtn.disabled = false;
        };
        reader.readAsDataURL(file);
    }

    // Remove Image
    removeBtn.addEventListener('click', () => {
        selectedFile = null;
        fileInput.value = '';
        dropZone.style.display = 'block';
        previewContainer.style.display = 'none';
        detectBtn.disabled = true;
        uploadError.style.display = 'none';
    });

    function showError(msg) {
        uploadError.textContent = msg;
        uploadError.style.display = 'block';
        selectedFile = null;
        fileInput.value = '';
        detectBtn.disabled = true;
    }

    // --- Form Submission Logic ---
    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        if (!selectedFile) return;

        // Show loading
        loadingOverlay.style.display = 'flex';
        uploadError.style.display = 'none';

        const formData = new FormData();
        formData.append('image', selectedFile);

        try {
            const token = typeof getToken === 'function' ? getToken() : localStorage.getItem('agri_token');
            const response = await fetch('/api/detect/disease', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                    // Do NOT set Content-Type here, let the browser set it automatically with boundary for FormData
                },
                body: formData
            });

            const data = await response.json();

            if (response.ok && data.success) {
                displayResults(data.data);
            } else {
                loadingOverlay.style.display = 'none';
                showError(data.error || 'Failed to analyze image. Please try again.');
            }
        } catch (err) {
            console.error(err);
            loadingOverlay.style.display = 'none';
            showError('Server connection error. Please check your network.');
        }
    });

    // --- Results Display Logic ---
    function displayResults(data) {
        // Hide upload, show results
        loadingOverlay.style.display = 'none';
        uploadSection.style.display = 'none';
        resultsSection.style.display = 'block';

        const diseaseNameEl = document.getElementById('disease-name');
        const statusBadge = document.getElementById('status-badge');
        const headerCard = document.getElementById('result-header');

        // Populate Text
        diseaseNameEl.textContent = data.disease;
        document.getElementById('confidence-score').textContent = `${data.confidence}%`;
        document.getElementById('symptoms-text').textContent = data.symptoms || 'No symptom data available.';
        document.getElementById('remedy-text').textContent = data.remedy || 'No treatment data available.';
        document.getElementById('severity-badge').textContent = data.severity || 'Unknown';
        document.getElementById('affected-crops').textContent = data.affected_crops ? data.affected_crops.join(', ') : 'Unknown';
        
        // Image
        if (data.image_url) {
            document.getElementById('result-image').src = data.image_url;
        }

        // Apply dynamic styling based on Healthy vs Disease
        if (data.disease.toLowerCase() === 'healthy') {
            diseaseNameEl.className = 'disease-title text-healthy';
            statusBadge.className = 'status-badge status-healthy';
            statusBadge.innerHTML = '<i class="fas fa-check-circle"></i> Plant is Healthy';
            headerCard.style.borderTop = '4px solid var(--primary-green)';
            document.getElementById('severity-badge').style.color = 'var(--primary-green)';
        } else {
            diseaseNameEl.className = 'disease-title text-disease';
            statusBadge.className = 'status-badge status-disease';
            statusBadge.innerHTML = '<i class="fas fa-exclamation-circle"></i> Disease Detected';
            headerCard.style.borderTop = '4px solid #dc2626';
            document.getElementById('severity-badge').style.color = '#dc2626';
        }

        // Update PDF Download button
        const downloadBtn = document.getElementById('btn-download-report');
        if (downloadBtn && data.prediction_id) {
            downloadBtn.onclick = () => {
                downloadReport('disease_detection', data.prediction_id);
            };
        }
    }

    // Try Another Image
    document.getElementById('try-another-btn').addEventListener('click', () => {
        resultsSection.style.display = 'none';
        uploadSection.style.display = 'block';
        removeBtn.click(); // resets the upload form
        window.scrollTo(0, 0);
    });
});
