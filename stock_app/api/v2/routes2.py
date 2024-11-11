"""Flask Routes for project part 2"""

import logging

import pandas as pd
from flask import jsonify

from stock_app.api.data_utils.loading_utils import load_data
from stock_app.api.route_utils.decorators import authenticate_request

# Configure logging
logging.basicConfig(level=logging.INFO)


# Load stock data
try:
    stock_data = load_data()
except Exception as e:
    logging.error(f"Failed to load stock data: {e}")


def get_prices(symbol, price_type):
    """Helper function to get price information for a specific stock symbol.

    Args:
        symbol (str): Stock symbol to lookup.
        price_type (str): Type of price ('Open', 'Close', 'High', 'Low').

    Returns:
        JSON: { 'symbol': <SYMBOL>, 'price_info': <list_of_prices> }
              or JSON: {'error': 'Symbol not found in the data'}
    """
    if symbol not in stock_data["Symbol"].unique():
        return jsonify({"error": "Symbol not found in the data"}), 404

    symbol_df = stock_data[stock_data["Symbol"] == symbol]
    symbol_df["Date"] = pd.to_datetime(
        symbol_df["Date"], format="%d-%b-%Y"
    ).dt.strftime("%Y-%b-%d")
    price_info = symbol_df[["Date", price_type]].to_dict(orient="records")
    return jsonify({"symbol": symbol, "price_info": price_info})


def register_routes2(app):
    """Registers Part 2 Routes"""

    @app.route("/api/v2/<PRICE_TYPE>/<SYMBOL>", methods=["GET"])
    @authenticate_request
    def open_prices(PRICE_TYPE, SYMBOL):
        """Returns prices for a specific stock symbol and price type

        Returns:
            JSON: { 'symbol': <SYMBOL>, 'price_info': <list_of_prices> }
            or JSON: {'error': 'Symbol not found in the data'}
        """
        PRICE_TYPE = PRICE_TYPE.capitalize()

        return get_prices(SYMBOL, PRICE_TYPE)

    @app.route("/api/v2/<YEAR>", methods=["GET"])
    @authenticate_request
    def count_year(YEAR):
        """Returns the number of rows for a specific year in the stock data.

        Returns:
            JSON: { 'year': <YEAR>, 'count': <row_count> }
            or JSON: {'error': 'Year not found in the data'}
        """
        row_count = len(stock_data[stock_data["Date"].str.contains(str(YEAR))])

        if row_count == 0:
            return jsonify({"error": "Year not found in the data"}), 404
        return jsonify({"year": int(YEAR), "count": row_count})
