"""Flask Routes V2"""

import logging
import pandas as pd
import sqlite3
from flask import jsonify
from stock_app.api.route_utils.decorators import authenticate_request
from stock_app.api.data_utils.loading_utils import execute_stock_q

# Configure logging
logging.basicConfig(level=logging.INFO)


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
    price_type = price_type.capitalize()  # Ensure consistent capitization

    query = "SELECT Symbol, Date , ? FROM stocks WHERE Symbol = ?"
    try:
        cursor = sqlite3.connect("/app/src/data/stocks.db").cursor()
        cursor.execute(query, (price_type, symbol))
        symbol_df = pd.DataFrame(cursor.fetchall())
        if symbol_df.empty:
            return jsonify({"error": "Symbol not found in the data"}), 404
        symbol_df["Date"] = pd.to_datetime(
            symbol_df["Date"], format="%d-%b-%Y"
        ).dt.strftime("%Y-%b-%d")
        price_info = symbol_df[["date", price_type.lower()]].to_dict(
            orient="records"
        )
        return jsonify({"symbol": symbol, "price_info": price_info})

    except Exception as e:
        logging.error(f"Database query failed: {e}")
        return None


def get_year_count(year):
    query = "SELECT * FROM stocks WHERE strftime('%Y', Date) = ?"
    cursor = sqlite3.connect("/app/src/data/stocks.db").cursor()

    print("HEREEEE")
    count = cursor.execute(query, (year,)).fetchone()[0]
    print(f'COUNTTTTTT {count}')
    return count


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
        return get_prices(symbol, price_type)

    @app.route("/api/v2/<year>", methods=["GET"])
    @authenticate_request
    def count_year(year):
        """Returns the number of rows for a specific year in the stock data.

        Returns:
            JSON: { 'year': <year>, 'count': <row_count> }
            or JSON: {'error': 'Year not found in the data'}
        """
        row_count = get_year_count(year)
        if row_count == 0:
            return jsonify({"error": "Year not found in the data"}), 404
        return jsonify({"year": int(year), "count": row_count})
