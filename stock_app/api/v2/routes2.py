import os
import pandas as pd
import logging
import zipfile
from flask import jsonify, request, abort, Blueprint
from os import listdir
from os.path import isfile, join

from stock_app.api.route_utils.decorators import authenticate_request


api_v2_bp = Blueprint('api_v2', __name__)

logging.basicConfig(level=logging.INFO)

def merge_daily_stock_data(zip_path):
    """
    Merges all CSV files within a given zip file into a single DataFrame.
    
    Args:
        zip_path (str): Path to the zip file containing stock data.

    Returns:
        pd.DataFrame: Merged DataFrame with all CSVs appended.
    """
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            file_list = zf.namelist()
            df = pd.read_csv(zf.open(file_list[0]))

            for csv_file in file_list[1:]:
                temp_df = pd.read_csv(zf.open(csv_file))
                df = pd.concat([df, temp_df], ignore_index=True, sort=False)
                
            # Add 'market' column based on file name
            if 'NASDAQ' in zip_path:
                df['market'] = 'NASDAQ'
            elif 'NYSE' in zip_path:
                df['market'] = 'NYSE'
            else:
                df['market'] = 'Unknown'

        return df
    except zipfile.BadZipFile:
        logging.error(f"Invalid zip file: {zip_path}")
        raise ValueError(f"Invalid zip file: {zip_path}")
    except Exception as e:
        logging.error(f"Error merging data from {zip_path}: {e}")
        raise RuntimeError(f"Error merging data: {e}")

def load_all_stock_data():
    """
    Loads stock data from all available zip files without storing intermediate files.

    Returns:
        pd.DataFrame: Combined DataFrame of stock data.
    """
    try:
        combined_df = pd.DataFrame()
        all_files = ['./data/raw_data/' + f for f in listdir('./data/raw_data/') if isfile(join('./data/raw_data/', f))]

        for path in all_files:
            logging.info(f"Loading {path.split('/')[-1]} data...")
            year_df = merge_daily_stock_data(path)
            combined_df = pd.concat([combined_df, year_df], ignore_index=True)

        return combined_df
    except Exception as e:
        logging.error(f"Error loading stock data: {e}")
        raise RuntimeError(f"Error loading stock data: {e}")

try:
    stock_data = load_all_stock_data()
except Exception as e:
    logging.error(f"Failed to load stock data: {e}")
    stock_data = pd.DataFrame()


@authenticate_request
@api_v2_bp.route('/api/v2/<YEAR>', methods=['GET'])
def count_year(YEAR):
    """
    Returns the number of rows for a specific year in the stock data.
    Returns:
        JSON: { 'year': <YEAR>, 'count': <row_count> }
        or JSON: {'error': 'Year not found in the data'}
    """
    row_count = len(stock_data[stock_data['Date'].str.contains(YEAR)])
    
    if row_count == 0:
        return jsonify({'error': 'Year not found in the data'}), 404
    else:
        return jsonify({'year': int(YEAR), 'count': row_count})

@authenticate_request
@api_v2_bp.route('/api/v2/open/<SYMBOL>', methods=['GET'])
def open_prices(SYMBOL):
    """
    Returns open prices for a specific stock symbol.
    Returns:
        JSON: { 'symbol': <SYMBOL>, 'price_info': <list_of_prices> }
        or JSON: {'error': 'Symbol not found in the data'}
    """
    

    if SYMBOL not in stock_data['Symbol'].unique():
        return jsonify({'error': 'Symbol not found in the data'}), 404
    
    symbol_df = stock_data[stock_data['Symbol'] == SYMBOL]
    open_prices = symbol_df[['Date', 'Open']].to_dict(orient='records')
    return jsonify({'symbol': SYMBOL, 'price_info': open_prices})

@authenticate_request
@api_v2_bp.route('/api/v2/close/<SYMBOL>', methods=['GET'])
def close_prices(SYMBOL):
    """
    Returns close prices for a specific stock symbol.
    """

    if SYMBOL not in stock_data['Symbol'].unique():
        return jsonify({'error': 'Symbol not found in the data'}), 404
    
    symbol_df = stock_data[stock_data['Symbol'] == SYMBOL]
    close_prices = symbol_df[['Date', 'Close']].to_dict(orient='records')
    return jsonify({'symbol': SYMBOL, 'price_info': close_prices})

@authenticate_request
@api_v2_bp.route('/api/v2/high/<SYMBOL>', methods=['GET'])
def high_prices(SYMBOL):
    """
    Returns high prices for a specific stock symbol.
    """


    if SYMBOL not in stock_data['Symbol'].unique():
        return jsonify({'error': 'Symbol not found in the data'}), 404
    
    symbol_df = stock_data[stock_data['Symbol'] == SYMBOL]
    high_prices = symbol_df[['Date', 'High']].to_dict(orient='records')
    return jsonify({'symbol': SYMBOL, 'price_info': high_prices})

@authenticate_request
@api_v2_bp.route('/api/v2/low/<SYMBOL>', methods=['GET'])
def low_prices(SYMBOL):
    """
    Returns low prices for a specific stock symbol.
    """


    if SYMBOL not in stock_data['Symbol'].unique():
        return jsonify({'error': 'Symbol not found in the data'}), 404
    
    symbol_df = stock_data[stock_data['Symbol'] == SYMBOL]
    low_prices = symbol_df[['Date', 'Low']].to_dict(orient='records')
    return jsonify({'symbol': SYMBOL, 'price_info': low_prices})

