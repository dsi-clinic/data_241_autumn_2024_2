"""Tests Flask server against requests"""

import logging
import os
from functools import wraps
import time
from stock_app.api.logger_utils.custom_logger import custom_logger
from flask import abort, request, Response

def log_route(func):
    """
    Decorator to log route details, including response time, request/response details, and status codes.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()

        # Log request details
        custom_logger.debug(
            f"Request: Path={request.path}, Method={request.method}, "
            f"Headers={dict(request.headers)}, Body={request.get_data(as_text=True)}"
        )

        # Execute the route function
        response = func(*args, **kwargs)

        # Handle tuple or Response
        if isinstance(response, tuple):
            response_body, status_code = response
            if not isinstance(response_body, Response):  # Handle non-Response bodies
                response_obj = Response(response_body, status=status_code)
            else:
                response_obj = response_body
        else:
            response_obj = response  # Assume it's already a Response object

        # Calculate duration
        duration = time.time() - start_time
        custom_logger.debug(f"Response Time: {duration:.2f} seconds")

        # Log response details
        custom_logger.debug(
            f"Response: Status={response_obj.status_code}, Body={response_obj.get_data(as_text=True)}"
        )

        # Log non-2xx responses
        if response_obj.status_code >= 300:
            custom_logger.info(
                f"Non-2xx Response: Path={request.path}, Status={response_obj.status_code}"
            )

        return response

    return wrapper


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

        if not api_key:
            custom_logger.warning(f"Missing API key for route {request.path}.")
            abort(401, description="Missing API key.")
        elif api_key != expected_api_key:
            custom_logger.warning(f"Invalid API key for route {request.path}.")
            abort(401, description="Unauthorized: Invalid API key.")

        return f(*args, **kwargs)

    return decorated_function
