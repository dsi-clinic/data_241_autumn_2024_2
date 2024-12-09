"""Tests Flask server against requests"""

import os
import requests


def make_get_request(endpoint, api_key):
    base_url = "http://127.0.0.1:4000"
    full_url = base_url + endpoint
    headers = {
        "DATA-241-API-KEY": api_key,
        "Content-Type": "application/json",
    }

    try:
        response = requests.get(full_url, headers=headers)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        print("Status Code:", response.status_code)
        try:
            print("Response Content:", response.json())
        except ValueError:
            print("Response Content is not valid JSON.")
        return response
    except requests.exceptions.RequestException as err:
        print(f"Error: {err}")
        return None


def make_post_request(endpoint, json, api_key):
    base_url = "http://127.0.0.1:4000"
    full_url = base_url + endpoint
    headers = {
        "DATA-241-API-KEY": api_key,
        "Content-Type": "application/json",
    }

    try:
        # Send the POST request with json
        response = requests.post(full_url, json=json, headers=headers)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        print("Status Code:", response.status_code)
        try:
            print("Response Content:", response.json())
        except ValueError:
            print("Response Content is not valid JSON.")
        return response
    except requests.exceptions.RequestException as err:
        print(f"Error: {err}")
        return None


def make_delete_request(endpoint, json, api_key):
    base_url = "http://127.0.0.1:4000"
    full_url = base_url + endpoint
    headers = {
        "DATA-241-API-KEY": api_key,
        "Content-Type": "application/json",
    }

    try:
        # Send the DELETE request with json
        response = requests.delete(full_url, json=json, headers=headers)
        response.raise_for_status()  # Raise an HTTPError for bad responses
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
    Main function to make GET requests to a specified Flask API endpoint.

    Process:
    1. Retrieves the API key from environment variable 'DATA_241_API_KEY'
    2. If the API key is not set, it prints an error and exits
    3. Sends a GET request to specified API endpoint displays the response
    """
    # Retrieve API key from environment variable
    api_key = os.environ.get("DATA_241_API_KEY")

    make_get_request("/api/v2/open/INVALID1",api_key)

    make_get_request("/api/v2/close/INVALID2",api_key)

    make_get_request("/api/v2/high/XYZ",api_key)

    make_get_request("/api/v2/low/ABC",api_key)

    '''
    make_post_request("/api/v4/back_test",{
    "value_1" : "O1",
    "value_2" : "C1",
    "operator" : "LT",
    "purchase_type": "B", 
    "start_date": "1999-01-03",
    "end_date": "32423-01-03"
    }, api_key)
    '''
