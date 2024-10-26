import os
import pandas as pd
import logging
from flask import jsonify, request, abort, Blueprint
from stock_app.api.v2.routes2 import load_all_stock_data

api_v1_bp = Blueprint('api_v1', __name__)

logging.basicConfig(level=logging.INFO)

def authenticate_request():
    """
    Authenticates the API request by checking the API key in the request header.
    Raises:
        401 Unauthorized: If the API key is missing or invalid.
    """
    api_key = request.headers.get('DATA-241-API-KEY')
    expected_api_key = os.environ.get('DATA_241_API_KEY')

    if not api_key or api_key != expected_api_key:
        logging.warning("Unauthorized access attempt.")
        abort(401, description="Unauthorized: Invalid or missing API key.")

@api_v1_bp.route('/api/v1/row_count', methods=['GET'])
def get_row_count():
    """
    Returns the total number of rows in the stock data.
    Returns:
        JSON: { 'row_count': <number_of_rows> }
    """
    authenticate_request()
    row_count = len(stock_data) 
    return jsonify({'row_count': row_count})

@api_v1_bp.route('/api/v1/unique_stock_count', methods=['GET'])
def get_unique_stock_count():
    """
    Returns the count of unique stocks in the stock data.
    Returns:
        JSON: { 'unique_stock_count': <number_of_unique_stocks> }
    """
    authenticate_request()

    if 'stock_symbol' not in stock_data.columns:
        logging.error("'stock_symbol' column missing in the data.")
        return jsonify({'error': 'Missing stock symbol data'}), 400

    unique_stocks = stock_data['stock_symbol'].nunique()
    return jsonify({'unique_stock_count': unique_stocks})

@api_v1_bp.route('/api/v1/row_by_market_count', methods=['GET'])
def get_row_by_market_count():
    """
    Returns the number of rows for each stock market (NASDAQ, NYSE) in the data.
    Returns:
        JSON: { 'NYSE': <count>, 'NASDAQ': <count> }
    """
    authenticate_request()

    if 'market' not in stock_data.columns:
        logging.error("'market' column missing in the data.")
        return jsonify({'error': 'Missing market data'}), 400

    market_counts = stock_data['market'].value_counts().to_dict()
    return jsonify({'NYSE': market_counts.get('NYSE', 0), 'NASDAQ': market_counts.get('NASDAQ', 0)})

try:
    stock_data = load_all_stock_data()
except Exception as e:
    logging.error(f"Failed to load stock data: {e}")
    stock_data = pd.DataFrame()

