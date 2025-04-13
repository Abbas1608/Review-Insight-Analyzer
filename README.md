# Review Insight - Product Reviews Analyzer

A web application that analyzes product reviews from Amazon URLs, performing sentiment analysis to categorize reviews as positive, negative, or neutral.

## Features

- Clean, modern dark UI matching the provided design
- Input field for Amazon product URLs
- Sentiment analysis of product reviews
- Visual presentation of results with charts and percentages
- Responsive design for all devices

## Installation

1. Clone this repository
2. Create a virtual environment:
   ```
   python -m venv venv
   ```
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`
4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Run the Flask application:
   ```
   python app.py
   ```
2. Open your browser and go to `http://127.0.0.1:5000`
3. Paste an Amazon product URL and click "Analyze"
4. View the sentiment analysis results

## Project Structure

- `app.py` - Flask backend
- `templates/index.html` - Main HTML page
- `static/css/styles.css` - CSS styling
- `static/js/script.js` - Frontend JavaScript

## Notes

- This is a demonstration version that uses simulated data
- For production use, you would need to implement actual web scraping and sentiment analysis
- Be aware of Amazon's terms of service regarding web scraping

## Requirements

- Python 3.7+
- Flask
- Requests
- BeautifulSoup4
- Chart.js (included via CDN)