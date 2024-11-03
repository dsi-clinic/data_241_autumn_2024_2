"""Tests Flask server against requests"""

import logging
import os
from functools import wraps

from flask import abort, request


def authenticate_request(f):
    """Decorator to authenticate the API request.

    Args:
        f (function): The function to be decorated.

    Returns:
        function: The decorated function.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get("DATA-241-API-KEY")
        expected_api_key = os.environ.get("DATA_241_API_KEY")

        if not api_key or api_key != expected_api_key:
            logging.warning("Unauthorized access attempt.")
            abort(401, description="Unauthorized: Invalid or missing API key.")

        return f(*args, **kwargs)

    return decorated_function
