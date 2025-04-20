import numpy as np
from flask import Flask, request, jsonify, render_template
import pickle
import csv
import subprocess
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import torch
import json
from datetime import datetime
from price_tracker import get_product_price, get_price_history, get_price_change

# Create flask app
flask_app = Flask(__name__)

# Initialize RoBERTa model and tokenizer
tokenizer = AutoTokenizer.from_pretrained("cardiffnlp/twitter-roberta-base-sentiment")
model = AutoModelForSequenceClassification.from_pretrained("cardiffnlp/twitter-roberta-base-sentiment")

# Initialize VADER analyzer
vader_analyzer = SentimentIntensityAnalyzer()

def analyze_sentiments(reviews):
    # Initialize counters for both models
    roberta_sentiments = {"positive": 0, "negative": 0, "neutral": 0}
    vader_sentiments = {"positive": 0, "negative": 0, "neutral": 0}
    
    for review in reviews:
        # RoBERTa analysis
        inputs = tokenizer(review, return_tensors="pt", truncation=True, max_length=512)
        with torch.no_grad():
            outputs = model(**inputs)
            scores = torch.nn.functional.softmax(outputs.logits, dim=1)
            roberta_sentiment = torch.argmax(scores).item()
            
            if roberta_sentiment == 2:  # Positive
                roberta_sentiments["positive"] += 1
            elif roberta_sentiment == 0:  # Negative
                roberta_sentiments["negative"] += 1
            else:  # Neutral
                roberta_sentiments["neutral"] += 1
        
        # VADER analysis
        vader_scores = vader_analyzer.polarity_scores(review)
        compound_score = vader_scores['compound']
        
        if compound_score >= 0.05:
            vader_sentiments["positive"] += 1
        elif compound_score <= -0.05:
            vader_sentiments["negative"] += 1
        else:
            vader_sentiments["neutral"] += 1

    total = len(reviews)
    if total == 0:
        return {
            "roberta": {"positive": 0, "negative": 0, "neutral": 0},
            "vader": {"positive": 0, "negative": 0, "neutral": 0}
        }

    # Calculate percentages for both models
    roberta_results = {
        "positive": round((roberta_sentiments["positive"] / total) * 100, 1),
        "negative": round((roberta_sentiments["negative"] / total) * 100, 1),
        "neutral": round((roberta_sentiments["neutral"] / total) * 100, 1)
    }
    
    vader_results = {
        "positive": round((vader_sentiments["positive"] / total) * 100, 1),
        "negative": round((vader_sentiments["negative"] / total) * 100, 1),
        "neutral": round((vader_sentiments["neutral"] / total) * 100, 1)
    }

    return {
        "roberta": roberta_results,
        "vader": vader_results
    }
    
@flask_app.route("/")
def Home():
    return render_template("index.html")

@flask_app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    product_url = data.get('url')

    if not product_url or not product_url.startswith('http'):
        return jsonify({'error': 'Invalid URL provided'}), 400

    try:
        subprocess.run(['python', 'scrape_reviews.py', product_url], check=True)

        # Read the newly scraped reviews
        reviews = []
        with open("amazon_reviews.csv", "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader)  # Skip header
            for row in reader:
                reviews.append(row[1])

        sentiment_result = analyze_sentiments(reviews)

        return jsonify({
            'success': True,
            'product_url': product_url,
            'sentiment': sentiment_result,
            'total_reviews': len(reviews)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@flask_app.route('/track-price', methods=['POST'])
def track_price():
    data = request.json
    product_url = data.get('url')
    
    if not product_url:
        return jsonify({'error': 'URL is required'}), 400
        
    try:
        current_price = get_product_price(product_url)
        if current_price is None:
            return jsonify({'error': 'Could not fetch price'}), 400
            
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Initialize price history
        price_history = []
        
        # Try to load existing price history
        try:
            with open('price_history.json', 'r') as f:
                price_history = json.load(f)
                if not isinstance(price_history, list):
                    price_history = []
        except (FileNotFoundError, json.JSONDecodeError):
            price_history = []
        
        # Add new price entry
        new_entry = {
            'timestamp': timestamp,
            'price': current_price
        }
        price_history.append(new_entry)
        
        # Save updated price history
        with open('price_history.json', 'w') as f:
            json.dump(price_history, f, indent=4)
        
        # Calculate price change
        price_change = None
        if len(price_history) >= 2:
            previous_price = price_history[-2]['price']
            change = current_price - previous_price
            percentage_change = (change / previous_price) * 100
            price_change = {
                'change': change,
                'percentage_change': percentage_change,
                'is_positive': change > 0
            }
        
        return jsonify({
            'success': True,
            'current_price': current_price,
            'price_history': price_history,
            'price_change': price_change,
            'last_updated': timestamp
        })
        
    except Exception as e:
        print(f"Error tracking price: {e}")
        return jsonify({'error': str(e)}), 500

@flask_app.route('/price-alert', methods=['POST'])
def set_price_alert():
    data = request.json
    target_price = data.get('target_price')
    email = data.get('email')
    
    if not target_price or not email:
        return jsonify({'error': 'Target price and email are required'}), 400
        
    # Store alert in database or file
    try:
        with open('price_alerts.json', 'r') as f:
            alerts = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        alerts = []
        
    alerts.append({
        'target_price': float(target_price),
        'email': email,
        'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    
    with open('price_alerts.json', 'w') as f:
        json.dump(alerts, f, indent=4)
        
    return jsonify({'success': True, 'message': 'Price alert set successfully'})

if __name__ == '__main__':
    flask_app.run(debug=True)
