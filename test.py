"""Tests Flask server against requests"""

import os

import requests


def make_get_request(endpoint, api_key):
    """Tests get requests"""
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
    """Tests Post Requests"""
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
    """Tests Delete Requests"""
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


    # CHECK PART 6 DOC FOR STRING LIST
    #V1
    make_get_request("/api/v1/row_by_market_count",api_key)
    make_get_request("/api/v1/row_count",api_key)
    make_get_request("/api/v1/unique_stock_count",api_key)


    #V2
    make_get_request("/api/v2/2019",api_key)
    make_get_request("/api/v2/Open/AAPL",api_key)



    #V3

    #1
    make_post_request("/api/v3/accounts",{ 'name' : 'SAWmdaodwawdwadwadwdw' }, api_key) 
    make_get_request("/api/v3/accounts",api_key) #TESTED DONE
    make_delete_request("/api/v3/accounts",{'account_id' : 1 }, api_key) #TESTING DONNEE

    #2
    make_post_request("/api/v3/accounts",{ 'name' : 'SAWmdaodwawdwadwadwdw' }, api_key) #TESTED DONE
    make_get_request("/api/v3/accounts",api_key) #TESTED DONE
    make_delete_request("/api/v3/accounts",{'account_id' : 1 }, api_key) #TESTING DONNEE

    #3
    make_post_request("/api/v3/accounts",{ 'name' : 'SAWmdaodwawdwadwadwdw' }, api_key) #TESTED DONE
    make_get_request("/api/v3/accounts",api_key) #TESTED DONE
    make_delete_request("/api/v3/accounts",{'account_id' : 1 }, api_key) #TESTING 

    #4
    make_post_request("/api/v3/accounts",{ 'name' : 'SAWmdaodwawdwadwadwdw' },api_key) #TESTED DONE
    make_get_request("/api/v3/accounts/1",api_key)
    make_delete_request("/api/v3/accounts",{'account_id' : 1 }, api_key) #TESTING DONNEE

    #5
    make_post_request("/api/v3/stocks", { 'account_id' : 2, 'symbol': 'AAME', 'purchase_date' : "01-Jan-2010", 'sale_date': "04-Jan-2010", 'number_of_shares': 10}, api_key) #TESTED DONE
    make_get_request("/api/v3/stocks/AAME",api_key) #TESTED DONE
    make_delete_request("/api/v3/stocks", { 'account_id' : 2, 'symbol': 'AAME', 'purchase_date' : "01-Jan-2010", 'sale_date': "04-Jan-2010", 'number_of_shares': 10}, api_key)

    #6
    make_post_request("/api/v3/stocks", { 'account_id' : 2, 'symbol': 'AAME', 'purchase_date' : "01-Jan-2010", 'sale_date': "04-Jan-2010", 'number_of_shares': 10}, api_key) #TESTED DONE
    make_get_request("/api/v3/stocks/AAME",api_key) #TESTED DONE
    make_delete_request("/api/v3/stocks", { 'account_id' : 2, 'symbol': 'AAME', 'purchase_date' : "01-Jan-2010", 'sale_date': "04-Jan-2010", 'number_of_shares': 10}, api_key)

    #7
    make_post_request("/api/v3/stocks", { 'account_id' : 2, 'symbol': 'AAME', 'purchase_date' : "01-Jan-2010", 'sale_date': "04-Jan-2010", 'number_of_shares': 10}, api_key) #TESTED DONE
    make_get_request("/api/v3/stocks/AAME",api_key) #TESTED DONE
    make_delete_request("/api/v3/stocks", { 'account_id' : 2, 'symbol': 'AAME', 'purchase_date' : "01-Jan-2010", 'sale_date': "04-Jan-2010", 'number_of_shares': 10}, api_key)

    #8
    make_post_request("/api/v3/stocks", { 'account_id' : 2, 'symbol': 'AAME', 'purchase_date' : "01-Jan-2010", 'sale_date': "04-Jan-2010", 'number_of_shares': 10}, api_key) #TESTED DONE
    make_post_request("/api/v3/stocks", { 'account_id' : 2, 'symbol': 'AAME', 'purchase_date' : "03-Jan-2011", 'sale_date': "02-Jan-2012", 'number_of_shares': 10}, api_key) #TESTED DONE
    make_get_request("/api/v3/accounts/return/2",api_key)
    make_delete_request("/api/v3/stocks", { 'account_id' : 2, 'symbol': 'AAME', 'purchase_date' : "01-Jan-2010", 'sale_date': "04-Jan-2010", 'number_of_shares': 10}, api_key)
    make_delete_request("/api/v3/stocks", { 'account_id' : 2, 'symbol': 'AAME', 'purchase_date' : "03-Jan-2011", 'sale_date': "02-Jan-2012", 'number_of_shares': 10}, api_key)

    print("Checking Done")
