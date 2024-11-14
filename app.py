"""Initiates flask app and stock_app routes"""

from flask import Flask

from stock_app.api.v1.routes1 import register_routes1
from stock_app.api.v2.routes2 import register_routes2
from stock_app.api.v3.routes3 import register_routes3

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)

    register_routes1(app)
    register_routes2(app)
    register_routes3(app) #ADDED THIS

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4000, debug=True)
