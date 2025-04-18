document.addEventListener('DOMContentLoaded', function() {
    const analyzeBtn = document.getElementById('analyze-btn');
    const productUrlInput = document.getElementById('product-url');
    const loadingDiv = document.getElementById('loading');
    const resultsSection = document.getElementById('results-section');
    const errorMessage = document.getElementById('error-message');
    const modelTabs = document.querySelectorAll('.model-tab');
    let currentModel = 'roberta';
    let chart = null;

    // Model tab switching
    modelTabs.forEach(tab => {
        tab.addEventListener('click', function() {
            modelTabs.forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            currentModel = this.dataset.model;
            updateChart();
        });
    });

    function updateChart() {
        if (chart) {
            chart.destroy();
        }

        const ctx = document.getElementById('sentiment-chart').getContext('2d');
        const data = window.sentimentData[currentModel];
        
        chart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Positive', 'Negative', 'Neutral'],
                datasets: [{
                    data: [data.positive, data.negative, data.neutral],
                    backgroundColor: [
                        '#28c76f', // green
                        '#ea5455', // red
                        '#ff9f43'  // yellow
                    ],
                    borderColor: [
                        '#28c76f', // green
                        '#ea5455', // red
                        '#ff9f43'  // yellow
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });

        // Update percentages
        document.getElementById('positive-percentage').textContent = `${data.positive}%`;
        document.getElementById('negative-percentage').textContent = `${data.negative}%`;
        document.getElementById('neutral-percentage').textContent = `${data.neutral}%`;
    }

    analyzeBtn.addEventListener('click', async function() {
        const productUrl = productUrlInput.value.trim();
        
        if (!productUrl) {
            alert('Please enter a product URL');
            return;
        }

        loadingDiv.classList.remove('hidden');
        resultsSection.classList.add('hidden');
        errorMessage.classList.add('hidden');

        try {
            const response = await fetch('/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ url: productUrl })
            });

            const data = await response.json();

            if (data.success) {
                window.sentimentData = data.sentiment;
                document.getElementById('total-reviews').textContent = data.total_reviews;
                updateChart();
                resultsSection.classList.remove('hidden');
            } else {
                errorMessage.classList.remove('hidden');
            }
        } catch (error) {
            console.error('Error:', error);
            errorMessage.classList.remove('hidden');
        } finally {
            loadingDiv.classList.add('hidden');
        }
    });
});
