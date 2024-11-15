"""Tests Flask server against requests"""

import os

import requests


def make_get_request(endpoint, api_key):
    """Sends GET request with API key to specified Flask API endpoint.

    Args:
        endpoint (str): The API endpoint to send the GET request to.
        api_key (str): The API key to authenticate the request.

    Returns:
        response (requests.Response):
        The response object from the GET request if successful

        otherwise:
        None if an error occurs.
    """
    # Base URL for the Flask app running in Docker

    base_url = "http://127.0.0.1:4000"
    full_url = base_url + endpoint

    # Define the request headers
    headers = {
        "DATA-241-API-KEY": api_key,  # API key included in the header
        "Content-Type": "application/json",
    }

    try:
        # Send the GET request
        response = requests.get(full_url, headers=headers)

        # Raise an HTTPError for bad responses (4xx and 5xx)
        response.raise_for_status()

        # Print the response status code
        print("Status Code:" + str(response.status_code))

        # Print the response content in JSON format
        print("Response Content:")
        print(response.json())  # Corrected to properly handle JSON response

        return response

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred: {req_err}")
    except Exception as err:
        print(f"An error occurred: {err}")

    return None




def make_post_request(endpoint, json, api_key):
    """Sends POST request with API key to specified Flask API endpoint.

    Args:
        endpoint (str): The API endpoint to send the POST request to.
        json (object): Object to post across
        api_key (str): The API key to authenticate the request.

    Returns:
        response (requests.Response):
        The response object from the GET request if successful

        otherwise:
        None if an error occurs.
    """
    # Base URL for the Flask app running in Docker

    base_url = "http://127.0.0.1:4000"
    full_url = base_url + endpoint

    # Define the request headers
    headers = {
        "DATA-241-API-KEY": api_key,  # API key included in the header
        "Content-Type": "application/json",
    }

    try:
        #https://www.w3schools.com/PYTHON/ref_requests_post.asp
        # Send the POST request
        response = requests.post(full_url, json, headers=headers)

        # Raise an HTTPError for bad responses (4xx and 5xx)
        response.raise_for_status()

        # Print the response status code
        print("Status Code:" + str(response.status_code))

        # Print the response content in JSON format
        print("Response Content:")
        print(response.json())  # Corrected to properly handle JSON response

        return response

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred: {req_err}")
    except Exception as err:
        print(f"An error occurred: {err}")

    return None


def make_delete_request(endpoint, json, api_key):
    """Sends DELETE request with API key to specified Flask API endpoint.

    Args:
        endpoint (str): The API endpoint to send the POST request to.
        json (object): Object to delete
        api_key (str): The API key to authenticate the request.

    Returns:
        response (requests.Response):
        The response object from the GET request if successful

        otherwise:
        None if an error occurs.
    """
    # Base URL for the Flask app running in Docker

    base_url = "http://127.0.0.1:4000"
    full_url = base_url + endpoint

    # Define the request headers
    headers = {
        "DATA-241-API-KEY": api_key,  # API key included in the header
        "Content-Type": "application/json",
    }

    try:
        #https://www.geeksforgeeks.org/delete-method-python-requests/
        # Send the POST request
        response = requests.delete(full_url, json, headers=headers)
        # Raise an HTTPError for bad responses (4xx and 5xx)
        response.raise_for_status()

        # Print the response status code
        print("Status Code:" + str(response.status_code))

        # Print the response content in JSON format
        print("Response Content:")
        print(response.json())  # Corrected to properly handle JSON response

        return response

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred: {req_err}")
    except Exception as err:
        print(f"An error occurred: {err}")

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

    if not api_key:
        print("Error: The DATA_241_API_KEY environment variable is not set.")
    else:
        # Testing v2 functions
        # Add string endpoint to test

        """
        # V1, V2 Endpoints
        get_list_endpoint = ["/api/v1/row_by_market_count",
            "/api/v2/2019",
            "/api/v2/open/AAPL",
            "/api/v2/close/AAPL",
            "/api/v2/high/AAPL",
            "/api/v2/low/AAPL",]
        
        """

        #V3 STUFF ADDED
        get_list_endpoint = [
            "/api/v3/accounts",
            "/api/v3/accounts/1",
             "/api/v3/accounts/return/1",
            "/api/v3/stocks/AAPL",
        ]
        

        post_list_endpoint = [
        ("/api/v3/accounts", { 'name' : 'Disha' }),
        ("/api/v3/stocks", { 'account_id' : 1, 'symbol': 'AAPL', 'purchase_date' : "2001/10/10", 'sale_date': "2001/11/10", 'number_of_shares': 10}),
        ]


        delete_list_endpoint = [
        ("/api/v3/accounts", { 'account_id' : 1 }),
        ("/api/v3/stocks", { 'account_id' : 1, 'symbol': 'AAPL', 'purchase_date' : "2001/10/10", 'sale_date': "2001/11/10", 'number_of_shares': 10}),
        ]

        for endpoint in get_list_endpoint:
            make_get_request(endpoint, api_key)
        for endpoint in post_list_endpoint:
            make_post_request(endpoint[0],endpoint[1], api_key)
        for endpoint in delete_list_endpoint:
            make_delete_request(endpoint[0],endpoint[1], api_key)
       