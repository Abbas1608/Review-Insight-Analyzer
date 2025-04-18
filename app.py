import numpy as np
from flask import Flask, request, jsonify, render_template
import pickle
import csv
import subprocess
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import torch

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


if __name__ == '__main__':
    flask_app.run(debug=True)
