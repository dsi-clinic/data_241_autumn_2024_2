"""Provide utility decorators for logging and authentication in the API."""

import os
from functools import wraps

from flask import Response, abort, request

from stock_app.api.logger_utils.custom_logger import custom_logger

# Define constant for non-2xx response threshold
NON_2XX_THRESHOLD = 300


def log_route(func):
    """Decorator to log route details.

    Logs response time, request/response details, and status codes.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        custom_logger.debug(
            "Request: "
            f"Path={request.path}, Method={request.method}, "
            f"Headers={dict(request.headers)}, "
            f"Body={request.get_data(as_text=True)}"
        )

        response = func(*args, **kwargs)

        if isinstance(response, tuple):
            response_body, status_code = response
            if not isinstance(response_body, Response):  
                response_obj = Response(response_body, status=status_code)
            else:
                response_obj = response_body
        else:
            response_obj = response

        custom_logger.debug(
            "Response: "
            f"Status={response_obj.status_code}, "
            f"Body={response_obj.get_data(as_text=True)}"
        )

        if response_obj.status_code >= NON_2XX_THRESHOLD:
            custom_logger.info(
                "Non-2xx Response: "
                f"Path={request.path}, Status={response_obj.status_code}"
            )

        return response_obj

    return wrapper


def authenticate_request(func):
    """Decorator to authenticate API requests.

    Verifies the presence of a valid API key in the request headers.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        api_key = request.headers.get("DATA-241-API-KEY")
        expected_api_key = os.environ.get("DATA_241_API_KEY")

        if not api_key:
            custom_logger.warning(
                f"Missing API key for route {request.path}."
            )
            abort(401, description="Missing API key.")
        elif api_key != expected_api_key:
            custom_logger.warning(
                f"Invalid API key for route {request.path}."
            )
            abort(401, description="Unauthorized: Invalid API key.")

        return func(*args, **kwargs)

    return wrapper
