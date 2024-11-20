"""Flask Routes V2."""

import json
import logging
import sqlite3

import pandas as pd
from flask import jsonify

from stock_app.api.route_utils.decorators import authenticate_request

# Configure logging
logging.basicConfig(level=logging.INFO)


def get_prices(symbol: str, price_type: str):
    """Fetch price information for a specific stock symbol.

    Args:
        symbol (str): Stock symbol to lookup.
        price_type (str): Type of price ('Open', 'Close', 'High', 'Low').

    Returns:
        tuple: A JSON response and HTTP status code.
    """
    # Ensure consistent formatting
    symbol = symbol.upper()
    price_type = price_type.capitalize()

    # Validate the price_type input to prevent SQL injection
    valid_price_types = {"Open", "Close", "High", "Low"}
    if price_type not in valid_price_types:
        return json.dumps({
            "error": (
                f"Invalid price type: {price_type}. "
                f"Allowed values: {list(valid_price_types)}"
            )
        }), 400

    # Construct the query with a WHERE clause for symbol
    query = f"SELECT Symbol, Date, {price_type} FROM stocks WHERE Symbol = ?"

    try:
        # Execute the query
        with sqlite3.connect("/app/src/data/stocks.db") as conn:
            cursor = conn.cursor()
            cursor.execute(query, (symbol,))
            rows = cursor.fetchall()

        # If no rows are found
        if not rows:
            return json.dumps({
                "error": f"Symbol '{symbol}' not found in the data"
            }), 404

        # Create a DataFrame with explicit column names
        symbol_df = pd.DataFrame(rows, columns=["Symbol", "Date", price_type])

        # Convert and format the 'Date' column
        symbol_df["Date"] = pd.to_datetime(
            symbol_df["Date"], format="%d-%b-%Y", errors="coerce"
        ).dt.strftime("%Y-%b-%d")

        # Check for invalid dates
        if symbol_df["Date"].isna().any():  # Fix for PD003
            logging.error("Invalid date format detected in the database.")
            return json.dumps({"error": "Invalid date format in data"}), 500

        # Prepare the response
        price_info = symbol_df.apply(
            lambda row: {
                "date": row["Date"],
                price_type.lower(): row[price_type]
            },
            axis=1
        ).tolist()

        # Explicitly construct the ordered JSON response
        response = {
            "symbol": symbol,
            "price_info": price_info,
        }

        # Use json.dumps to control serialization
        return json.dumps(response), 200

    except sqlite3.Error as e:
        # Log and return database errors
        logging.error(f"Database query failed: {e}")
        return json.dumps({"error": "Failed to fetch price data"}), 500

    except Exception as e:
        # Handle unexpected errors
        logging.error(f"Unexpected error: {e}")
        return json.dumps({"error": "An unexpected error occurred"}), 500


def get_year_count(year: str) -> int:
    """Get the count of records for a specific year.

    Args:
        year (str): The year to filter records.

    Returns:
        int: Count of records for the given year.
    """
    query = "SELECT COUNT(*) FROM stocks WHERE SUBSTR(Date, -4) = ?"
    with sqlite3.connect("/app/src/data/stocks.db") as conn:
        cursor = conn.cursor()
        count = cursor.execute(query, (year,)).fetchone()[0]
    return count


def register_routes2(app):
    """Registers Part 2 Routes."""
    @app.route("/api/v2/<price_type>/<symbol>", methods=["GET"])
    def price_endpoint(price_type: str, symbol: str):
        """Endpoint for fetching stock prices by type and symbol.

        Args:
            price_type (str): Type of price ('Open', 'Close', 'High', 'Low').
            symbol (str): Stock symbol to lookup.

        Returns:
            JSON: Response with price details or error message.
        """
        if not price_type:
            return jsonify({"error": "Price type is required"}), 400

        response = get_prices(symbol, price_type)
        if response is None:
            return jsonify({
                "error": f"No data found for symbol {symbol}"
            }), 404

        return response

    @app.route("/api/v2/<year>", methods=["GET"])
    @authenticate_request
    def count_year(year: str):
        """Returns the number of rows for a specific year in the stock data.

        Args:
            year (str): The year to filter stock data.

        Returns:
            JSON: { 'year': <year>, 'count': <row_count> }
            or JSON: {'error': 'Year not found in the data'}
        """
        row_count = get_year_count(year)
        if row_count == 0:
            return jsonify({"error": "Year not found in the data"}), 404
        return jsonify({"year": int(year), "count": row_count})
