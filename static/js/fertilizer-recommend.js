/**
 * Logic for Fertilizer Recommendation Page.
 */

document.addEventListener('DOMContentLoaded', () => {
    // Auth
    const user = requireAuth();
    if (user) {
    }

    // Sidebar toggle
    const menuToggle = document.getElementById('menu-toggle');
    const sidebar = document.getElementById('sidebar');
    if (menuToggle && sidebar) {
        menuToggle.addEventListener('click', () => sidebar.classList.toggle('active'));
    }

    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', async () => { await logout(); });
    }

    // Auto-fill from localStorage if coming from input-form page
    const savedInputData = localStorage.getItem('crop_result_data');
    if (savedInputData) {
        try {
            const parsed = JSON.parse(savedInputData);
            const inp = parsed.input || {};
            if (inp.nitrogen) document.getElementById('nitrogen').value = inp.nitrogen;
            if (inp.phosphorus) document.getElementById('phosphorus').value = inp.phosphorus;
            if (inp.potassium) document.getElementById('potassium').value = inp.potassium;
            if (inp.temperature) document.getElementById('temperature').value = inp.temperature;
            if (inp.humidity) document.getElementById('humidity').value = inp.humidity;
            if (inp.soil_type) {
                const sel = document.getElementById('soil_type');
                for (let opt of sel.options) {
                    if (opt.value === inp.soil_type) { sel.value = inp.soil_type; break; }
                }
            }
        } catch (e) { /* ignore parse errors */ }
    }

    // Form submission
    const form = document.getElementById('fert-form');
    const submitBtn = document.getElementById('submit-btn');
    const formError = document.getElementById('form-error');
    const resultSection = document.getElementById('result-section');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        formError.style.display = 'none';

        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
        submitBtn.disabled = true;

        const payload = {
            nitrogen: parseFloat(document.getElementById('nitrogen').value),
            phosphorus: parseFloat(document.getElementById('phosphorus').value),
            potassium: parseFloat(document.getElementById('potassium').value),
            crop: document.getElementById('crop').value,
            soil_type: document.getElementById('soil_type').value,
            temperature: parseFloat(document.getElementById('temperature').value),
            humidity: parseFloat(document.getElementById('humidity').value),
            moisture: parseFloat(document.getElementById('moisture').value)
        };

        try {
            const response = await apiPost('/recommend/fertilizer', payload);

            if (response && response.success) {
                displayResults(response.data, payload);
            } else {
                formError.textContent = (response && response.error) || 'Recommendation failed.';
                formError.style.display = 'block';
            }
        } catch (err) {
            formError.textContent = 'Network error. Please try again.';
            formError.style.display = 'block';
        } finally {
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }
    });

    function displayResults(data, input) {
        resultSection.style.display = 'block';

        if (window.innerWidth <= 900) {
            resultSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }

        // Hero card
        document.getElementById('fert-name').textContent = data.fertilizer;
        document.getElementById('fert-full-name').textContent = data.full_name || data.fertilizer;
        document.getElementById('fert-confidence').textContent = `${data.confidence}% Match`;
        document.getElementById('fert-qty').textContent = data.quantity_kg_per_acre;

        // Detail cards
        document.getElementById('fert-application').textContent = data.application_method || 'N/A';
        document.getElementById('fert-description').textContent = data.description || 'N/A';
        document.getElementById('fert-cost').textContent = data.cost_estimate || 'Contact local supplier';

        const warningCard = document.getElementById('warning-card');
        const warningText = document.getElementById('fert-warning');
        if (data.warning) {
            warningText.textContent = data.warning;
            warningCard.style.display = 'block';
        } else {
            warningCard.style.display = 'none';
        }

        // NPK bars
        const npk = data.input_npk || { nitrogen: input.nitrogen, phosphorus: input.phosphorus, potassium: input.potassium };
        setNPKBar('npk-n', npk.nitrogen, 140);
        setNPKBar('npk-p', npk.phosphorus, 145);
        setNPKBar('npk-k', npk.potassium, 205);
        
        // Update PDF Download button
        const downloadBtn = document.getElementById('btn-download-report');
        if (downloadBtn && data.prediction_id) {
            downloadBtn.onclick = () => {
                downloadReport('fertilizer_recommendation', data.prediction_id);
            };
        }
    }

    function setNPKBar(prefix, value, maxVal) {
        const pct = Math.min((value / maxVal) * 100, 100);
        document.getElementById(prefix + '-val').textContent = value + ' kg/ha';

        // Animate bar
        setTimeout(() => {
            document.getElementById(prefix + '-bar').style.width = pct + '%';
        }, 100);
    }
});
