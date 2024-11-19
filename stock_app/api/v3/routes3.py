import sqlite3
import logging
from flask import Flask, request, jsonify
from stock_app.api.route_utils.decorators import authenticate_request

# Path to your SQLite database file
DB_PATH = "stock_app.db"


# Configure logging
logging.basicConfig(level=logging.INFO)


# Utility for Database Connection
def get_db_connection():
    """Get a database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Enable dictionary-like row access
    return conn


# Accounts Routes
@app.route("/api/v3/accounts", methods=["GET", "POST"])
@authenticate_request
def accounts_op():
    if request.method == "GET":
        return get_account_data()

    if request.method == "POST":
        return add_account()


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
