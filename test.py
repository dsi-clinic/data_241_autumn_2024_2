import requests
import os

def make_get_request(endpoint, api_key):
    # Base URL for the Flask app running in Docker
    base_url = "http://localhost:4000"
    full_url = f"{base_url}{endpoint}"

    # Define the headers
    headers = {
        'DATA-241-API-KEY': api_key,  # API key in the header
        'Content-Type': 'application/json'
    }

    try:
        # Make the GET request
        response = requests.get(full_url, headers=headers)
        
        # Check if the request was successful
        response.raise_for_status()
        
        # Print the response status code
        print(f"Status Code: {response.status_code}")
        
        # Print the response content as JSON
        print("Response Content:")
        print(response.json())  # Corrected from .json to .json()
        
        return response

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None


if __name__ == "__main__":
    # Ensure the environment variable is set correctly
    api_key = os.environ.get('DATA_241_API_KEY')
    print(api_key)
    if not api_key:
        print("Error: DATA_241_API_KEY environment variable is not set.")
    else:
        # Specify the endpoint you want to test
        endpoint = '/api/v1/row_count'
        make_get_request(endpoint, api_key)
