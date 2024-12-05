"""Routes for backtesting calculations in the stock application.

This module provides API routes for validating stock data,
performing computations, and responding to requests with results.
"""

import sqlite3
from datetime import datetime, timedelta

import pandas as pd
from flask import jsonify, request

from stock_app.api.data_utils.loading_utils import execute_stock_q
from stock_app.api.route_utils.decorators import (
    authenticate_request,
    log_route,
)


def calc_backtest():
    """Perform backtesting calculations based on JSON request data.

    Returns:
        Response: JSON response with total returns and number of observations.
    """
    # Parse JSON request data
    data = request.get_json()
    value_1 = data.get("value_1")
    value_2 = data.get("value_2")
    operator = data.get("operator")
    purchase_type = data.get("purchase_type")
    start_date = data.get("start_date")  # Format: '%Y-%m-%d'
    end_date = data.get("end_date")  # Format: '%Y-%m-%d'

    # Validate start and end dates
    date_validation_query = "SELECT Date FROM stocks WHERE Date = ?"
    start_date_in_stock = execute_stock_q(
        date_validation_query, (start_date,), fetch_all=False
    )
    end_date_in_stock = execute_stock_q(
        date_validation_query, (end_date,), fetch_all=False
    )

    if not start_date_in_stock or not end_date_in_stock:
        return jsonify({"error": "Invalid Start / End date"}), 400

    # Column mapping
    column_map = {"O": "Open", "C": "Close", "L": "Low", "H": "High"}
    col_one = column_map.get(value_1[0])
    col_two = column_map.get(value_2[0])

    # Calculate back days
    back_val_one = int(value_1[1:])
    back_val_two = int(value_2[1:])
    back_target = max(back_val_one, back_val_two)
    back_day = (
        datetime.strptime(start_date, "%Y-%m-%d") - timedelta(days=back_target)
    ).strftime("%Y-%m-%d")

    # Query data from the database
    query = """
    SELECT *
    FROM stocks
    WHERE Date BETWEEN ? AND ?
    """
    conn = sqlite3.connect("/app/src/data/stocks.db")
    cursor = conn.cursor()
    cursor.execute(query, (back_day, end_date))
    results = cursor.fetchall()
    headers = [description[0] for description in cursor.description]
    stock_range_df = pd.DataFrame(results, columns=headers)
    conn.close()

    # Filter data for unique symbols and valid date range
    stock_range_df["Date"] = pd.to_datetime(stock_range_df["Date"])
    stock_range_df = stock_range_df.sort_values(by=["Symbol", "Date"])

    # Initialize totals
    total = 0
    num_observations = 0

    # Precompute shifted values for back days
    stock_range_df["val_one_day"] = stock_range_df["Date"] - pd.to_timedelta(
        back_val_one, unit="D"
    )
    stock_range_df["val_two_day"] = stock_range_df["Date"] - pd.to_timedelta(
        back_val_two, unit="D"
    )

    # Merge to get lagged data for value_1 and value_2
    val_one_df = stock_range_df[["Symbol", "Date", col_one]].rename(
        columns={"Date": "val_one_day", col_one: "val_one_target"}
    )
    val_two_df = stock_range_df[["Symbol", "Date", col_two]].rename(
        columns={"Date": "val_two_day", col_two: "val_two_target"}
    )
    merged_df = (
    stock_range_df.merge(
        val_one_df, on=["Symbol", "val_one_day"], how="left"
    ).merge(
        val_two_df, on=["Symbol", "val_two_day"], how="left"
    )
)

    # Filter for valid start-to-end date range
    start_to_end = pd.date_range(start=start_date, end=end_date)
    merged_df = merged_df[merged_df["Date"].isin(start_to_end)]

    # Apply conditions and calculate totals
    for _, row in merged_df.iterrows():
        if pd.isna(row["val_one_target"]) or pd.isna(row["val_two_target"]):
            continue

        if operator == "LT" and row["val_one_target"] < row["val_two_target"]:
            day_total = (
                row["Close"] - row["Open"]
                if purchase_type == "B"
                else row["Open"] - row["Close"]
            )
            total += day_total
            num_observations += 1
        elif (
            operator == "LTE"
            and row["val_one_target"] <= row["val_two_target"]
            ):
            day_total = (
                row["Close"] - row["Open"]
                if purchase_type == "B"
                else row["Open"] - row["Close"]
            )
            total += day_total
            num_observations += 1

    return jsonify(
        {
            "return": round(total, 2),
            "num_observations": int(num_observations),
        }
    )


def register_routes4(app):
    """Register all API routes for Version 4.

    Args:
        app (Flask): The Flask application instance.
    """
    @app.route("/api/v4/back_test", methods=["POST"])
    @log_route
    @authenticate_request
    def back_test():
        """Handle backtesting API requests.

        Returns:
            Response: JSON response with calculation results or error messages.
        """
        return calc_backtest()
