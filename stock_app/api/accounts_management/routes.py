"""ROUTES v3"""
import json
import logging
import sqlite3

from flask import Response, jsonify, request

from stock_app.api.data_utils.loading_utils import execute_stock_q
from stock_app.api.route_utils.decorators import authenticate_request

# Path to your SQLite database file
DB_PATH = "/app/src/data/stocks.db"

# Configure logging
logging.basicConfig(level=logging.INFO)

def get_account_data():
    """Returns a list of all accounts.

    Returns:
        JSON response with a list of accounts or an error message.
    """
    try:
        # Execute the query to fetch all accounts
        query = "SELECT id AS account_id, name FROM accounts"
        accounts = execute_stock_q(query)

        # Check if any accounts are retrieved
        if not accounts:
            return jsonify([]), 200  # Return an empty list with a 200 status

        # Convert accounts to a list of dictionaries and return as JSON
        return jsonify([dict(account) for account in accounts]), 200

    except Exception as e:
        # Log the error and return a 500 status with an error message
        logging.error(f"Error fetching accounts: {e}")
        return jsonify({"error": "Internal server error"}), 500



def add_account():
    """Creates a new account.

    Returns:
        JSON response with the created account details or an error message.
    """
    try:
        # Parse request data
        data = request.get_json()
        name = data.get("name")

        # Validate required fields
        if not name:
            return jsonify({"error": "Name is required"}), 400

        # Check if the account already exists
        query_check = "SELECT 1 FROM accounts WHERE name = ?"
        existing = execute_stock_q(query_check, (name,), fetch_all=False)

        if existing:
            return jsonify({"error": "Account already exists"}), 409

        # Insert the new account
        query_insert = "INSERT INTO accounts (name) VALUES (?)"
        execute_stock_q(query_insert, (name,), fetch_all=False)

        # Get the ID of the newly created account
        query_last_id = "SELECT last_insert_rowid() AS id"
        account_id = execute_stock_q(query_last_id, fetch_all=False)["id"]

        # Return success response
        return jsonify({"account_id": account_id, "name": name}), 201

    except Exception as e:
        # Log the error and return a 500 status with an error message
        logging.error(f"Error adding account: {e}")
        return jsonify({"error": "Internal server error"}), 500



def delete_account():
    """Deletes an account and its associated stock holdings.

    Returns:
        JSON response: Empty list for success or an error message.
    """
    try:
        # Parse request data
        data = request.get_json()
        account_id = data.get("account_id")

        # Validate required fields
        if not account_id:
            return jsonify({"error": "Account ID is required"}), 400

        # Delete the account
        query_delete_account = "DELETE FROM accounts WHERE id = ?"
        result = execute_stock_q(query_delete_account, (account_id,), fetch_all=False)

        # Check if any account was deleted
        if result is None or result.rowcount == 0:
            return jsonify([]), 404

        # Delete associated stock holdings
        query_delete_stocks = "DELETE FROM stocks_owned WHERE account_id = ?"
        execute_stock_q(query_delete_stocks, (account_id,), fetch_all=False)

        # Return success response
        return jsonify([]), 204

    except Exception as e:
        # Log the error and return a 500 status with an error message
        logging.error(f"Error deleting account: {e}")
        return jsonify({"error": "Internal server error"}), 500


def get_id_stock(acc_id):
    """Get all stock holdings for a specific account ID.

    Args:
        acc_id (int): The account ID to retrieve holdings for.

    Returns:
        JSON response:
            {
                "account_id": int,
                "name": str,
                "stock_holdings": [
                    {"symbol": str, "purchase_date": str, "sale_date": str, "number_of_shares": int},
                    ...
                ]
            }
    """
    try:
        # Fetch account name
        query_account = "SELECT name FROM accounts WHERE id = ?"
        account = execute_stock_q(query_account, (acc_id,), fetch_all=False)

        if not account:
            return jsonify({"error": "Account not found"}), 404

        account_name = account["name"]

        # Fetch stock holdings for the account
        query_stocks = "SELECT * FROM stocks_owned WHERE account_id = ?"
        stock_data = execute_stock_q(query_stocks, (acc_id,))

        # Convert stock holdings to a list of dictionaries
        stock_holdings = [dict(row) for row in stock_data]

        # Construct and return the response
        return jsonify({
            "account_id": acc_id,
            "name": account_name,
            "stock_holdings": stock_holdings
        }), 200

    except Exception as e:
        logging.error(f"Error getting stock data for account ID {acc_id}: {e}")
        return jsonify({"error": "Internal server error"}), 500



