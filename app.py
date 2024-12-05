"""Initiates flask app and stock_app routes"""

from flask import Flask

from stock_app.api.accounts_management.routes import register_routes3
from stock_app.api.backtesting.routes import register_routes4
from stock_app.api.basic_stocks.routes import register_routes1
from stock_app.api.stock_price.routes import register_routes2


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)

    register_routes1(app)
    register_routes2(app)
    register_routes3(app)
    register_routes4(app)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4000, debug=True)
