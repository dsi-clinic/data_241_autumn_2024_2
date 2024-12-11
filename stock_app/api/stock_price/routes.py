"""Flask Routes V2."""

import logging
import sqlite3

import pandas as pd
from flask import Response, jsonify

from stock_app.api.data_utils.loading_utils import execute_stock_q
from stock_app.api.route_utils.decorators import (
    authenticate_request,
    log_route,
)

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
            return Response(status=400)

        query = (
            f"SELECT Symbol, Date, {price_type} FROM stocks WHERE Symbol = ?"
        )
        rows = execute_stock_q(query, (symbol,))

        if not rows:
            return Response(status=404)

        symbol_df = pd.DataFrame(rows, columns=["Symbol", "Date", price_type])
        symbol_df["Date"] = pd.to_datetime(
            symbol_df["Date"], format="%Y-%m-%d", errors="coerce"
        ).dt.strftime("%Y-%m-%d")

        if symbol_df["Date"].isna().any():
            logging.error("Invalid date format detected in the database.")
            return Response(status=500)

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
        return Response(status=500)

    except Exception as e:
        logging.error("Unexpected error: %s", e)
        return Response(status=500)


def get_year_count(year):
    """Get the count of stock records for a specific year.

    Args:
        year (str): The year to filter records by.

    Returns:
        JSON response: { 'year': str, 'count': int }
    """
    try:
        if not year.isdigit() or len(year) != FOUR_DIGIT_YEAR_LENGTH:
            return Response(status=400)

        query = "SELECT COUNT(*) FROM stocks WHERE SUBSTRING(Date, 1, 4) = ?"
        result = execute_stock_q(query, (year,), fetch_all=False)

        count = result[0] if result else 0
        if int(count) == 0:
            return Response(status=404)
        else:
            return jsonify({"year": int(year), "count": int(count)}), 200

    except sqlite3.Error as e:
        logging.error(
            "Database error while fetching year count for %s: %s", year, e
        )
        return Response(status=500)

    except Exception as e:
        logging.error(
            "Unexpected error while fetching year count for %s: %s", year, e
        )
        return Response(status=500)


def register_routes2(app):
    """Register Part 2 Routes."""

    @app.route("/api/v2/<price_type>/<symbol>", methods=["GET"])
    @log_route
    @authenticate_request
    def price_endpoint(price_type, symbol):
        """Fetch prices for a given symbol and price type."""
        if not price_type:
            return Response(status=400)

        response = get_prices(symbol, price_type)
        if response is None:
            return Response(status=404)

        return response

    @app.route("/api/v2/<year>", methods=["GET"])
    @log_route
    @authenticate_request
    def count_year(year):
        """Fetch the number of stock rows for a specific year."""
        response = get_year_count(year)
        return response
