import os
import pandas as pd
import zipfile
from flask import Flask, jsonify, request, abort

app = Flask(__name__)

def mergedaily(zippath):
  """
  Input:
  Zippath: path to zip file

  Process:
  1. Unzips file in Zip file object
  2. Gets a list of csv files within the zip file
  3. Makes the DF using the first csv as the template
  4. Loops through the csv files and appends to the template
  5. Appends either NASDAQ or NYSE at the end


  Output:
  Merged dataframe containing merged CSV data from zip file
  """

  zf = zipfile.ZipFile(zippath)
  zflist = zf.namelist()
  zfdf = pd.read_csv(zf.open(zflist[0]))
  for csv in zf.namelist()[1:]:
    mergedf = pd.read_csv(zf.open(csv))
    zfdf = pd.concat([zfdf, mergedf],
                          ignore_index = True,
                          sort = False)
  if 'NASDAQ' in zippath:
    zfdf['market'] = 'NASDAQ'
  elif 'NYSE' in zippath:
    zfdf['market'] = 'NYSE'
  else:
    zfdf['market'] = 'Not NYSE or NASDAQ'

  return zfdf

# Load data from zip file without storing intermediate files
def load_stock_data():
    try:
        pathone = './data/raw_data/NASDAQ_2019.zip'
        pathtwo = './data/raw_data/NYSE_2019.zip'

        nasdaqdf = mergedaily(pathone)  # Ensure mergedaily returns a DataFrame
        nysedf = mergedaily(pathtwo)
        combineddf = pd.concat([nasdaqdf, nysedf], ignore_index=True, sort=False)

        return combineddf
    except Exception as e:
        print(f"Error loading stock data: {e}")
        return pd.DataFrame()  # Return an empty DataFrame in case of error

# Ensure the API key matches the environment variable
def authenticate_request():
    api_key = request.headers.get('DATA-241-API-KEY')
    expected_api_key = os.environ.get('DATA_241_API_KEY')

    if not api_key or api_key != expected_api_key:
        abort(401)

# Load the data once globally when the app starts
stock_data = load_stock_data()

@app.route('/api/v1/row_count', methods=['GET'])
def row_count():
    authenticate_request()
    row_count = len(stock_data)
    return jsonify({'row_count': row_count})

@app.route('/api/v1/unique_stock_count', methods=['GET'])
def unique_stock_count():
    authenticate_request()
    if 'stock_symbol' not in stock_data.columns:
        return jsonify({'error': 'Missing stock symbol data'}), 400

    unique_stocks = stock_data['stock_symbol'].nunique()
    return jsonify({'unique_stock_count': unique_stocks})

@app.route('/api/v1/row_by_market_count', methods=['GET'])
def row_by_market_count():
    authenticate_request()
    if 'market' not in stock_data.columns:
        return jsonify({'error': 'Missing market data'}), 400

    market_counts = stock_data['market'].value_counts().to_dict()
    return jsonify({'NYSE': market_counts.get('NYSE', 0), 'NASDAQ': market_counts.get('NASDAQ', 0)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000)
