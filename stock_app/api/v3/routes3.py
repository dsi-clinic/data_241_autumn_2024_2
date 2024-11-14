"""Flask Routes"""

import logging
import pandas as pd
from flask import jsonify
from stock_app.api.data_utils.loading_utils import load_stock_data, load_account_data, load_stocks_owned_data#ADDED NEW LOADING FUNCTIONS
from stock_app.api.route_utils.decorators import authenticate_request



# Configure logging
logging.basicConfig(level=logging.INFO)

# Load stock data
try:
    stock_data = load_stock_data()
    account_data = load_account_data()
    stocks_owned_data = load_stocks_owned_data()
    # Ensure columns are consistently lowercase
    stock_data.columns = stock_data.columns.str.lower()
except Exception as e:
    logging.error(f"Failed to load stock data: {e}")



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

      # Validate required fields
      if data.get("name") in account_data["name"].tolist():
        return jsonify({"error": "name already exists"}), 409

      # Add account
      add_account(data)

      return jsonify({'account_id': account_data }), 201

    except Exception as e:
      return jsonify({"error": f"An error occurred: {str(e)}"}), 500



def register_routes3(app):
    """Registers Part 3 Routes"""

    @app.route("/api/v3/accounts", methods=["GET", "POST","DELETE"])
    @authenticate_request
    def accounts_op():

        if request.method == "GET":
            get_account_data()


        if requests.method == "POST":
            add_account()