def get_stock_data(symbol):
    """Returns stock holdings for a specific symbol across all accounts.

    Args:
        symbol (str): The stock symbol to filter holdings.

    Returns:
        JSON response:
            {
                'symbol': str,
                'holdings': [
                    {'account_id': int, 'purchase_date': str, 'sale_date': str, 'number_of_shares': int}, ...
                ]
            }
    """
    try:
        # Query stock holdings for the given symbol
        query = """
            SELECT account_id, purchase_date, sale_date, number_of_shares
            FROM stocks_owned
            WHERE symbol = ?
        """
        holdings = execute_stock_q(query, (symbol,))

        # Convert holdings to a list of dictionaries
        holdings_list = [
            {key: row[key] for key in row.keys()} for row in holdings
        ]

        # Construct the response with the desired key order
        stock_holdings = {
            "symbol": symbol,
            "holdings": holdings_list
        }

        # Use Flask Response to return the JSON
        return Response(json.dumps(stock_holdings), mimetype="application/json", status=200)

    except sqlite3.Error as db_error:
        # Handle specific database errors
        logging.error(f"Database error fetching stock data for symbol {symbol}: {db_error}")
        return jsonify({"error": "Database error"}), 500

    except Exception as e:
        # Handle unexpected errors
        logging.error(f"Unexpected error fetching stock data for symbol {symbol}: {e}")
        return jsonify({"error": "Internal server error"}), 500



def add_stock_data():
    """Adds new stock data.

    Returns:
        JSON response with the added stock data or an error message.
    """
    try:
        # Parse request data
        data = request.get_json()
        account_id_v = data.get("account_id")
        symbol_v = data.get("symbol")
        purchase_date_v = data.get("purchase_date")
        sale_date_v = data.get("sale_date")
        number_of_shares_v = data.get("number_of_shares")

        # Validate required fields
        if not all([account_id_v, symbol_v, purchase_date_v, number_of_shares_v]):
            return jsonify({"error": "Missing required fields"}), 400

        # Validate purchase_date and sale_date
        query_date_check = """
            SELECT Date
            FROM stocks
            WHERE Date = ?
        """
        purchase_date_in_stock = execute_stock_q(query_date_check, (purchase_date_v,), fetch_all=False)
        sale_date_in_stock = None
        if sale_date_v:
            sale_date_in_stock = execute_stock_q(query_date_check, (sale_date_v,), fetch_all=False)

        if not purchase_date_in_stock or (sale_date_v and not sale_date_in_stock):
            return jsonify({"error": "Invalid date"}), 400

        # Insert stock data into the database
        query_insert = """
            INSERT INTO stocks_owned (
                account_id, symbol, purchase_date, sale_date, number_of_shares
            ) VALUES (?, ?, ?, ?, ?)
        """
        execute_stock_q(
            query_insert,
            (account_id_v, symbol_v, purchase_date_v, sale_date_v, number_of_shares_v),
            fetch_all=False
        )

        # Return success response
        return jsonify({
            "account_id": account_id_v,
            "symbol": symbol_v,
            "purchase_date": purchase_date_v,
            "sale_date": sale_date_v,
            "number_of_shares": number_of_shares_v
        }), 201

    except Exception as e:
        # Log the error and return a 500 status with an error message
        logging.error(f"Error adding stock data: {e}")
        return jsonify({"error": "Internal server error"}), 500


def delete_stock_data():
    """Deletes stock data.

    Returns:
        JSON response with appropriate status codes for success or failure.
    """
    try:
        # Parse request data
        data = request.get_json()
        account_id_v = data.get("account_id")
        symbol_v = data.get("symbol")
        purchase_date_v = data.get("purchase_date")
        sale_date_v = data.get("sale_date")
        number_of_shares_v = data.get("number_of_shares")

        # Validate required fields
        if not all([account_id_v, symbol_v, purchase_date_v, sale_date_v, number_of_shares_v]):
            return jsonify({"error": "Missing required fields"}), 400

        # Execute the delete query
        query = """
            DELETE FROM stocks_owned
            WHERE account_id = ? AND symbol = ? AND purchase_date = ?
            AND sale_date = ? AND number_of_shares = ?
        """
        result = execute_stock_q(
            query,
            (account_id_v, symbol_v, purchase_date_v, sale_date_v, number_of_shares_v),
            fetch_all=False
        )

        # Check if any rows were affected
        if result is None or result.rowcount == 0:
            return jsonify({"error": "Stock data not found for deletion"}), 404

        # Return success response
        return "", 204

    except Exception as e:
        # Log the error and return a 500 status with an error message
        logging.error(
            f"Error deleting stock data for account_id: {account_id_v}, "
            f"symbol: {symbol_v}: {e}"
        )
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
        query_account_check = "SELECT COUNT(*) FROM stocks_owned WHERE account_id = ?"
        account_exists = execute_stock_q(query_account_check, (account_id,), fetch_all=False)[0]

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
        total_return = execute_stock_q(query_return, (account_id,), fetch_all=False)[0]

        # Default return value to 0.0 if no holdings exist
        if total_return is None:
            total_return = 0.0

        return jsonify({"account_id": account_id, "return": total_return}), 200

    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
        return jsonify({"error": "Failed to calculate returns"}), 500

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500


def register_routes3(app):
    """Register all routes for version 3."""
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

    @app.route("/api/v3/stocks", methods=["POST", "DELETE"])
    @authenticate_request
    def stock_data_op_post_del():
        if request.method == "POST":
            return add_stock_data()
        if request.method == "DELETE":
            return delete_stock_data()

    @app.route("/api/v3/accounts/return/<account_id>", methods=["GET"])
    @authenticate_request
    def account_returns(account_id):
        return calculate_account_returns(account_id)

    @app.route("/api/v3/accounts/<acc_id>", methods=["GET"])
    @authenticate_request
    def accounts_op_get(acc_id):
        return get_id_stock(acc_id)
