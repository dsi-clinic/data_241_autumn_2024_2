import logging
from flask import Flask, jsonify, request, abort

from stock_app.api.v2.routes import merge_daily_stock_data
from stock_app.api.v2.routes import load_stock_data
from stock_app.api.v2.routes import get_row_count
from stock_app.api.v2.routes import get_unique_stock_count
from stock_app.api.v2.routes import get_row_by_market_count

# Initialize the Flask app
def create_app(config_class):
    app = Flask(__name__)

    # Register routes
    register_v2_routes(app)
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000)
