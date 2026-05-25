/**
 * Logic for the Crop Recommendation Results page.
 * Loads data from localStorage and populates the UI.
 */
document.addEventListener('DOMContentLoaded', async () => {
    // Check auth
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

    // Logout logic
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', async () => {
            await logout();
        });
    }

    // Load Result Data
    const storedData = localStorage.getItem('crop_result_data');
    if (!storedData) {
        document.getElementById('error-content').style.display = 'block';
        return;
    }

    try {
        const { input, result } = JSON.parse(storedData);
        
        // Populate Header
        document.getElementById('display-crop-name').innerHTML = `<i class="fas fa-seedling"></i> ${result.crop}`;
        document.getElementById('display-confidence').textContent = `${result.confidence}%`;
        
        // Animate Ring
        const ring = document.getElementById('confidence-ring');
        if (ring) {
            // Circumference is 408.4. Offset goes from 408.4 down to representing the percentage
            const circumference = 408.4;
            const offset = circumference - (result.confidence / 100) * circumference;
            // Delay slightly to ensure CSS transition fires
            setTimeout(() => {
                ring.style.strokeDashoffset = offset;
            }, 100);
        }

        // Populate Info Card
        if (result.info) {
            document.getElementById('display-season').textContent = result.info.season || 'N/A';
            document.getElementById('display-water').textContent = result.info.water_needs || 'N/A';
            document.getElementById('display-tips').textContent = result.info.growing_tips || 'No tips available.';
        }

        // Populate Input Summary
        document.getElementById('param-n').textContent = `${input.nitrogen} kg/ha`;
        document.getElementById('param-p').textContent = `${input.phosphorus} kg/ha`;
        document.getElementById('param-k').textContent = `${input.potassium} kg/ha`;
        document.getElementById('param-temp').textContent = `${input.temperature} °C`;
        document.getElementById('param-hum').textContent = `${input.humidity} %`;
        document.getElementById('param-rain').textContent = `${input.rainfall} mm`;
        document.getElementById('param-ph').textContent = input.ph || 'N/A';

        // Show Content
        document.getElementById('result-content').style.display = 'block';

        // Clear local storage so hitting refresh without new data shows error
        // Optional: comment this out if you want them to be able to refresh the result page
        // localStorage.removeItem('crop_result_data');

        // Download Report button
        const downloadBtn = document.getElementById('btn-download-report');
        if (downloadBtn && result.prediction_id) {
            downloadBtn.addEventListener('click', () => {
                downloadReport('crop_recommendation', result.prediction_id);
            });
        }

    } catch (e) {
        console.error("Error parsing result data:", e);
        document.getElementById('error-content').style.display = 'block';
    }
});
