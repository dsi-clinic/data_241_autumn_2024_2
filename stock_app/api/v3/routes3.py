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

def get_stock_data(symbol):
    """Returns all stock_data

    Returns:
    { 'symbol': str, 'holdings': [{'account_id' : int, 'purchase_date' : str, 'sale_date' : str, 'number_of_shares': int }, ...]}

    """
    create_stocks_owned = """
    CREATE TABLE stocks_owned (
    account_id INTEGER,
    symbol TEXT NOT NULL,
    purchase_date DATE NOT NULL,
    sale_date DATE NOT NULL,
    number_of_shares INTEGER NOT NULL,)"""

    package = {}
    holding = []

    symbol_data = stocks_owned_data[stocks_owned_data["symbol"] == symbol]

    if symbol_data.empty:
        return jsonify([]), 200

    account_ids = symbol_data["account_id"].tolist()
    purchase_dates = symbol_data["purchase_date"].tolist()
    sale_dates = symbol_data["sale_date"].tolist()
    number_of_shares = symbol_data["number_of_shares"].tolist()

    for i in range(len(account_ids)):
        holding.append({
            "account_id": account_ids[i],
            "purchase_date": purchase_dates[i],
            "sale_date": sale_dates[i],
            "number_of_shares": number_of_shares[i]
        })

    package["symbol"] = str(symbol)
    package["holdings"] = holding

    return jsonify(package), 200




def add_stock_data():
    """Creates a new stock_data

    Returns:
    { 'symbol': str, 'holdings': [{'account_id' : int, 'purchase_date' : str, 'sale_date' : str, 'number_of_shares': int }, ...]}

    """
    trading_days = stock_data['date'].tolist()
    try:
      data = request.get_json()

      # Validate required fields
      if data.get("sale_date") not in trading_days:
        return jsonify({"error": "Not a trading day"}), 400

      # Add account
      add_stocks_data(
          data
          )

      return 201

    except Exception as e:
      return jsonify({"error": f"An error occurred: {str(e)}"}), 500

def delete_stock_data():
    """Deletes a stock_data

    Returns:
    { 'symbol': str, 'holdings': [{'account_id' : int, 'purchase_date' : str, 'sale_date' : str, 'number_of_shares': int }, ...]}

    """
    try:
      data = request.get_json()

      target = stocks_owned_data[(stocks_owned_data["account_id"] == data["account_id"]) & (stocks_owned_data["symbol"] == data["symbol"]) & (stocks_owned_data["purchase_date"] == data["purchase_date"]) & (stocks_owned_data["sale_date"] == data["sale_date"]) & (stocks_owned_data["number_of_shares"] == data["number_of_shares"])]
      # Validate required fields
      if target.empty:
        return 404

      else:
        remove_stocks_data(
            data
            )
      return 200

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

    @app.route("/api/v3/stocks/<symbol>", methods=["GET"])
    @authenticate_request
    def stock_data_op_get():

        if request.method == "GET":
            get_stock_data(symbol)


    @app.route("/api/v3/stocks", methods=["POST","DELETE"])
    @authenticate_request
    def stock_data_op_post_del():

        if requests.method == "POST":
            add_stock_data()


        if requests.method == "DELETE":
            delete_stock_data()


    @app.route("/api/v3/accounts/return/<int:account_id>", methods=["GET"])
    @authenticate_request
    def calculate_account_nominal_return(account_id):
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
        

         # Ensure account exists
        if account_id not in account_data["id"].tolist():
            return jsonify({"error": "Account not found"}), 404

        # Filter holdings for the account
        account_holdings = stocks_owned_data[stocks_owned_data["account_id"] == account_id]

        if account_holdings.empty:
            # If no holdings, return 0.0
            return jsonify({"account_id": account_id, "return": 0.0}), 200

        total_return = 0.0

        for _, holding in account_holdings.iterrows():
            symbol = holding["symbol"]
            purchase_date = holding["purchase_date"]
            sale_date = holding["sale_date"]
            num_shares = holding["number_of_shares"]

            open_price = stock_data.loc[
                (stock_data["symbol"] == symbol) & (stock_data["date"] == purchase_date), "open"
            ].values[0]
            close_price = stock_data.loc[
                (stock_data["symbol"] == symbol) & (stock_data["date"] == sale_date), "close"
            ].values[0]

            # Calculate return for this holding
            total_return += num_shares * (close_price - open_price)

        return jsonify({"account_id": account_id, "return": total_return}), 200









