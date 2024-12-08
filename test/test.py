"""Tests for the Flask application."""
import sys
from pathlib import Path
import os
import pytest
from jsonschema import validate

# Add the src directory to the Python path so we can import the app
sys.path.append(str(Path(__file__).parent.parent.resolve()))

from flask_app import create_app  # noqa E402


@pytest.fixture
def app():
    """Create and configure a test instance of the application."""
    app = create_app()
    app.config.update({
        "TESTING": True,
        # Add any test-specific configuration here
    })
    return app


@pytest.fixture
def client(app):
    """Create a test client for the app."""
    return app.test_client()


def test_app_exists(app):
    """Test that the app exists."""
    assert app is not None


def test_app_is_testing(app):
    """Test that the app is in testing mode."""
    assert app.config["TESTING"]

def test_0_v1_row_count(client):
    """
    Test the /api/v1/row_count route with valid API key.

    Verifies correct schema and successful response.
    """
    HTTP_OK = 200

    schema = {
        "type": "object",
        "properties": {
            "row_count": {"type": "integer", "minimum": 0}
        },
        "required": ["row_count"]
    }

    # Ensure the environment variable is set
    os.environ["DATA_241_API_KEY"] = "disha"

    # Set the correct header
    headers = {"DATA-241-API-KEY": os.environ["DATA_241_API_KEY"]}

    response = client.get("/api/v1/row_count", headers=headers)

    # Assertions
    assert response.status_code == HTTP_OK
    assert response.content_type == "application/json"

    # Validate JSON schema
    json_data = response.get_json()
    validate(instance=json_data, schema=schema)


def test_1_v1_unique_stock_count(client):
    """
    Test the /api/v1/unique_stock_count route with a valid API key.

    Verifies the response includes the correct JSON schema and returns a successful status.
    """
    HTTP_OK = 200

    schema = {
        "type": "object",
        "properties": {
            "unique_stock_count": {"type": "integer", "minimum": 0}
        },
        "required": ["unique_stock_count"]
    }

    # Ensure the environment variable is set for authentication
    os.environ["DATA_241_API_KEY"] = "disha"

    # Set the correct headers
    headers = {"DATA-241-API-KEY": os.environ["DATA_241_API_KEY"]}

    # Make the request to the endpoint
    response = client.get("/api/v1/unique_stock_count", headers=headers)

    # Extract the JSON data from the response
    json_data = response.get_json()

    # Perform assertions
    assert response.status_code == HTTP_OK, "Expected HTTP 200 OK status"
    assert response.content_type == "application/json", "Response content type must be JSON"

    # Validate the structure of the JSON response
    validate(instance=json_data, schema=schema)

    # Additional check to ensure the unique_stock_count is an expected value (if applicable)
    assert json_data["unique_stock_count"] >= 0, "The unique stock count must be non-negative"

def test_2_v1_market_count(client):
    """Test the /api/v1/row_by_market_count endpoint."""

    schema = {
        "type": "object",
        "properties": {
            "NYSE": {"type": "integer"},
            "NASDAQ": {"type": "integer"}
        },
        "required": ["NYSE", "NASDAQ"]
    }

    # Ensure the environment variable is set
    os.environ["DATA_241_API_KEY"] = "disha"

    # Set the correct header
    headers = {"DATA-241-API-KEY": os.environ["DATA_241_API_KEY"]}


    good_response = client.get("/api/v1/row_by_market_count", headers=headers)
    assert good_response.status_code == 200
    assert good_response.content_type == "application/json"
    validate(instance=good_response.get_json(), schema=schema)



def test_3_v2_year(client):
    """Test the /api/players endpoint."""


    schema = {
    "type": "object",
    "properties": {
        "year": {"type": "integer"},
        "count": {"type": "integer"}
    },
    "required": ["year", "count"]
    }

    # Ensure the environment variable is set
    os.environ["DATA_241_API_KEY"] = "disha"

    # Set the correct header
    headers = {"DATA-241-API-KEY": "disha"}

    good_response = client.get(f"/api/v2/2019", headers=headers)
    assert good_response.status_code == 200
    assert good_response.content_type == "application/json"
    validate(instance=good_response.get_json(), schema=schema)

def test_4_v2_open_symbol(client):
    """Test the /api/players endpoint."""

    schema = schema = {
    "type": "object",
    "properties": {
        "symbol": {
            "type": "string"
        },
        "price_info": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
                    },
                    "open": {
                        "type": "number"
                    }
                },
                "required": ["date", "open"]
            }
        }
    },
    "required": ["symbol", "price_info"]
    }

    # Ensure the environment variable is set
    os.environ["DATA_241_API_KEY"] = "disha"

    # Set the correct header
    headers = {"DATA-241-API-KEY": "disha"}

    good_response = client.get(f"/api/v2/open/AAPL", headers=headers)
    assert good_response.status_code == 200
    assert good_response.content_type == "application/json"
    validate(instance=good_response.get_json(), schema=schema)

def test_5_v2_close_symbol(client):
    """Test the /api/players endpoint."""

    schema = schema = {
    "type": "object",
    "properties": {
        "symbol": {
            "type": "string"
        },
        "price_info": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
                    },
                    "close": {
                        "type": "number"
                    }
                },
                "required": ["date", "close"]
            }
        }
    },
    "required": ["symbol", "price_info"]
    }

    # Ensure the environment variable is set
    os.environ["DATA_241_API_KEY"] = "disha"

    # Set the correct header
    headers = {"DATA-241-API-KEY": "disha"}

    good_response = client.get(f"/api/v2/close/AAPL", headers=headers)
    assert good_response.status_code == 200
    assert good_response.content_type == "application/json"
    validate(instance=good_response.get_json(), schema=schema)

