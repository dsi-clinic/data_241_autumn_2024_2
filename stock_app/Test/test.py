import requests
import os

def make_get_request(endpoint, api_key):
    """
    Sends a GET request to the specified Flask API endpoint with the provided API key.

    Args:
        endpoint (str): The API endpoint to send the GET request to.
        api_key (str): The API key to authenticate the request.

    Returns:
        response (requests.Response): The response object from the GET request if successful,
                                      otherwise None if an error occurs.
    """
    # Base URL for the Flask app running in Docker
    base_url = "http://localhost:4000"
    full_url = f"{base_url}{endpoint}"

    # Define the request headers
    headers = {
        'DATA-241-API-KEY': api_key,  # API key included in the header
        'Content-Type': 'application/json'
    }

    try:
        # Send the GET request
        response = requests.get(full_url, headers=headers)

        # Raise an HTTPError for bad responses (4xx and 5xx)
        response.raise_for_status()

        # Print the response status code
        print(f"Status Code: {response.status_code}")

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
    1. Retrieves the API key from the environment variable 'DATA_241_API_KEY'.
    2. If the API key is not set, it prints an error and exits.
    3. Sends a GET request to the specified API endpoint and displays the response.
    """
    # Retrieve API key from environment variable
    api_key = os.environ.get('DATA_241_API_KEY')

    if not api_key:
        print("Error: The DATA_241_API_KEY environment variable is not set.")
    else:
        #Testing v2 functions
        #Add string endpoint to test
        list_endpoint = [
        '/api/v2/2019',
        '/api/v2/open/AAPL',
        '/api/v2/close/AAPL',
        '/api/v2/high/AAPL',
        '/api/v2/low/AAPL'
        ]

        for endpoint in list_endpoint:
            make_get_request(endpoint,api_key)


        '''
        #Testing individual endpoint

        endpoint = '/api/v1/row_count'
        make_get_request(endpoint, api_key)
        '''