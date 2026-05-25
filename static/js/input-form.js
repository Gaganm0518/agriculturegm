/**
 * Input Form Logic
 * Handles data entry, validation, fetching live weather mock data, and submitting to /api/analyze.
 */

requireAuth();

document.addEventListener('DOMContentLoaded', async () => {
    // --- Layout setup ---
    const menuToggle = document.getElementById('menu-toggle');
    const sidebar = document.getElementById('sidebar');
    
    if (menuToggle && sidebar) {
        menuToggle.addEventListener('click', () => {
            sidebar.classList.toggle('open');
        });
    }

    // Load user profile
    const userRes = await apiGet('/auth/me');
    if (userRes && userRes.success) {
        const user = userRes.data.user;
    }

    // Logout handler
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', async () => {
            await apiPost('/auth/logout');
            removeToken();
            window.location.href = '/login.html';
        });
    }

    // --- Form Logic ---
    const form = document.getElementById('analysis-form');
    const alertContainer = document.getElementById('alert-container');
    const liveWeatherBtn = document.getElementById('btn-live-weather');

    function showError(inputId, message) {
        const input = document.getElementById(inputId);
        const errorDiv = document.getElementById(`${inputId}-error`);
        if (input) input.classList.add('error');
        if (errorDiv) errorDiv.textContent = message;
    }

    function clearErrors() {
        document.querySelectorAll('.form-input').forEach(input => input.classList.remove('error'));
        document.querySelectorAll('.form-error').forEach(div => div.textContent = '');
        if (alertContainer) alertContainer.innerHTML = '';
    }

    function showAlert(message, type = 'error') {
        if (!alertContainer) return;
        alertContainer.innerHTML = `
            <div class="alert alert-${type}">
                <i class="fas fa-${type === 'error' ? 'exclamation-circle' : 'check-circle'}"></i>
                <span>${message}</span>
            </div>
        `;
    }

    function setLoading(isLoading) {
        const btnText = document.getElementById('btn-text');
        const btnSpinner = document.getElementById('btn-spinner');
        const submitBtn = document.getElementById('submit-btn');
        
        if (!submitBtn) return;
        
        if (isLoading) {
            submitBtn.disabled = true;
            if (btnText) btnText.style.display = 'none';
            if (btnSpinner) btnSpinner.style.display = 'block';
        } else {
            submitBtn.disabled = false;
            if (btnText) btnText.style.display = 'block';
            if (btnSpinner) btnSpinner.style.display = 'none';
        }
    }

    // Live Weather — Real Geolocation + Backend API
    if (liveWeatherBtn) {
        liveWeatherBtn.addEventListener('click', () => {
            if (!navigator.geolocation) {
                showAlert('Geolocation is not supported by your browser.', 'error');
                return;
            }

            liveWeatherBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Detecting location...';
            liveWeatherBtn.disabled = true;

            navigator.geolocation.getCurrentPosition(
                async (position) => {
                    const lat = position.coords.latitude.toFixed(4);
                    const lon = position.coords.longitude.toFixed(4);

                    liveWeatherBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Fetching weather...';

                    try {
                        const res = await apiGet(`/weather?lat=${lat}&lon=${lon}`);

                        if (res && res.success && res.data && res.data.success) {
                            const w = res.data;
                            document.getElementById('temperature').value = w.temperature;
                            document.getElementById('humidity').value = w.humidity;
                            document.getElementById('rainfall').value = w.rainfall;

                            // Show weather info banner
                            const banner = document.getElementById('weather-info-banner');
                            if (banner) {
                                document.getElementById('weather-icon').src = w.icon || '';
                                document.getElementById('weather-city-label').textContent = `${w.city}, ${w.country}`;
                                document.getElementById('weather-desc-label').textContent = ` — ${w.description}, ${w.temperature}°C, Wind ${w.wind_speed} m/s`;
                                banner.style.display = 'flex';
                            }

                            liveWeatherBtn.innerHTML = `<i class="fas fa-check"></i> ${w.city} — ${w.description}`;
                            liveWeatherBtn.style.background = 'var(--success-light)';
                            liveWeatherBtn.style.color = 'var(--success-green)';
                            liveWeatherBtn.style.borderColor = 'var(--success-green)';
                        } else {
                            const msg = (res && res.data && res.data.message) || 'Could not fetch weather.';
                            showAlert(msg, 'warning');
                            liveWeatherBtn.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Retry';
                        }
                    } catch (err) {
                        showAlert('Failed to connect to weather service.', 'error');
                        liveWeatherBtn.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Retry';
                    }

                    setTimeout(() => {
                        liveWeatherBtn.innerHTML = '<i class="fas fa-location-dot"></i> Detect My Location';
                        liveWeatherBtn.style.background = '';
                        liveWeatherBtn.style.color = '';
                        liveWeatherBtn.style.borderColor = '';
                        liveWeatherBtn.disabled = false;
                    }, 4000);
                },
                (error) => {
                    let msg = 'Location access denied.';
                    if (error.code === 2) msg = 'Location unavailable.';
                    if (error.code === 3) msg = 'Location request timed out.';
                    showAlert(msg + ' Please enter weather data manually.', 'warning');
                    liveWeatherBtn.innerHTML = '<i class="fas fa-location-dot"></i> Detect My Location';
                    liveWeatherBtn.disabled = false;
                },
                { enableHighAccuracy: false, timeout: 10000, maximumAge: 300000 }
            );
        });
    }

    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            clearErrors();
            
            let isValid = true;
            const data = {
                temperature: parseFloat(document.getElementById('temperature').value),
                humidity: parseFloat(document.getElementById('humidity').value),
                rainfall: parseFloat(document.getElementById('rainfall').value),
                soil_type: document.getElementById('soil_type').value,
                nitrogen: parseFloat(document.getElementById('nitrogen').value),
                phosphorus: parseFloat(document.getElementById('phosphorus').value),
                potassium: parseFloat(document.getElementById('potassium').value),
                ph: parseFloat(document.getElementById('ph').value),
                actions: Array.from(document.querySelectorAll('input[name="actions"]:checked')).map(cb => cb.value)
            };

            // Validations
            if (isNaN(data.temperature) || data.temperature < 0 || data.temperature > 60) {
                showError('temperature', 'Enter a valid temperature between 0 and 60 °C');
                isValid = false;
            }
            if (isNaN(data.humidity) || data.humidity < 0 || data.humidity > 100) {
                showError('humidity', 'Enter a valid humidity between 0 and 100 %');
                isValid = false;
            }
            if (isNaN(data.rainfall) || data.rainfall < 0 || data.rainfall > 500) {
                showError('rainfall', 'Enter a valid rainfall between 0 and 500 mm');
                isValid = false;
            }
            if (!data.soil_type) {
                showError('soil_type', 'Please select a soil type');
                isValid = false;
            }
            if (isNaN(data.nitrogen) || data.nitrogen < 0) {
                showError('nitrogen', 'Enter a valid positive number');
                isValid = false;
            }
            if (isNaN(data.phosphorus) || data.phosphorus < 0) {
                showError('phosphorus', 'Enter a valid positive number');
                isValid = false;
            }
            if (isNaN(data.potassium) || data.potassium < 0) {
                showError('potassium', 'Enter a valid positive number');
                isValid = false;
            }
            if (isNaN(data.ph) || data.ph < 0 || data.ph > 14) {
                showError('ph', 'Enter a valid pH between 0 and 14');
                isValid = false;
            }
            

            if (!isValid) return;

            setLoading(true);

            // POST to backend ML API
            try {
                const response = await apiPost('/recommend/crop', data);
                
                if (response && response.success) {
                    // Store inputs and result locally for the result page to display
                    const resultData = {
                        input: data,
                        result: response.data
                    };
                    localStorage.setItem('crop_result_data', JSON.stringify(resultData));
                    window.location.href = '/crop-result.html';
                } else {
                    showAlert(response ? response.error : 'Failed to get recommendation.', 'error');
                }

            } catch (err) {
                showAlert('Failed to connect to the ML API server.', 'error');
            }

            setLoading(false);
        });
    }
});
