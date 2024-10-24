import os
import pandas as pd
import zipfile
import logging
from flask import Flask, jsonify, request, abort


from os import listdir
from os.path import isfile, join


logging.basicConfig(level=logging.INFO)


def merge_daily_stock_data(zip_path):
    """
    Merges all CSV files within a given zip file into a single DataFrame.
    
    Args:
        zip_path (str): Path to the zip file containing stock data.

    Returns:
        pd.DataFrame: Merged DataFrame with all CSVs appended, with a 'market' column 
                      indicating NASDAQ or NYSE based on the zip file name.
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



def load_stock_data():
    """
    Loads stock data from NASDAQ and NYSE zip files without storing intermediate files.

    Returns:
        pd.DataFrame: Combined DataFrame of NASDAQ and NYSE stock data.
    """
    try:

        #### Returns combined_df with all of the data
        combined_df = pd.DataFrame()

        all_files = ['./data/raw_data/'+ f for f in listdir('./data/raw_data/') if isfile(join('./data/raw_data/', f))]

        for path in all_files:
            logging.info(f"Loading {path.split('/')[-1]} data...")
            year_df = merge_daily_stock_data(path)
            combined_df = pd.concat([combined_df, year_df], ignore_index=True)
        ####


        return combined_df

    except Exception as e:
        logging.error(f"Error loading stock data: {e}")
        raise RuntimeError(f"Error loading stock data: {e}")


# Load the stock data once when the app starts
try:
    stock_data = load_stock_data()
except Exception as e:
    logging.error(f"Failed to load stock data: {e}")
    stock_data = pd.DataFrame()  # Load an empty dataframe if data fails






# Will need to write decorator for this function!
# Will need a seperate pyfile 

def authenticate_request():
    """
    Authenticates the API request by checking the API key in the request header.

    Raises:
        401 Unauthorized: If the API key is missing or invalid.
    """
    api_key = request.headers.get('DATA-241-API-KEY')
    expected_api_key = os.environ.get('DATA_241_API_KEY')

    if not api_key or api_key != expected_api_key:
        logging.warning("Unauthorized access attempt.")
        abort(401, description="Unauthorized: Invalid or missing API key.")


@app.route('/api/v1/row_count', methods=['GET'])
def get_row_count():
    """
    Returns the total number of rows in the stock data.

    Returns:
        JSON: { 'row_count': <number_of_rows> }
    """
    authenticate_request()
    return jsonify({'row_count': len(stock_data)})




@app.route('/api/v1/unique_stock_count', methods=['GET'])
def get_unique_stock_count():
    """
    Returns the count of unique stocks in the stock data.

    Returns:
        JSON: { 'unique_stock_count': <number_of_unique_stocks> }
    """
    authenticate_request()

    if 'stock_symbol' not in stock_data.columns:
        logging.error("'stock_symbol' column missing in the data.")
        return jsonify({'error': 'Missing stock symbol data'}), 400

    unique_stocks = stock_data['stock_symbol'].nunique()
    return jsonify({'unique_stock_count': unique_stocks})


@app.route('/api/v1/row_by_market_count', methods=['GET'])
def get_row_by_market_count():
    """
    Returns the number of rows for each stock market (NASDAQ, NYSE) in the data.

    Returns:
        JSON: { 'NYSE': <count>, 'NASDAQ': <count> }
    """
    authenticate_request()

    if 'market' not in stock_data.columns:
        logging.error("'market' column missing in the data.")
        return jsonify({'error': 'Missing market data'}), 400

    market_counts = stock_data['market'].value_counts().to_dict()
    return jsonify({'NYSE': market_counts.get('NYSE', 0), 'NASDAQ': market_counts.get('NASDAQ', 0)})



