"""Routes for Version 3 of the API."""

import json
import logging
import sqlite3

from flask import Response, jsonify, request

from stock_app.api.data_utils.loading_utils import execute_stock_q
from stock_app.api.route_utils.decorators import (
    authenticate_request,
    log_route,
)

# Path to SQLite database
DB_PATH = "/app/src/data/stocks.db"

# Configure logging
logging.basicConfig(level=logging.INFO)


def get_account_data():
    """Fetches all accounts.

    Returns:
        JSON response with a list of accounts or an error message.
    """
    try:
        query = "SELECT id AS account_id, name FROM accounts"
        accounts = execute_stock_q(query)

        if not accounts:
            return jsonify([]), 200

        return jsonify([dict(account) for account in accounts]), 200

    except Exception as e:
        logging.error("Error fetching accounts: %s", e)
        return jsonify({"error": "Internal server error"}), 500


def add_account():
    """Creates a new account.

    Returns:
        JSON response with created account details or an error message.
    """
    try:
        data = request.get_json()
        name = data.get("name")

        if not name:
            return jsonify({"error": "Name is required"}), 400

        query_check = "SELECT 1 FROM accounts WHERE name = ?"
        if execute_stock_q(query_check, (name,), fetch_all=False):
            return jsonify({"error": "Account already exists"}), 409

        query_insert = "INSERT INTO accounts (name) VALUES (?)"
        execute_stock_q(query_insert, (name,), fetch_all=False)

        id_check = "SELECT id FROM accounts WHERE name = ?"
        account_id = execute_stock_q(id_check, (name,), fetch_all=False)[0]

        return jsonify({"account_id": int(account_id)}), 201

    except Exception as e:
        logging.error("Error adding account: %s", e)
        return jsonify({"error": "Internal server error"}), 500


def delete_account():
    """Deletes an account and associated stock holdings.

    Returns:
        JSON response with a success message or an error message.
    """
    try:
        data = request.get_json()
        account_id = data.get("account_id")

        if not account_id:
            return jsonify({"error": "Account ID is required"}), 400

        query_delete_account = "DELETE FROM accounts WHERE id = ?"
        result = execute_stock_q(
            query_delete_account, (account_id,), fetch_all=False
        )

        if not result or result.rowcount == 0:
            return jsonify({"error": "Account not found"}), 404

        query_delete_stocks = "DELETE FROM stocks_owned WHERE account_id = ?"
        execute_stock_q(query_delete_stocks, (account_id,), fetch_all=False)

        return jsonify([]), 204

    except Exception as e:
        logging.error("Error deleting account: %s", e)
        return jsonify({"error": "Internal server error"}), 500


def get_id_stock(acc_id):
    """Fetch all stock holdings for a specific account ID.

    Args:
        acc_id (int): The account ID.

    Returns:
        JSON response with account details and stock holdings.
    """
    try:
        query_account = "SELECT name FROM accounts WHERE id = ?"
        account = execute_stock_q(query_account, (acc_id,), fetch_all=False)

        if not account:
            return jsonify({"error": "Account not found"}), 404

        query_stocks = "SELECT * FROM stocks_owned WHERE account_id = ?"
        stock_data = execute_stock_q(query_stocks, (acc_id,))

        stock_holdings = [dict(row) for row in stock_data]

        response_data = {
            "account_id": int(acc_id),
            "name": account["name"],
            "stock_holdings": stock_holdings,
        }
        return jsonify(response_data), 200

    except Exception as e:
        logging.error(
            "Error fetching stock data for account ID %s: %s",
            acc_id,
            e,
        )

        return jsonify({"error": "Internal server error"}), 500


def get_stock_data(symbol):
    """Fetch stock holdings for a specific symbol.

    Args:
        symbol (str): Stock symbol.

    Returns:
        JSON response with stock data or an error message.
    """
    try:
        query = """
            SELECT account_id, purchase_date, sale_date, number_of_shares
            FROM stocks_owned
            WHERE symbol = ?
        """
        holdings = execute_stock_q(query, (symbol,))

        holdings_list = [
            {key: row[key] for key in row.keys()} for row in holdings
        ]

        response_data = {
            "symbol": symbol,
            "holdings": holdings_list,
        }
        return Response(
            json.dumps(response_data),
            mimetype="application/json",
            status=200,
        )

    except sqlite3.Error as e:
        logging.error(
            "Database error fetching stock data for symbol %s: %s",
            symbol,
            e,
        )

        return jsonify({"error": "Database error"}), 500

    except Exception as e:
        logging.error(
            "Unexpected error fetching stock data for symbol %s: %s",
            symbol,
            e,
        )

        return jsonify({"error": "Internal server error"}), 500


