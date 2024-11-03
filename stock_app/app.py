"""Initiates flask app and stock_app routes"""

from flask import Flask

from stock_app.api.v1.routes1 import api_v1_bp
from stock_app.api.v2.routes2 import api_v2_bp


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)

    # Register the API blueprints
    app.register_blueprint(api_v1_bp)
    app.register_blueprint(api_v2_bp)

    return app


if __name__ == "__main__":
    app_instance = create_app()
    app_instance.run(host="localhost", port=4000)
