"""Flask Routes"""

import logging
import pandas as pd
from flask import jsonify
from stock_app.api.data_utils.loading_utils import load_stock_data
from stock_app.api.route_utils.decorators import authenticate_request

# Configure logging
logging.basicConfig(level=logging.INFO)

# Load stock data
try:
    stock_data = load_stock_data()
    # Ensure columns are consistently lowercase
    stock_data.columns = stock_data.columns.str.lower()
except Exception as e:
    logging.error(f"Failed to load stock data: {e}")

def get_prices(symbol, price_type):
    """Helper function to get price information for a specific stock symbol.

    Args:
        symbol (str): Stock symbol to lookup.
        price_type (str): Type of price ('open', 'close', 'high', 'low').

    Returns:
        JSON: { 'symbol': <symbol>, 'price_info': <list_of_prices> }
              or JSON: {'error': 'Symbol not found in the data'}
    """
    symbol = symbol.upper()  # Ensure consistent symbol format
    if symbol not in stock_data["symbol"].unique():
        return jsonify({"error": "Symbol not found in the data"}), 404

    symbol_df = stock_data[stock_data["symbol"] == symbol].copy()
    symbol_df["date"] = pd.to_datetime(
        symbol_df["date"], format="%d-%b-%Y"
    ).dt.strftime("%Y-%b-%d")
    price_info = symbol_df[["date", price_type.lower()]].to_dict(orient="records")
    return jsonify({"symbol": symbol, "price_info": price_info})

def register_routes2(app):
    """Registers Part 2 Routes"""

    @app.route("/api/v2/<price_type>/<symbol>", methods=["GET"])
    @authenticate_request
    def price_endpoint(price_type, symbol):
        """Returns prices for a specific stock symbol and price type

        Returns:
            JSON: { 'symbol': <symbol>, 'price_info': <list_of_prices> }
            or JSON: {'error': 'Symbol not found in the data'}
        """
        price_type = price_type.lower()
        return get_prices(symbol, price_type)

    @app.route("/api/v2/<year>", methods=["GET"])
    @authenticate_request
    def count_year(year):
        """Returns the number of rows for a specific year in the stock data.

        Returns:
            JSON: { 'year': <year>, 'count': <row_count> }
            or JSON: {'error': 'Year not found in the data'}
        """
        row_count = len(stock_data[stock_data["date"].str.contains(str(year))])

        if row_count == 0:
            return jsonify({"error": "Year not found in the data"}), 404
        return jsonify({"year": int(year), "count": row_count})
