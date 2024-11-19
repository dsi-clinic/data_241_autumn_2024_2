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



#___________________________________________________________________________________________________

def register_routes3(app):
    # Accounts Routes
    @app.route("/api/v3/accounts", methods=["GET", "POST"])
    @authenticate_request
    def accounts_op():
        if request.method == "GET":
            return get_account_data()

        if request.method == "POST":
            return add_account()

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