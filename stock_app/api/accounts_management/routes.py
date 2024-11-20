"""Routes for Version 3 of the API."""

import json
import logging
import sqlite3

from flask import Response, jsonify, request

from stock_app.api.data_utils.loading_utils import execute_stock_q
from stock_app.api.route_utils.decorators import authenticate_request

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

        query_last_id = "SELECT last_insert_rowid() AS id"
        account_id = execute_stock_q(query_last_id, fetch_all=False)["id"]

        return jsonify({"account_id": account_id, "name": name}), 201

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
            query_delete_account, 
            (account_id,), 
            fetch_all=False
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
            "account_id": acc_id,
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
            {key: row[key] for key in row.keys()}
            for row in holdings
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


def register_routes3(app):
    """Register all API routes for Version 3.

    Args:
        app (Flask): The Flask application instance.
    """
    @app.route("/api/v3/accounts", methods=["GET", "POST", "DELETE"])
    @authenticate_request
    def accounts_op():
        if request.method == "GET":
            return get_account_data()
        if request.method == "POST":
            return add_account()
        if request.method == "DELETE":
            return delete_account()

    @app.route("/api/v3/stocks/<symbol>", methods=["GET"])
    @authenticate_request
    def stock_data_op_get(symbol):
        return get_stock_data(symbol)

    @app.route("/api/v3/accounts/<acc_id>", methods=["GET"])
    @authenticate_request
    def accounts_op_get(acc_id):
        return get_id_stock(acc_id)
