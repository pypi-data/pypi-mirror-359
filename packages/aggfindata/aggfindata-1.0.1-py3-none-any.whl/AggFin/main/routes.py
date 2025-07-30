import requests
from flask import Blueprint, render_template, request, jsonify, current_app
import yfinance as yf
import random
from AggFin.config import Config
from flask import jsonify

main = Blueprint('main', __name__)


# Define the custom filter
def format_thousands(value):
    """Format a number with commas as thousands separators."""
    if isinstance(value, (int, float)):
        return f"{value:,}"
    return value

# Register the custom filter with the blueprint
main.add_app_template_filter(format_thousands, 'format_thousands')

# Function to fetch news using NewsAPI
def get_news(stock_name):
    url = f'https://newsapi.org/v2/everything?q={stock_name}&from=2023-05-01&to=2023-08-31&sortBy=popularity&apiKey={Config.NEWS_API_KEY}'
    response = requests.get(url)
    return response.json().get('articles', [])

# Sample data for a larger list of stocks
STOCK_OPTIONS = [
    {"ticker": "AAPL", "description": "Apple Inc. is an American multinational technology company that designs, manufactures, and markets consumer electronics, computer software, and online services."},
    {"ticker": "MSFT", "description": "Microsoft Corporation is an American multinational technology company that develops, licenses, and sells computer software, consumer electronics, personal computers, and related services."},
    {"ticker": "GOOGL", "description": "Alphabet Inc. is the parent company of Google and several other businesses, focusing on internet services and products."},
    {"ticker": "AMZN", "description": "Amazon.com, Inc. is an American multinational technology company that focuses on e-commerce, cloud computing, digital streaming, and artificial intelligence."},
    {"ticker": "TSLA", "description": "Tesla, Inc. is an American electric vehicle and clean energy company that designs, manufactures, and sells electric cars, battery energy storage, and solar energy products."},
    {"ticker": "FB", "description": "Meta Platforms, Inc., formerly Facebook, Inc., is an American technology conglomerate that owns Facebook, Instagram, WhatsApp, and Oculus."},
    {"ticker": "NFLX", "description": "Netflix, Inc. is an American subscription streaming service and production company."},
    {"ticker": "NVDA", "description": "NVIDIA Corporation is an American multinational technology company incorporated in Delaware, known for its graphics processing units (GPUs) for gaming and professional markets."},
    {"ticker": "DIS", "description": "The Walt Disney Company is an American diversified multinational mass media and entertainment conglomerate headquartered in Burbank, California."},
    {"ticker": "PYPL", "description": "PayPal Holdings, Inc. is an American company operating a worldwide online payments system."}
]

# Home route for displaying stock info and news
@main.route("/", methods=['GET', 'POST'])
@main.route("/home", methods=['GET', 'POST'])
def home():
    stock_info = None
    news = None
    bg_color = 'white'  # Default background color
    version = current_app.config['VERSION']

    if request.method == 'POST':
        stock_name = request.form.get('stock_name')
        bg_color = request.form.get('bg_color', 'white')  
        stock_info = yf.Ticker(stock_name).info  
        news = get_news(stock_name)  
        version=version

    # Randomly select 5 stocks from the larger list
    most_visited_stocks = random.sample(STOCK_OPTIONS, 5)

    return render_template('home.html', stock_info=stock_info, news=news, bg_color=bg_color, most_visited_stocks=most_visited_stocks)

@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/api/v1/suggest')
def suggest():
    query = request.args.get('q', '').upper()
    matches = [stock for stock in STOCK_OPTIONS if stock['ticker'].startswith(query)]
    return jsonify(matches[:4])  # limit to 4 suggestions




@main.route('/cause-error')
def cause_error():
     raise Exception("This is a test exception to trigger a 500 error.")