def test_6_v2_high_symbol(client):
    """Test the /api/players endpoint."""

    schema = schema = {
    "type": "object",
    "properties": {
        "symbol": {
            "type": "string"
        },
        "price_info": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
                    },
                    "high": {
                        "type": "number"
                    }
                },
                "required": ["date", "high"]
            }
        }
    },
    "required": ["symbol", "price_info"]
    }

    # Ensure the environment variable is set
    os.environ["DATA_241_API_KEY"] = "disha"

    # Set the correct header
    headers = {"DATA-241-API-KEY": "disha"}

    good_response = client.get(f"/api/v2/high/AAPL", headers=headers)
    assert good_response.status_code == 200
    assert good_response.content_type == "application/json"
    validate(instance=good_response.get_json(), schema=schema)

def test_7_v2_low_symbol(client):
    """Test the /api/players endpoint."""

    schema = schema = {
    "type": "object",
    "properties": {
        "symbol": {
            "type": "string"
        },
        "price_info": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
                    },
                    "low": {
                        "type": "number"
                    }
                },
                "required": ["date", "low"]
            }
        }
    },
    "required": ["symbol", "price_info"]
    }

    # Ensure the environment variable is set
    os.environ["DATA_241_API_KEY"] = "disha"

    # Set the correct header
    headers = {"DATA-241-API-KEY": "disha"}

    good_response = client.get(f"/api/v2/low/AAPL", headers=headers)
    assert good_response.status_code == 200
    assert good_response.content_type == "application/json"
    validate(instance=good_response.get_json(), schema=schema)


def test_9_v4_backtest(client):
    """Test the /api/v4/back_test endpoint with a POST request."""

    schema = {
        "type": "object",
        "properties": {
            "return": {
                "type": "number"
            },
            "num_observations": {
                "type": "integer"
            }
        },
        "required": ["return", "num_observations"]
    }

    os.environ["DATA_241_API_KEY"] = "disha"

    headers = {"DATA-241-API-KEY": "disha"}

    payload = {
    "value_1" : "O1",
    "value_2" : "C1",
    "operator" : "LT",
    "purchase_type": "B", 
    "start_date": "2020-01-03",
    "end_date": "2020-01-03"
    }

    response = client.post("/api/v4/back_test", headers=headers, json=payload)

    assert response.status_code == 200
    assert response.content_type == "application/json"

    validate(instance=response.get_json(), schema=schema)


def test_10_routes_without_api_key(client):
    """
    Test routes from v1, v2, and v4 without an API key.

    Verifies that each route returns a 401 Unauthorized status
    when no API key is provided.
    """
    HTTP_UNAUTHORIZED = 401

    # V1 Routes Test - Row Count
    v1_row_count_response = client.get("/api/v1/row_count")
    assert v1_row_count_response.status_code == HTTP_UNAUTHORIZED

    # V2 Routes Test - Year Count (using 2020 as an example year)
    v2_year_count_response = client.get("/api/v2/2020")
    assert v2_year_count_response.status_code == HTTP_UNAUTHORIZED

    # V4 Route Test - Backtesting (using a POST request)
    v4_backtest_response = client.post("/api/v4/back_test", json={
        "value_1": "O1",
        "value_2": "C2",
        "operator": "LT",
        "purchase_type": "B",
        "start_date": "2020-01-01",
        "end_date": "2020-12-31"
    })
    assert v4_backtest_response.status_code == HTTP_UNAUTHORIZED

def test_11_v2_year_invalid(client):
    """
    Test sending a request with an incorrect/non-existent year to /api/v2/{YEAR} endpoint.

    Verify that the endpoint returns the correct status code when an invalid year (e.g., 1980) is provided.
    """
    invalid_year = "1980"

    # Set the correct header using environment variable
    headers = {"DATA-241-API-KEY": os.environ["DATA_241_API_KEY"]}

    response = client.get(f"/api/v2/{invalid_year}", headers=headers)

    # This should return a 404 status code since there's no data for this year
    assert response.status_code == 404


def test_12_invalid_api_key(client):
    """Test invalid API Key for one v1, one v2, and one v4 route."""

    # Define invalid api key
    invalid_headers = {"DATA-241-API-KEY": "anuj"}

    # v1 route test: /api/v1/row_by_market_count
    v1_response = client.get("/api/v1/row_by_market_count", headers=invalid_headers)
    assert v1_response.status_code == 401, f"Unexpected status code for v1: {v1_response.status_code}"

    # v2 route test: /api/v2/{YEAR}
    v2_response = client.get("/api/v2/{YEAR}", headers=invalid_headers)
    assert v2_response.status_code == 401, f"Unexpected status code for v2: {v2_response.status_code}"

    # Test v4 route: back_test (requires POST with JSON data)
    v4_data = {
        "value_1": "O1",
        "value_2": "C2",
        "operator": "LT",
        "purchase_type": "B",
        "start_date": "2020-01-01",
        "end_date": "2020-12-31"
    }
    v4_response = client.post(
        "/api/v4/back_test",
        json=v4_data,
        headers=invalid_headers
    )
    assert v4_response.status_code == 401









