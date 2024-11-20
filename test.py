"""Tests Flask server against requests."""

import os

import requests


def make_get_request(endpoint: str, api_key: str):
    """Sends a GET request to a specified endpoint.

    Args:
        endpoint (str): API endpoint to send the request to.
        api_key (str): API key for authentication.

    Returns:
        requests.Response: The response object from the GET request.
    """
    base_url = "http://127.0.0.1:4000"
    full_url = base_url + endpoint
    headers = {
        "DATA-241-API-KEY": api_key,
        "Content-Type": "application/json",
    }

    try:
        response = requests.get(full_url, headers=headers)
        response.raise_for_status()
        print("Status Code:", response.status_code)
        try:
            print("Response Content:", response.json())
        except ValueError:
            print("Response Content is not valid JSON.")
        return response
    except requests.exceptions.RequestException as err:
        print(f"Error: {err}")
        return None


def make_post_request(endpoint: str, json_data: dict, api_key: str):
    """Sends a POST request to a specified endpoint with JSON data.

    Args:
        endpoint (str): API endpoint to send the request to.
        json_data (dict): Data to include in the POST request body.
        api_key (str): API key for authentication.

    Returns:
        requests.Response: The response object from the POST request.
    """
    base_url = "http://127.0.0.1:4000"
    full_url = base_url + endpoint
    headers = {
        "DATA-241-API-KEY": api_key,
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(full_url, json=json_data, headers=headers)
        response.raise_for_status()
        print("Status Code:", response.status_code)
        try:
            print("Response Content:", response.json())
        except ValueError:
            print("Response Content is not valid JSON.")
        return response
    except requests.exceptions.RequestException as err:
        print(f"Error: {err}")
        return None


def make_delete_request(endpoint: str, json_data: dict, api_key: str):
    """Sends a DELETE request to a specified endpoint with JSON data.

    Args:
        endpoint (str): API endpoint to send the request to.
        json_data (dict): Data to include in the DELETE request body.
        api_key (str): API key for authentication.

    Returns:
        requests.Response: The response object from the DELETE request.
    """
    base_url = "http://127.0.0.1:4000"
    full_url = base_url + endpoint
    headers = {
        "DATA-241-API-KEY": api_key,
        "Content-Type": "application/json",
    }

    try:
        response = requests.delete(full_url, json=json_data, headers=headers)
        response.raise_for_status()
        print("Status Code:", response.status_code)
        try:
            print("Response Content:", response.json())
        except ValueError:
            print("Response Content is not valid JSON.")
        return response
    except requests.exceptions.RequestException as err:
        print(f"Error: {err}")
        return None


if __name__ == "__main__":
    """
    Main script to test Flask API endpoints.

    Steps:
    1. Retrieves API key from the 'DATA_241_API_KEY' environment variable.
    2. If the API key is missing, prints an error message and exits.
    3. Sends GET requests to various endpoints and displays the responses.
    """
    api_key = os.environ.get("DATA_241_API_KEY")

    if not api_key:
        print("Error: The DATA_241_API_KEY environment variable is not set.")
    else:
        # Version 1 Endpoints
        make_get_request("/api/v1/row_by_market_count", api_key)
        make_get_request("/api/v1/row_count", api_key)
        make_get_request("/api/v1/unique_stock_count", api_key)

        # Version 2 Endpoints
        make_get_request("/api/v2/2019", api_key)
        make_get_request("/api/v2/Open/AAPL", api_key)

