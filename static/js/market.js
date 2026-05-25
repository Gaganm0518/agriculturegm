/**
 * Market Prices JS
 * Handles fetching live prices, rendering the table, and plotting prediction charts.
 */

document.addEventListener('DOMContentLoaded', async () => {
    // Only run on market page
    const path = window.location.pathname;
    if (!path.includes('market')) return;

    // Verify Auth
    const user = requireAuth();
    if (!user) return;

    // State
    let trendChartInstance = null;

    // Elements
    const tbody = document.getElementById('prices-tbody');
    const refreshBtn = document.getElementById('refresh-prices');
    const cropSelect = document.getElementById('trend-crop-select');
    const adviceBox = document.getElementById('ai-advice-box');
    const adviceText = document.getElementById('ai-advice-text');

    // Init
    await loadPrices();
    await loadPrediction(cropSelect.value);

    // Event Listeners
    if (refreshBtn) {
        refreshBtn.addEventListener('click', async () => {
            const originalHTML = refreshBtn.innerHTML;
            refreshBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
            refreshBtn.disabled = true;
            
            await loadPrices();
            await loadPrediction(cropSelect.value);
            
            refreshBtn.innerHTML = originalHTML;
            refreshBtn.disabled = false;
        });
    }

    if (cropSelect) {
        cropSelect.addEventListener('change', async (e) => {
            await loadPrediction(e.target.value);
        });
    }

    async function loadPrices() {
        try {
            const res = await apiGet('/market/prices');
            
            if (res && res.success) {
                const prices = res.data;
                tbody.innerHTML = '';
                
                prices.forEach(p => {
                    const diffText = p.difference > 0 ? `+₹${p.difference}` : `-₹${Math.abs(p.difference)}`;
                    const color = p.mandi_price < p.msp ? 'var(--error-red)' : 'var(--success-green)';
                    const icon = p.mandi_price < p.msp ? 'fa-arrow-down' : 'fa-arrow-up';
                    
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td><strong>${p.crop}</strong></td>
                        <td style="font-size: 1.1em; font-weight: bold;">₹${p.mandi_price.toLocaleString()}</td>
                        <td style="color: var(--gray-600);">₹${p.msp.toLocaleString()}</td>
                        <td style="color: ${color}; font-weight: 500;">
                            <i class="fas ${icon}"></i> ${diffText}
                        </td>
                    `;
                    tbody.appendChild(tr);
                });
            } else {
                tbody.innerHTML = `<tr><td colspan="4" style="color: var(--error-red); text-align: center;">Failed to load prices.</td></tr>`;
            }
        } catch (error) {
            console.error("Error loading prices:", error);
            tbody.innerHTML = `<tr><td colspan="4" style="color: var(--error-red); text-align: center;">Network error.</td></tr>`;
        }
    }

    async function loadPrediction(cropName) {
        try {
            const res = await apiGet(`/market/predict/${cropName}`);
            
            if (res && res.success) {
                const data = res.data;
                
                // Show advice
                adviceText.textContent = data.advice;
                adviceBox.style.display = 'block';
                
                // Render Chart
                renderChart(data.crop, data.trend);
            }
        } catch (error) {
            console.error("Error loading predictions:", error);
        }
    }

    function renderChart(cropName, trendData) {
        const ctx = document.getElementById('trendChart').getContext('2d');
        
        const labels = trendData.map(t => t.month);
        const data = trendData.map(t => t.price);
        
        if (trendChartInstance) {
            trendChartInstance.destroy();
        }
        
        trendChartInstance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: `Predicted Price (₹) for ${cropName}`,
                    data: data,
                    borderColor: '#2563eb', // info-blue
                    backgroundColor: 'rgba(37, 99, 235, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#2563eb',
                    pointRadius: 4,
                    pointHoverRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: true, position: 'top' },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return ` ₹${context.parsed.y.toLocaleString()}`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        ticks: {
                            callback: function(value) {
                                return '₹' + value;
                            }
                        }
                    }
                }
            }
        });
    }
});
