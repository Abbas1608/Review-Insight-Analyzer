from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
import re
import random
import time

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_reviews():
    data = request.json
    product_url = data.get('url')
    
    # Validate URL (basic validation)
    if not product_url or not product_url.startswith('http'):
        return jsonify({'error': 'Invalid URL provided'}), 400
    
    try:
        # For demo purposes, we're simulating the scraping and analysis
        # In a real implementation, you would:
        # 1. Fetch the page content using requests
        # 2. Parse the HTML with BeautifulSoup
        # 3. Extract reviews
        # 4. Perform sentiment analysis
        
        # Simulated processing time
        time.sleep(2)
        
        # Generate random sentiment analysis results for demo
        positive = round(random.uniform(30, 80), 1)
        negative = round(random.uniform(5, 30), 1)
        neutral = round(100 - positive - negative, 1)
        
        # In a real implementation, replace with actual sentiment analysis
        
        return jsonify({
            'success': True,
            'product_url': product_url,
            'sentiment': {
                'positive': positive,
                'negative': negative,
                'neutral': neutral
            },
            'total_reviews': random.randint(50, 500)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)