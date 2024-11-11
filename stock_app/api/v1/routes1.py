"""Flask Routes for Part 1"""

import logging
from flask import jsonify
from stock_app.api.data_utils.loading_utils import load_data
from stock_app.api.route_utils.decorators import authenticate_request

# Configure logging
logging.basicConfig(level=logging.INFO)

# Load stock data
try:
    stock_data = load_data()
    # Ensure columns are consistently lowercase
    stock_data.columns = stock_data.columns.str.lower()
except Exception as e:
    logging.error(f"Failed to load stock data: {e}")

def register_routes1(app):
    """Registers Part 1 Routes"""

    @app.route("/api/v1/row_by_market_count", methods=["GET"])
    @authenticate_request
    def get_row_by_market_count():
        """Returns rows for (NASDAQ, NYSE) in the data.

        Returns:
            JSON: { 'nyse': <count>, 'nasdaq': <count> }
        """
        if "market" not in stock_data.columns:
            logging.error("'market' column missing in the data.")
            return jsonify({"error": "Missing market data"}), 400

        market_counts = stock_data["market"].value_counts().to_dict()
        return jsonify(
            {
                "nyse": market_counts.get("nyse", 0),
                "nasdaq": market_counts.get("nasdaq", 0),
            }
        )

    @app.route("/api/v1/unique_stock_count", methods=["GET"])
    @authenticate_request
    def get_unique_stock_count():
        """Returns the count of unique stocks in the stock data.

        Returns:
            JSON: { 'unique_stock_count': <number_of_unique_stocks> }
        """
        if "symbol" not in stock_data.columns:
            logging.error("'symbol' column missing in the data.")
            return jsonify({"error": "Missing stock symbol data"}), 400

        unique_stocks = stock_data["symbol"].nunique()
        return jsonify({"unique_stock_count": unique_stocks})

    @app.route("/api/v1/row_count", methods=["GET"])
    @authenticate_request
    def get_row_count():
        """Returns the total number of rows in the stock data.

        Returns:
            JSON: { 'row_count': <number_of_rows> }
        """
        row_count = len(stock_data)
        return jsonify({"row_count": row_count})
