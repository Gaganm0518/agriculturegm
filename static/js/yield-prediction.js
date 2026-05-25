/**
 * Logic for Yield Prediction Page
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

    const yieldForm = document.getElementById('yield-form');
    const submitBtn = document.getElementById('submit-btn');
    const formError = document.getElementById('form-error');
    const resultCard = document.getElementById('result-card');
    const geoBtn = document.getElementById('geo-btn');

    // Auto-fill rainfall using geolocation/weather API (mock calculation for demo)
    if (geoBtn) {
        geoBtn.addEventListener('click', async () => {
            const btn = geoBtn;
            const originalText = btn.innerHTML;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Locating...';
            btn.disabled = true;

            if ("geolocation" in navigator) {
                navigator.geolocation.getCurrentPosition(async (position) => {
                    // For the sake of the demo, we will generate a realistic rainfall amount
                    // based on a successful location ping.
                    setTimeout(() => {
                        const rainfallInput = document.getElementById('rainfall');
                        // Average monsoonal rainfall 800 - 1500mm
                        const estRainfall = Math.floor(Math.random() * (1500 - 800 + 1)) + 800;
                        rainfallInput.value = estRainfall;
                        
                        btn.innerHTML = '<i class="fas fa-check"></i> Rainfall Filled';
                        btn.style.background = '#86efac'; // success green
                        
                        setTimeout(() => {
                            btn.innerHTML = originalText;
                            btn.style.background = '';
                            btn.disabled = false;
                        }, 3000);
                    }, 800);
                }, (error) => {
                    alert("Location access denied or unavailable. Please enter rainfall manually.");
                    btn.innerHTML = originalText;
                    btn.disabled = false;
                });
            } else {
                alert("Geolocation is not supported by your browser");
                btn.innerHTML = originalText;
                btn.disabled = false;
            }
        });
    }

    // Handle Form Submission
    yieldForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        formError.style.display = 'none';
        
        const originalBtnText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Calculating...';
        submitBtn.disabled = true;

        const payload = {
            crop: document.getElementById('crop').value,
            season: document.getElementById('season').value,
            region: document.getElementById('region').value,
            area_ha: document.getElementById('area_ha').value,
            rainfall: document.getElementById('rainfall').value,
            fertilizer_kg: document.getElementById('fertilizer_kg').value,
            pesticide_kg: document.getElementById('pesticide_kg').value
        };

        try {
            const response = await apiPost('/predict/yield', payload);

            if (response.success) {
                displayResults(response.data);
            } else {
                formError.textContent = response.error || 'Prediction failed.';
                formError.style.display = 'block';
            }
        } catch (err) {
            formError.textContent = 'A network error occurred. Please try again.';
            formError.style.display = 'block';
        } finally {
            submitBtn.innerHTML = originalBtnText;
            submitBtn.disabled = false;
        }
    });

    // Display Results with Animation
    function displayResults(data) {
        resultCard.style.display = 'block';
        
        // Scroll to results on mobile
        if (window.innerWidth <= 900) {
            resultCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }

        const totalYield = data.total_yield_kg;
        const yieldPerHa = data.yield_per_ha;
        const tonnes = (totalYield / 1000).toFixed(2);
        
        // Reset counters
        document.getElementById('yield-total').textContent = '0';
        document.getElementById('yield-tonnes').textContent = '0';
        document.getElementById('yield-bar').style.width = '0%';
        
        // Setup text
        document.getElementById('yield-per-ha').textContent = `${yieldPerHa.toLocaleString()} kg/ha`;
        
        // Meaning text logic based on arbitrary logic for the UI demonstration
        const meaningText = document.getElementById('meaning-text');
        if (yieldPerHa > 4000) {
            meaningText.innerHTML = `<strong>Excellent Forecast:</strong> Your projected yield of ${yieldPerHa.toLocaleString()} kg per hectare for ${data.crop} is well above average. Ensure your storage and transport logistics are prepared for a bumper harvest!`;
        } else if (yieldPerHa > 2000) {
            meaningText.innerHTML = `<strong>Solid Forecast:</strong> Your projected yield of ${yieldPerHa.toLocaleString()} kg per hectare is on track with typical seasonal averages. Maintain your current irrigation and monitoring schedule.`;
        } else {
            meaningText.innerHTML = `<strong>Attention Needed:</strong> Your projected yield of ${yieldPerHa.toLocaleString()} kg per hectare is slightly below optimum. Consider reviewing your fertilizer application or checking for early disease signs to boost output.`;
        }

        // Animate total yield counter
        animateValue("yield-total", 0, totalYield, 1500);
        
        // Set tonnes instantly
        setTimeout(() => {
            document.getElementById('yield-tonnes').textContent = tonnes;
            
            // Animate bar width (cap at 100%, assuming 6000kg/ha is max scale)
            const percentage = Math.min((yieldPerHa / 6000) * 100, 100);
            document.getElementById('yield-bar').style.width = `${percentage}%`;
        }, 500);

        // Update PDF Download button
        const downloadBtn = document.getElementById('btn-download-report');
        if (downloadBtn && data.prediction_id) {
            downloadBtn.onclick = () => {
                downloadReport('yield_prediction', data.prediction_id);
            };
        }
    }

    // Number counting animation utility
    function animateValue(id, start, end, duration) {
        if (start === end) return;
        var range = end - start;
        var current = start;
        var increment = end > start ? 
            Math.max(1, Math.floor(range / (duration / 16))) : 
            -Math.max(1, Math.floor(Math.abs(range) / (duration / 16)));
        var stepTime = Math.abs(Math.floor(duration / (range / increment)));
        var obj = document.getElementById(id);
        
        var timer = setInterval(function() {
            current += increment;
            if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
                current = end;
                clearInterval(timer);
            }
            // Format with commas
            obj.innerHTML = current.toLocaleString();
        }, stepTime);
    }
});
