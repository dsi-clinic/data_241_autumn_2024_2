"""ROUTES v3"""

import sqlite3
import logging
from flask import Flask, request, jsonify
from stock_app.api.route_utils.decorators import authenticate_request

# Path to your SQLite database file
DB_PATH = "/app/src/data/stocks.db"


# Configure logging
logging.basicConfig(level=logging.INFO)



# Utility for Database Connection
def get_db_connection():
    """Get a database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Enable dictionary-like row access
    return conn




#__________________________________________________________________________________________

#/api/v3/accounts



def get_account_data():
    """Returns a list of all accounts."""
    try:
        conn = get_db_connection()
        accounts = conn.execute("SELECT id AS account_id, name FROM accounts").fetchall()
        conn.close()

        return jsonify([dict(account) for account in accounts]), 200
    except Exception as e:
        logging.error(f"Error fetching accounts: {e}")
        return jsonify({"error": str(e)}), 500


def add_account():
    """Creates a new account."""
    try:
        data = request.get_json()
        name = data.get("name")

        if not name:
            return jsonify({"error": "Name is required"}), 400

        conn = get_db_connection()
        existing = conn.execute("SELECT 1 FROM accounts WHERE name = ?", (name,)).fetchone()
        if existing:
            conn.close()
            return jsonify({"error": "Account already exists"}), 409

        conn.execute("INSERT INTO accounts (name) VALUES (?)", (name,))
        conn.commit()
        account_id = conn.execute("SELECT last_insert_rowid() AS id").fetchone()["id"]
        conn.close()

        return jsonify({"account_id": account_id, "name": name}), 201
    except Exception as e:
        logging.error(f"Error adding account: {e}")
        return jsonify({"error": str(e)}), 500


def delete_account():
    """Deletes an account."""
    try:
        data = request.get_json()
        account_id = data.get("account_id")

        conn = get_db_connection()
        conn.execute("DELETE FROM accounts WHERE id = ?", (account_id,))
        conn.commit()
        if conn.total_changes == 0:
            conn.close()
            return jsonify([]),404
        conn.execute("DELETE FROM stocks_owned WHERE account_id = ?", (account_id,))
        conn.commit()
        conn.close()
        return jsonify([]),204

    except Exception as e:
        logging.error(f"Error deleting account: {e}")
        return jsonify({"error": str(e)}), 500
#___________________________________________________________________________________________________________-

#

def get_stock_data(symbol):
    """Returns stock holdings for a specific symbol."""
    try:
        conn = get_db_connection()
        holdings = conn.execute("""
            SELECT account_id, purchase_date, sale_date, number_of_shares
            FROM stocks_owned
            WHERE symbol = ?
        """, (symbol,)).fetchall()
        conn.close()

        if not holdings:
            return jsonify([]), 200

        holdings_list = [dict(h) for h in holdings]
        return jsonify({"symbol": symbol, "holdings": holdings_list}), 200
    except Exception as e:
        logging.error(f"Error fetching stock data: {e}")
        return jsonify({"error": str(e)}), 500

def add_stock_data():
    try:
        data = request.get_json()
        account_id_v = data.get("account_id")
        symbol_v = data.get("symbol")
        purchase_date_v = data.get("purchase_date")
        sale_date_v = data.get("sale_date")
        number_of_shares_v = data.get("number_of_shares")

        '''
        ####ADD IF DATA NOT VALID
        if not purchase_date:
            return jsonify({"error": "Name is required"}), 400
        ##############
        '''
        conn = get_db_connection()
        conn.execute("INSERT INTO stocks_owned (account_id,symbol,purchase_date,sale_date,number_of_shares) VALUES (?,?,?,?,?)", (account_id_v,symbol_v,purchase_date_v,sale_date_v,number_of_shares_v))
        conn.commit()
        conn.close()

        return jsonify({"account_id": account_id_v, "symbol": symbol_v, "purchase_date":purchase_date_v,"sale_date":sale_date_v,"number_of_shares":number_of_shares_v}), 201
    except Exception as e:
        logging.error(f"Error adding account: {e}")
        return jsonify({"error": str(e)}), 500

def delete_stock_data():
    try:
        # Get the JSON data from the request
        data = request.get_json()
        
        # Extract parameters from the request
        account_id_v = data.get("account_id")
        symbol_v = data.get("symbol")
        purchase_date_v = data.get("purchase_date")
        sale_date_v = data.get("sale_date")
        number_of_shares_v = data.get("number_of_shares")
        
        
        # Get a database connection
        conn = get_db_connection()
        cursor = conn.cursor()
        # Prepare and execute the DELETE query
        cursor.execute("""
            DELETE FROM stocks_owned
            WHERE account_id = ? AND symbol = ? AND purchase_date = ? AND sale_date = ? AND number_of_shares = ?
        """, (account_id_v, symbol_v, purchase_date_v, sale_date_v, number_of_shares_v))

        if cursor.rowcount == 0:
            # If no rows were deleted, return 404 Not Found
            return jsonify({"error": "Stock data not found for deletion"}), 404

        # Commit and close the connection
        conn.commit()
        conn.close()

        return '', 204  
        
    except Exception as e:
        logging.error(f"Error deleting stock data for account_id: {account_id_v}, symbol: {symbol_v}: {e}")
        return jsonify({"error": "Failed to delete stock data"}), 500




def get_id_stock(acc_id):
    """
    Get all stock holding for a particular id
    """

    try:
        conn = get_db_connection()
        stock_data = conn.execute("SELECT * FROM stocks_owned WHERE account_id = ?", (acc_id,)).fetchall()
        conn.close()
        conn = get_db_connection()
        name  = conn.execute("SELECT name FROM accounts WHERE id = ?", (acc_id,)).fetchone()[0]
        conn.close()

        if not name:
            return jsonify([]), 404
        if not stock_data:
            return jsonify({'account_id':acc_id,'name':name,'stock_holdings':[]})
        
        return jsonify({'account_id':acc_id,'name':name,'stock_holdings':[dict(row) for row in stock_data] })
    except Exception as e:
        logging.error(f"Error getting stock data from id: {e}")
        return jsonify({"error": str(e)}), 500




def calculate_account_returns(account_id):
    """
    Returns the nominal return for all stock holdings of an account.

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
    """
    try:
        # Check if account exists

        """
        query_account_check = "SELECT COUNT(*) FROM accounts WHERE id = ?"
        with sqlite3.connect("/app/src/data/stocks.db") as conn:
            cursor = conn.cursor()
            cursor.execute(query_account_check, (account_id,))
            account_exists = cursor.fetchone()[0]
        if not account_exists:
            return jsonify({"error": "Account not found"}), 404

        """
       
        # Calculate the nominal return using a single SQL query
        query = """
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
        with sqlite3.connect("/app/src/data/stocks.db") as conn:
            cursor = conn.cursor()
            cursor.execute(query, (account_id,))
            total_return = cursor.fetchone()[0]

        # If the account has no holdings, return 0.0
        if total_return is None:
            total_return = 0.0

        return jsonify({"account_id": account_id, "return": total_return}), 200

    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
        return jsonify({"error": "Failed to calculate returns"}), 500

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500

#___________________________________________________________________________________________________

def register_routes3(app):
    # Accounts Routes
    @app.route("/api/v3/accounts", methods=["GET", "POST","DELETE"])
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