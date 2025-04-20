// Initialize chart with sample data when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Sample data for initial chart display
    const sampleData = {
        current_price: 0,
        price_history: [
            { timestamp: new Date(Date.now() - 86400000 * 6).toISOString(), price: 0 },
            { timestamp: new Date(Date.now() - 86400000 * 5).toISOString(), price: 0 },
            { timestamp: new Date(Date.now() - 86400000 * 4).toISOString(), price: 0 },
            { timestamp: new Date(Date.now() - 86400000 * 3).toISOString(), price: 0 },
            { timestamp: new Date(Date.now() - 86400000 * 2).toISOString(), price: 0 },
            { timestamp: new Date(Date.now() - 86400000).toISOString(), price: 0 },
            { timestamp: new Date().toISOString(), price: 0 }
        ]
    };
    
    // Initialize the chart with sample data
    updatePriceTracker(sampleData);
});

function updatePriceTracker(data) {
    if (!data || !data.current_price) {
        console.error('Invalid price data received:', data);
        return;
    }

    // Update current price
    const currentPrice = document.querySelector('.current-price .amount');
    if (currentPrice) {
        currentPrice.textContent = data.current_price.toFixed(2);
    }
    
    // Update last updated time
    const updateTime = document.querySelector('.price-update-time');
    if (updateTime && data.last_updated) {
        const date = new Date(data.last_updated);
        updateTime.textContent = `Last updated: ${date.toLocaleTimeString('en-IN', { 
            hour: '2-digit', 
            minute: '2-digit',
            hour12: true 
        })}`;
    }
    
    // Set current price as default value in target price input
    const targetPriceInput = document.getElementById('targetPrice');
    if (targetPriceInput) {
        targetPriceInput.value = data.current_price.toFixed(2);
        targetPriceInput.min = "0";
        targetPriceInput.step = "0.01";
    }
    
    // Update price change
    const priceChange = document.querySelector('.price-change');
    if (priceChange && data.price_change) {
        const changeClass = data.price_change.is_positive ? 'positive' : 'negative';
        const changeSymbol = data.price_change.is_positive ? '↑' : '↓';
        priceChange.innerHTML = `
            <span class="${changeClass}">
                <span class="icon">${changeSymbol}</span>
                ₹${Math.abs(data.price_change.change).toFixed(2)} (${data.price_change.percentage_change.toFixed(1)}%)
            </span>
        `;
        priceChange.className = `price-change ${changeClass}`;
    }
    
    // Update price history chart
    const ctx = document.getElementById('priceHistoryChart');
    if (!ctx) {
        console.error('Could not find price history chart canvas');
        return;
    }

    // Destroy existing chart if it exists
    if (window.priceChart) {
        window.priceChart.destroy();
    }
    
    if (!data.price_history || !Array.isArray(data.price_history) || data.price_history.length === 0) {
        console.error('No valid price history data');
        return;
    }

    const dates = data.price_history.map(item => {
        const date = new Date(item.timestamp);
        return date.toLocaleDateString('en-IN', { 
            day: 'numeric',
            month: 'short',
            hour: '2-digit',
            minute: '2-digit'
        });
    });
    
    const prices = data.price_history.map(item => item.price);
    
    // Create gradient for chart
    const gradient = ctx.getContext('2d').createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, 'rgba(76, 175, 80, 0.2)');
    gradient.addColorStop(1, 'rgba(76, 175, 80, 0)');
    
    window.priceChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [{
                label: 'Price History (₹)',
                data: prices,
                borderColor: '#4CAF50',
                backgroundColor: gradient,
                fill: true,
                tension: 0.4,
                pointRadius: 4,
                pointBackgroundColor: '#4CAF50',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointHoverRadius: 6,
                pointHoverBackgroundColor: '#4CAF50',
                pointHoverBorderColor: '#fff',
                pointHoverBorderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            layout: {
                padding: {
                    top: 20,
                    right: 20,
                    bottom: 20,
                    left: 20
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `₹${context.parsed.y.toFixed(2)}`;
                        }
                    },
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    borderColor: '#4CAF50',
                    borderWidth: 1,
                    padding: 10,
                    displayColors: false
                },
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    ticks: {
                        callback: function(value) {
                            return '₹' + value.toFixed(2);
                        },
                        color: '#fff',
                        font: {
                            size: 12
                        }
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)',
                        drawBorder: false
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        maxRotation: 45,
                        minRotation: 45,
                        color: '#fff',
                        font: {
                            size: 12
                        }
                    }
                }
            }
        }
    });
}

// Add resize event listener to handle chart resizing
window.addEventListener('resize', function() {
    if (window.priceChart) {
        window.priceChart.resize();
    }
});

document.getElementById('priceAlertForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const targetPrice = document.getElementById('targetPrice').value;
    const email = document.getElementById('email').value;
    
    try {
        const response = await fetch('/price-alert', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ target_price: targetPrice, email: email })
        });
        
        const data = await response.json();
        if (data.success) {
            alert('Price alert set successfully!');
        } else {
            alert('Error setting price alert: ' + data.error);
        }
    } catch (error) {
        alert('Error setting price alert: ' + error.message);
    }
}); 