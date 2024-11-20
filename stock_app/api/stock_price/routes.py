"""Flask Routes V2."""

import logging
import sqlite3

import pandas as pd
from flask import jsonify

from stock_app.api.data_utils.loading_utils import execute_stock_q
from stock_app.api.route_utils.decorators import authenticate_request

# Configure logging
logging.basicConfig(level=logging.INFO)

FOUR_DIGIT_YEAR_LENGTH = 4  # Constant for year length validation


def get_prices(symbol, price_type):
    """Fetch price information for a specific stock symbol.

    Args:
        symbol (str): Stock symbol to lookup.
        price_type (str): Type of price ('Open', 'Close', 'High', 'Low').

    Returns:
        Response: JSON response with price information or an error message.
    """
    try:
        symbol = symbol.upper()
        price_type = price_type.capitalize()

        valid_price_types = {"Open", "Close", "High", "Low"}
        if price_type not in valid_price_types:
            return (
                jsonify(
                    {
                        "error": f"Invalid price type: {price_type}. "
                        f"Allowed values: {list(valid_price_types)}"
                    }
                ),
                400,
            )

        query = (
            f"SELECT Symbol, Date, {price_type} FROM stocks WHERE Symbol = ?"
        )
        rows = execute_stock_q(query, (symbol,))

        if not rows:
            return (
                jsonify(
                    {"error": f"Symbol '{symbol}' not found in the data"}
                ),
                404,
            )

        symbol_df = pd.DataFrame(rows, columns=["Symbol", "Date", price_type])
        symbol_df["Date"] = pd.to_datetime(
            symbol_df["Date"], format="%d-%b-%Y", errors="coerce"
        ).dt.strftime("%Y-%m-%d")

        if symbol_df["Date"].isna().any():
            logging.error("Invalid date format detected in the database.")
            return jsonify({"error": "Invalid date format in data"}), 500

        price_info = symbol_df.apply(
            lambda row: {
                "date": row["Date"],
                price_type.lower(): row[price_type],
            },
            axis=1,
        ).tolist()


        response = {"symbol": symbol, "price_info": price_info}
        return jsonify(response), 200

    except sqlite3.Error as e:
        logging.error("Database query failed: %s", e)
        return jsonify({"error": "Failed to fetch price data"}), 500

    except Exception as e:
        logging.error("Unexpected error: %s", e)
        return jsonify({"error": "An unexpected error occurred"}), 500


def get_year_count(year):
    """Get the count of stock records for a specific year.

    Args:
        year (str): The year to filter records by.

    Returns:
        JSON response: { 'year': str, 'count': int }
    """
    try:
        if not year.isdigit() or len(year) != FOUR_DIGIT_YEAR_LENGTH:
            return (
                jsonify(
                    {"error": "Invalid year format. Provide a 4-digit year."}
                ),
                400,
            )

        query = "SELECT COUNT(*) FROM stocks WHERE SUBSTR(Date, -4) = ?"
        result = execute_stock_q(query, (year,), fetch_all=False)
        count = result[0] if result else 0

        return jsonify({"year": year, "count": count}), 200

    except sqlite3.Error as e:
        logging.error(
            "Database error while fetching year count for %s: %s", year, e
        )
        return jsonify({"error": "Failed to fetch year count"}), 500

    except Exception as e:
        logging.error(
            "Unexpected error while fetching year count for %s: %s", year, e
        )
        return jsonify({"error": "An unexpected error occurred"}), 500


def register_routes2(app):
    """Register Part 2 Routes."""

    @app.route("/api/v2/<price_type>/<symbol>", methods=["GET"])
    def price_endpoint(price_type, symbol):
        """Fetch prices for a given symbol and price type."""
        if not price_type:
            return jsonify({"error": "Price type is required"}), 400

        response = get_prices(symbol, price_type)
        if response is None:
            return (
                jsonify({"error": f"No data found for symbol {symbol}"}), 404
            )

        return response

    @app.route("/api/v2/<year>", methods=["GET"])
    @authenticate_request
    def count_year(year):
        """Fetch the number of stock rows for a specific year."""
        response = get_year_count(year)
        if not response.json.get("count", 0):
            return jsonify({"error": "Year not found in the data"}), 404
        return response
