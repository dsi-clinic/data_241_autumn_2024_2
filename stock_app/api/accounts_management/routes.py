"""Flask Routes 3"""

import logging
import pandas as pd
from flask import Flask, request, jsonify
from stock_app.api.data_utils.loading_utils import load_stock_data, load_account_data, load_stocks_owned_data
from stock_app.api.route_utils.decorators import authenticate_request

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize Flask app
app = Flask(__name__)

# Load stock data
try:
    stock_data = load_stock_data()
    account_data = load_account_data()
    stocks_owned_data = load_stocks_owned_data()
    # Ensure columns are consistently lowercase
    stock_data.columns = stock_data.columns.str.lower()
except Exception as e:
    logging.error(f"Failed to load stock data: {e}")

def get_account_stocks(account_id):
    """Returns all stocks owned by the account

    Parameters:
    account_id (int): The account ID to retrieve stocks for

    Returns:
    JSON response with account details and stock holdings
    """
    # Check if the account exists
    account_row = account_data[account_data["id"] == account_id]
    if account_row.empty:
        return jsonify({"error": "Account not found"}), 404

    account_name = account_row.iloc[0]["name"]

    # Retrieve stocks owned by the account
    stock_rows = stocks_owned_data[stocks_owned_data["account_id"] == account_id]
    stock_holdings = []
    for _, row in stock_rows.iterrows():
        stock_holdings.append({
            "symbol": row["symbol"],
            "purchase_date": row["purchase_date"],
            "sale_date": row["sale_date"],
            "number_of_shares": row["number_of_shares"]
        })

    response = {
        "account_id": account_id,
        "name": account_name,
        "stock_holdings": stock_holdings
    }

    return jsonify(response), 200

# Register route for getting account stocks
@app.route("/api/v3/accounts/<account_id>", methods=["GET"])
@authenticate_request
def account_stocks(account_id):
    return get_account_stocks(account_id)

if __name__ == "__main__":
    app.run(debug=True)


def get_account_data():
    """Returns a list of all accounts

    Returns:
    { 'account_id' : INT, 'name' : str}
    """
    accounts = account_data["id"].tolist()
    names = account_data["name"].tolist()
    if not accounts:
        return jsonify([]), 200

    account_list = [{"account_id": acc_id, "name": name} for acc_id, name in zip(accounts, names)]
    return jsonify(account_list), 200


def add_account():
    """Creates a new account

    Returns:
    { 'account_id' : INT, 'name' : str}
    """
    try:
        data = request.get_json()
        name = data.get("name")

        # Validate required fields
        if not name:
            return jsonify({"error": "Name is required"}), 400

        if name in account_data["name"].tolist():
            return jsonify({"error": "Name already exists"}), 409

        # Add account
        account_id = len(account_data) + 1  # Simulating auto-increment ID for example
        new_account = {"id": account_id, "name": name}
        account_data.append(new_account)

        return jsonify({'account_id': account_id}), 201

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    
def delete_account():
    """Deletes an account and all associated stocks

    Returns:
    { 'account_id' : INT }
    """
    try:
        data = request.get_json()
        account_id = data.get("account_id")

        # Validate account existence
        if account_id not in account_data["id"].tolist():
            return jsonify({"error": "Account not found"}), 404

        # Delete account and associated stocks
        account_data.drop(account_data[account_data["id"] == account_id].index, inplace=True)
        stocks_owned_data.drop(stocks_owned_data[stocks_owned_data["account_id"] == account_id].index, inplace=True)

        return jsonify({'account_id': account_id}), 204

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

def get_account_stocks(account_id):
    """Returns all stocks owned by the account

    Parameters:
    account_id (int): The account ID to retrieve stocks for

    Returns:
    JSON response with account details and stock holdings
    """
    # Check if the account exists
    account_row = account_data[account_data["id"] == account_id]
    if account_row.empty:
        return jsonify({"error": "Account not found"}), 404

    account_name = account_row.iloc[0]["name"]

    # Retrieve stocks owned by the account
    stock_rows = stocks_owned_data[stocks_owned_data["account_id"] == account_id]
    stock_holdings = []
    for _, row in stock_rows.iterrows():
        stock_holdings.append({
            "symbol": row["symbol"],
            "purchase_date": row["purchase_date"],
            "sale_date": row["sale_date"],
            "number_of_shares": row["number_of_shares"]
        })

    response = {
        "account_id": account_id,
        "name": account_name,
        "stock_holdings": stock_holdings
    }

    return jsonify(response), 200


def register_routes3(app):
    """Registers Part 3 Routes"""

    @app.route("/api/v3/accounts", methods=["GET", "POST","DELETE"])
    @authenticate_request
    def accounts_op():

        if request.method == "GET":
            get_account_data()


        if requests.method == "POST":
            add_account()







