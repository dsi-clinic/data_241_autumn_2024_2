import logging
from flask import Flask, jsonify, request, abort

from stock_app.api.v1.routes1 import merge_daily_stock_data
from stock_app.api.v1.routes import load_stock_data
from stock_app.api.v1.routes import authenticate_request # Need to make this decorator
from stock_app.api.v1.routes import get_row_count
from stock_app.api.v1.routes import get_unique_stock_count
from stock_app.api.v1.routes import get_row_by_market_count

from stock_app.api.v2.routes2 import merge_daily_stock_data
from stock_app.api.v2.routes2 import load_all_stock_data
from stock_app.api.v2.routes2 import authenticate_request # Need to make this decorator
from stock_app.api.v2.routes2 import count_year
from stock_app.api.v2.routes2 import open_prices
from stock_app.api.v2.routes2 import close_prices
from stock_app.api.v2.routes2 import high_prices
from stock_app.api.v2.routes2 import low_prices

# Initialize the Flask app
def create_app(config_class):
    app = Flask(__name__)

    # Register routes
    merge_daily_stock_data(app)
    load_stock_data(app)
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000)
