import os
import pandas as pd
import zipfile
from flask import Flask, jsonify, request, abort

app = Flask(__name__)

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
        raise ValueError(f"Invalid zip file: {zip_path}")
    except Exception as e:
        raise RuntimeError(f"Error merging data: {e}")

def load_stock_data():
    """
    Loads stock data from NASDAQ and NYSE zip files without storing intermediate files.
    
    Returns:
        pd.DataFrame: Combined DataFrame of NASDAQ and NYSE stock data.
    """
    try:
        nasdaq_zip_path = os.environ.get('NASDAQ_ZIP_PATH', './data/raw_data/NASDAQ_2019.zip')
        nyse_zip_path = os.environ.get('NYSE_ZIP_PATH', './data/raw_data/NYSE_2019.zip')

        nasdaq_df = merge_daily_stock_data(nasdaq_zip_path)
        nyse_df = merge_daily_stock_data(nyse_zip_path)
        
        combined_df = pd.concat([nasdaq_df, nyse_df], ignore_index=True, sort=False)
        return combined_df
    except Exception as e:
        raise RuntimeError(f"Error loading stock data: {e}")

def authenticate_request():
    """
    Authenticates the API request by checking the API key in the request header.

    Raises:
        401 Unauthorized: If the API key is missing or invalid.
    """
    api_key = request.headers.get('DATA-241-API-KEY')
    expected_api_key = os.environ.get('DATA_241_API_KEY')

    if not api_key or api_key != expected_api_key:
        abort(401, description="Unauthorized: Invalid or missing API key.")

# Load the stock data once when the app starts
stock_data = load_stock_data()

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
        return jsonify({'error': 'Missing market data'}), 400

    market_counts = stock_data['market'].value_counts().to_dict()
    return jsonify({'NYSE': market_counts.get('NYSE', 0), 'NASDAQ': market_counts.get('NASDAQ', 0)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000)
