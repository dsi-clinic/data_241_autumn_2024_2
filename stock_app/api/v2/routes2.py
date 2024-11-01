"""Flask Routes for project part 2"""

import logging
import zipfile
from os import listdir

import pandas as pd
from flask import Blueprint, jsonify

from stock_app.api.route_utils.decorators import authenticate_request

# Initialize API Blueprint
api_v2_bp = Blueprint("api_v2", __name__)

# Configure logging
logging.basicConfig(level=logging.INFO)


def merge_daily_stock_data(zip_path):
    """Merges all CSV files within a given zip file into a single DataFrame.

    Args:
        zip_path (str): Path to the zip file containing stock data.

    Returns:
        pd.DataFrame: Merged DataFrame with all CSVs appended.
    """
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            file_list = zf.namelist()
            data = pd.read_csv(zf.open(file_list[0]))

            for csv_file in file_list[1:]:
                temp_df = pd.read_csv(zf.open(csv_file))
                data = pd.concat(
                    [data, temp_df], ignore_index=True, sort=False
                )

            # Add 'market' column based on file name
            if "NASDAQ" in zip_path:
                data["market"] = "NASDAQ"
            elif "NYSE" in zip_path:
                data["market"] = "NYSE"
            else:
                data["market"] = "Unknown"

        return data
    except zipfile.BadZipFile:
        logging.error(f"Invalid zip file: {zip_path}")
        raise ValueError(f"Invalid zip file: {zip_path}") from None
    except Exception as e:
        logging.error(f"Error merging data from {zip_path}: {e}")
        raise RuntimeError(f"Error merging data: {e}") from None


def load_all_stock_data():
    """Loads stock data from all zip files.

    Returns:
        pd.DataFrame: Combined DataFrame of stock data.
    """
    try:
        combined_df = pd.DataFrame()
        data_path = "./data/raw_data/"
        all_files = [
            "./data/raw_data/" + f
            for f in listdir(data_path)
            if (data_path + str(f)).is_file()
        ]

        for path in all_files:
            logging.info(f"Loading {path.split('/')[-1]} data...")
            year_df = merge_daily_stock_data(path)
            combined_df = pd.concat([combined_df, year_df], ignore_index=True)

        return combined_df
    except Exception as e:
        logging.error(f"Error loading stock data: {e}")
        raise RuntimeError(f"Error loading stock data: {e}") from None


# Load stock data
try:
    stock_data = load_all_stock_data()
except Exception as e:
    logging.error(f"Failed to load stock data: {e}")
    stock_data = pd.DataFrame()


@authenticate_request
@api_v2_bp.route("/api/v2/<YEAR>", methods=["GET"])
def count_year(YEAR):
    """Returns the number of rows for a specific year in the stock data.

    Returns:
        JSON: { 'year': <YEAR>, 'count': <row_count> }
        or JSON: {'error': 'Year not found in the data'}
    """
    row_count = len(stock_data[stock_data["Date"].str.contains(str(YEAR))])

    if row_count == 0:
        return jsonify({"error": "Year not found in the data"}), 404
    return jsonify({"year": int(YEAR), "count": row_count})


@authenticate_request
@api_v2_bp.route("/api/v2/open/<SYMBOL>", methods=["GET"])
def open_prices(SYMBOL):
    """Returns open prices for a specific stock symbol.

    Returns:
        JSON: { 'symbol': <SYMBOL>, 'price_info': <list_of_prices> }
        or JSON: {'error': 'Symbol not found in the data'}
    """
    return get_prices(SYMBOL, "Open")


@authenticate_request
@api_v2_bp.route("/api/v2/close/<SYMBOL>", methods=["GET"])
def close_prices(SYMBOL):
    """Returns close prices for a specific stock symbol.

    Returns:
        JSON: { 'symbol': <SYMBOL>, 'price_info': <list_of_prices> }
        or JSON: {'error': 'Symbol not found in the data'}
    """
    return get_prices(SYMBOL, "Close")


@authenticate_request
@api_v2_bp.route("/api/v2/high/<SYMBOL>", methods=["GET"])
def high_prices(SYMBOL):
    """Returns high prices for a specific stock symbol.

    Returns:
        JSON: { 'symbol': <SYMBOL>, 'price_info': <list_of_prices> }
        or JSON: {'error': 'Symbol not found in the data'}
    """
    return get_prices(SYMBOL, "High")


@authenticate_request
@api_v2_bp.route("/api/v2/low/<SYMBOL>", methods=["GET"])
def low_prices(SYMBOL):
    """Returns low prices for a specific stock symbol.

    Returns:
        JSON: { 'symbol': <SYMBOL>, 'price_info': <list_of_prices> }
        or JSON: {'error': 'Symbol not found in the data'}
    """
    return get_prices(SYMBOL, "Low")


def get_prices(symbol, price_type):
    """Helper function to get price information for a specific stock symbol.

    Args:
        symbol (str): Stock symbol to lookup.
        price_type (str): Type of price ('Open', 'Close', 'High', 'Low').

    Returns:
        JSON: { 'symbol': <SYMBOL>, 'price_info': <list_of_prices> }
              or JSON: {'error': 'Symbol not found in the data'}
    """
    if symbol not in stock_data["Symbol"].unique():
        return jsonify({"error": "Symbol not found in the data"}), 404

    symbol_df = stock_data[stock_data["Symbol"] == symbol]
    price_info = symbol_df[["Date", price_type]].to_dict(orient="records")
    return jsonify({"symbol": symbol, "price_info": price_info})
