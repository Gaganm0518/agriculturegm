/**
 * Weather Insights Logic
 */

requireAuth();

document.addEventListener('DOMContentLoaded', () => {
    const weatherForm = document.getElementById('weather-form');
    const btnDetect = document.getElementById('btn-detect');
    const alertContainer = document.getElementById('alert-container');
    const spinner = document.getElementById('loading-spinner');
    const resultDiv = document.getElementById('weather-result');

    function showAlert(message, type = 'error') {
        if (!alertContainer) return;
        alertContainer.innerHTML = `
            <div class="alert alert-${type}">
                <i class="fas fa-${type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
                <span>${message}</span>
            </div>
        `;
    }

    function showLoading(isLoading) {
        if (isLoading) {
            spinner.style.display = 'block';
            resultDiv.style.display = 'none';
            alertContainer.innerHTML = '';
        } else {
            spinner.style.display = 'none';
        }
    }

    function displayWeather(data) {
        if (!data || data.temperature === undefined) {
            showAlert('Invalid weather data received.');
            return;
        }

        document.getElementById('location-name').textContent = `Weather in ${data.city || 'Unknown Location'}, ${data.country || ''}`;
        document.getElementById('w-temp').textContent = `${data.temperature} °C`;
        document.getElementById('w-humidity').textContent = `${data.humidity} %`;
        document.getElementById('w-rainfall').textContent = `${data.rainfall !== undefined ? data.rainfall : '--'} mm`;
        document.getElementById('w-desc').textContent = data.description || '--';

        resultDiv.style.display = 'block';
        
        if (data.success === false) {
            showAlert(data.message || 'Live API failed. Showing fallback/unavailable data.', 'warning');
        }
    }

    async function fetchWeather(params) {
        showLoading(true);
        try {
            const query = new URLSearchParams(params).toString();
            const response = await apiGet(`/weather/?${query}`);
            
            showLoading(false);
            if (response && response.success === false && !response.data) {
                showAlert(response.error || 'Failed to fetch weather data.');
            } else if (response && response.data) {
                displayWeather(response.data);
            }
        } catch (e) {
            showLoading(false);
            showAlert('Network error or server unavailable.');
        }
    }

    // City Search
    weatherForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const city = document.getElementById('city-input').value.trim();
        if (!city) return;
        fetchWeather({ city });
    });

    // Detect Location
    btnDetect.addEventListener('click', () => {
        if (!navigator.geolocation) {
            showAlert('Geolocation is not supported by your browser.', 'error');
            return;
        }

        const ogText = btnDetect.innerHTML;
        btnDetect.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Detecting...';
        btnDetect.disabled = true;

        navigator.geolocation.getCurrentPosition(
            (position) => {
                btnDetect.innerHTML = ogText;
                btnDetect.disabled = false;
                const lat = position.coords.latitude.toFixed(4);
                const lon = position.coords.longitude.toFixed(4);
                fetchWeather({ lat, lon });
            },
            (error) => {
                btnDetect.innerHTML = ogText;
                btnDetect.disabled = false;
                let msg = 'Location access denied.';
                if (error.code === 2) msg = 'Location unavailable.';
                if (error.code === 3) msg = 'Location request timed out.';
                showAlert(msg + ' Please enter city manually.', 'warning');
            },
            { enableHighAccuracy: false, timeout: 10000, maximumAge: 300000 }
        );
    });
});
