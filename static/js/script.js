document.addEventListener('DOMContentLoaded', function() {
        // Elements
        const productUrlInput = document.getElementById('product-url');
        const analyzeBtn = document.getElementById('analyze-btn');
        const loadingSection = document.getElementById('loading');
        const resultsSection = document.getElementById('results-section');
        const errorMessage = document.getElementById('error-message');
        const positivePercentage = document.getElementById('positive-percentage');
        const negativePercentage = document.getElementById('negative-percentage');
        const neutralPercentage = document.getElementById('neutral-percentage');
        const totalReviews = document.getElementById('total-reviews');
        const scrollTopBtn = document.querySelector('.scroll-top');
        
        // Chart variables
        let sentimentChart = null;
        
        // Event Listeners
        analyzeBtn.addEventListener('click', analyzeReviews);
        scrollTopBtn.addEventListener('click', () => {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
        
        // Functions
        function analyzeReviews() {
            const productUrl = productUrlInput.value.trim();
            
            if (!productUrl) {
                showError('Please enter a valid product URL');
                return;
            }
            
            // Show loading, hide results and errors
            loadingSection.classList.remove('hidden');
            resultsSection.classList.add('hidden');
            errorMessage.classList.add('hidden');
            
            // Send request to backend
            fetch('/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url: productUrl }),
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                if (data.error) {
                    throw new Error(data.error);
                }
                
                displayResults(data);
            })
            .catch(error => {
                showError(error.message);
            })
            .finally(() => {
                loadingSection.classList.add('hidden');
            });
        }
        
        function displayResults(data) {
            // Update percentages
            positivePercentage.textContent = `${data.sentiment.positive}%`;
            negativePercentage.textContent = `${data.sentiment.negative}%`;
            neutralPercentage.textContent = `${data.sentiment.neutral}%`;
            totalReviews.textContent = data.total_reviews;
            
            // Create/update chart
            createSentimentChart(data.sentiment);
            
            // Show results section
            resultsSection.classList.remove('hidden');
        }
        
        function createSentimentChart(sentimentData) {
            const ctx = document.getElementById('sentiment-chart').getContext('2d');
            
            // Destroy previous chart if it exists
            if (sentimentChart) {
                sentimentChart.destroy();
            }
            
            // Create new chart
            sentimentChart = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['Positive', 'Negative', 'Neutral'],
                    datasets: [{
                        data: [
                            sentimentData.positive,
                            sentimentData.negative,
                            sentimentData.neutral
                        ],
                        backgroundColor: [
                            '#28c76f', // Green for positive
                            '#ea5455', // Red for negative
                            '#ff9f43'  // Yellow for neutral
                        ],
                        borderWidth: 0,
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                color: '#f5f5f5',
                                padding: 20
                            }
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return `${context.label}: ${context.raw}%`;
                                }
                            }
                        }
                    },
                    cutout: '70%'
                }
            });
        }
        
        function showError(message) {
            errorMessage.querySelector('p').textContent = message || 'Error analyzing reviews. Please check the URL and try again.';
            errorMessage.classList.remove('hidden');
            loadingSection.classList.add('hidden');
            resultsSection.classList.add('hidden');
        }
    });