def add_stock_data():
    """Adds new stock data to the database."""
    try:
        # Parse and validate JSON input
        data = request.get_json()
        required_fields = [
            "account_id",
            "symbol",
            "purchase_date",
            "sale_date",
            "number_of_shares",
        ]

        # Validate required fields
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        # Extract parameters
        account_id_v = data.get("account_id")
        symbol_v = data.get("symbol")
        purchase_date_v = data.get("purchase_date")
        sale_date_v = data.get("sale_date")
        number_of_shares_v = data.get("number_of_shares")

        # Validate purchase and sale dates
        purchase_date_query = """
        SELECT Distinct Date
        FROM stocks
        WHERE Date = ?
        """
        sale_date_query = """
        SELECT Distinct Date
        FROM stocks
        WHERE Date = ?
        """

        purchase_date_in_stock = execute_stock_q(
            purchase_date_query, (purchase_date_v,), fetch_all=False
        )
        sale_date_in_stock = execute_stock_q(
            sale_date_query, (sale_date_v,), fetch_all=False
        )

        if not purchase_date_in_stock or not sale_date_in_stock:
            return jsonify({"error": "Invalid date"}), 400

        # Insert new stock data
        insert_query = """
        INSERT INTO stocks_owned (
            account_id, symbol, purchase_date, sale_date, number_of_shares
        ) VALUES (?, ?, ?, ?, ?)
        """
        parameters = (
            account_id_v,
            symbol_v,
            purchase_date_v,
            sale_date_v,
            number_of_shares_v,
        )
        execute_stock_q(insert_query, parameters, fetch_all=False)

        # Return success response
        return "", 201

    except RuntimeError as e:
        logging.error(f"Error adding stock data: {e}")
        return jsonify({"error": str(e)}), 500


def delete_stock_data():
    """Deletes stock data from the database."""
    try:
        # Parse and validate JSON input
        data = request.get_json()
        required_fields = [
            "account_id",
            "symbol",
            "purchase_date",
            "sale_date",
            "number_of_shares",
        ]

        # Validate all required fields are present
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        # Extract parameters
        parameters = (
            data.get("account_id"),
            data.get("symbol"),
            data.get("purchase_date"),
            data.get("sale_date"),
            data.get("number_of_shares"),
        )

        # Define SQL query
        query = """
        DELETE FROM stocks_owned
        WHERE account_id = ? AND symbol = ? AND purchase_date = ?
        AND sale_date = ? AND number_of_shares = ?
        """

        # Execute the query using the helper function
        cursor = execute_stock_q(query, parameters, fetch_all=False)

        # Check if a row was deleted
        if cursor.rowcount == 0:
            return jsonify({"error": "Stock data not found for deletion"}), 404

        return "", 204

    except RuntimeError as e:
        logging.error(f"Error deleting stock data. Error: {e}")
        return jsonify({"error": "Failed to delete stock data"}), 500


def calculate_account_returns(account_id):
    """Returns the nominal return for all stock holdings of an account.

    Parameters:
    - account_id: int

    Returns:
    {
        'account_id': int,
        'return': float
    }

    Status Codes:
    - 200: Successfully calculated.
    - 404: Account not found.
    - 500: Internal server error.
    """
    try:
        # Check if the account exists
        query = "SELECT COUNT(*) FROM stocks_owned WHERE account_id = ?"
        account_exists = execute_stock_q(
            query, (account_id,), fetch_all=False
        )[0]

        if not account_exists:
            return jsonify({"error": "Account not found"}), 404

        # Calculate the nominal return
        query_return = """
        SELECT
            SUM(
                stocks_owned.number_of_shares *
                (close_prices.Close - open_prices.Open)
            ) AS total_return
        FROM
            stocks_owned
        INNER JOIN
            stocks AS open_prices
            ON stocks_owned.symbol = open_prices.Symbol
            AND stocks_owned.purchase_date = open_prices.Date
        INNER JOIN
            stocks AS close_prices
            ON stocks_owned.symbol = close_prices.Symbol
            AND stocks_owned.sale_date = close_prices.Date
        WHERE
            stocks_owned.account_id = ?
        """
        total_return = execute_stock_q(
            query_return, (account_id,), fetch_all=False
        )[0]

        # Default return value to 0.0 if no holdings exist
        if total_return is None:
            total_return = 0.0

        return jsonify(
            {"account_id": int(account_id), "return": total_return}
        ), 200

    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
        return jsonify({"error": "Failed to calculate returns"}), 500

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500


def register_routes3(app):
    """Register all API routes for Version 3.

    Args:
        app (Flask): The Flask application instance.
    """

    @app.route("/api/v3/accounts", methods=["GET", "POST", "DELETE"])
    @log_route
    @authenticate_request
    def accounts_op():
        """Gets, Post and Deletes Account data"""
        if request.method == "GET":
            return get_account_data()
        if request.method == "POST":
            return add_account()
        if request.method == "DELETE":
            return delete_account()

    @app.route("/api/v3/stocks/<symbol>", methods=["GET"])
    @log_route
    @authenticate_request
    def stock_data_op_get(symbol):
        """Gets stock owned per symbol"""
        return get_stock_data(symbol)

    @app.route("/api/v3/accounts/<acc_id>", methods=["GET"])
    @log_route
    @authenticate_request
    def accounts_op_get(acc_id):
        """Returns stocks owned for an account"""
        return get_id_stock(acc_id)

    @app.route("/api/v3/stocks", methods=["POST", "DELETE"])
    @log_route
    @authenticate_request
    def stock_data_op_post_del():
        """Adds and Deletes Stock Own Data"""
        if request.method == "POST":
            return add_stock_data()

        if request.method == "DELETE":
            return delete_stock_data()

    @app.route("/api/v3/accounts/return/<account_id>", methods=["GET"])
    @log_route
    @authenticate_request
    def account_returns(account_id):
        """Returns profit made"""
        return calculate_account_returns(account_id)
