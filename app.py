import numpy as np
from flask import Flask, request, jsonify, render_template
import pickle
from textblob import TextBlob 
import csv
import subprocess

# Create flask app
flask_app = Flask(__name__)

# Function to analyze sentiments
def analyze_sentiments(reviews):
    positive, negative, neutral = 0, 0, 0
    for review in reviews:
        analysis = TextBlob(review)
        polarity = analysis.sentiment.polarity
        if polarity > 0.1:
            positive += 1
        elif polarity < -0.1:
            negative += 1
        else:
            neutral += 1

    total = len(reviews)
    if total == 0:
        return {"positive": 0, "negative": 0, "neutral": 0}

    return {
        "positive": round((positive / total) * 100, 1),
        "negative": round((negative / total) * 100, 1),
        "neutral": round((neutral / total) * 100, 1)
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


if __name__ == '__main__':
    flask_app.run(debug=True)
