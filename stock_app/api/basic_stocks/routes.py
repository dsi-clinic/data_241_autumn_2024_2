"""Flask Routes for Part 1"""

import logging

from flask import jsonify

from stock_app.api.data_utils.loading_utils import execute_stock_q
from stock_app.api.route_utils.decorators import authenticate_request

# Configure logging
logging.basicConfig(level=logging.INFO)


def get_market_counts():
    """Helper function to get row counts by market (NYSE, NASDAQ).

    Returns:
        dict: { 'nyse': <count>, 'nasdaq': <count> }
    """
    query = "SELECT market, COUNT(*) FROM stocks GROUP BY market"
    try:
        counts = execute_stock_q(query).fetchall()
        market_counts = {market.lower(): count for market, count in counts}
        return {
            "nyse": market_counts.get("nyse", 0),
            "nasdaq": market_counts.get("nasdaq", 0),
        }
    except Exception as e:
        logging.error(f"Database query failed: {e}")
        return None


def get_unique_stock_count():
    """Helper function to get the count of unique stocks.

    Returns:
        int: Number of unique stocks in the data.
    """
    query = "SELECT COUNT(DISTINCT Symbol) FROM stocks"
    try:
        uniq = execute_stock_q(query).fetchone()[0]
        return uniq
    except Exception as e:
        logging.error(f"Database query failed: {e}")
        return None


def get_row_count():
    """Helper function to get the total row count.

    Returns:
        int: Total number of rows in the data.
    """
    query = "SELECT COUNT(*) FROM stocks"
    try:
        row_count = execute_stock_q(query).fetchone()[0]
        return row_count
    except Exception as e:
        logging.error(f"Database query failed: {e}")
        return None


def register_routes1(app):
    """Registers Part 1 Routes"""

    @app.route("/api/v1/row_by_market_count", methods=["GET"])
    @authenticate_request
    def get_row_by_market_count_route():
        """Returns rows for (NASDAQ, NYSE) in the data.

        Returns:
            JSON: { 'nyse': <count>, 'nasdaq': <count> }
        """
        market_counts = get_market_counts()
        print(market_counts)
        if market_counts is None:
            return jsonify({"error": "Failed to retrieve market data"}), 500
        return jsonify(market_counts)

    @app.route("/api/v1/unique_stock_count", methods=["GET"])
    @authenticate_request
    def unique_stock_count_route():
        """Returns the count of unique stocks in the stock data.

        Returns:
            JSON: { 'unique_stock_count': <number_of_unique_stocks> }
        """
        unique_count = get_unique_stock_count()
        if unique_count is None:
            return jsonify(
                {"error": "Failed to retrieve stock symbol data"}
            ), 500
        return jsonify({"unique_stock_count": unique_count})

    @app.route("/api/v1/row_count", methods=["GET"])
    @authenticate_request
    def row_count_route():
        """Returns the total number of rows in the stock data.

        Returns:
            JSON: { 'row_count': <number_of_rows> }
        """
        total_rows = get_row_count()
        if total_rows is None:
            return jsonify({"error": "Failed to retrieve row count"}), 500
        return jsonify({"row_count": total_rows})
