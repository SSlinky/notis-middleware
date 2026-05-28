"""Test cases for the main application."""
from dotenv import dotenv_values
from app.main import process_metadata, process_response

config = dotenv_values(".env")

META = {
    "person": {
        "id": "2001234",
        "type": "people",
        "attributes": {
            "first_name": "John",
            "last_name": "Doe"
        }
    },
    "service": {
        "id": "1001234",
        "type": "services",
        "attributes": {"name": "Service 1"},
        "relationships": {"deal": {"data": {"id": "1000"}}}
    },
    "deal": {
        "id": "1000",
        "type": "deals",
        "attributes": {"name": "Project Name"}
    }
}


class MockResponse:
    """A mock response object for testing."""
    def __init__(self, json_data):
        self._json_data = json_data
        self.status_code = 200

    def json(self):
        """Return the JSON data."""
        return self._json_data

    def raise_for_status(self):
        """Mock raise_for_status method."""


def test_process_metadata():
    """Test the process_metadata function."""
    response = MockResponse({
        "data": [
            {
                "type": "time_entries",
                "attributes": {"time": 120},
                "relationships": {
                    "person": {"data": {
                        "type": "people",
                        "id": META["person"]["id"]}
                    },
                    "service": {"data": {
                        "type": "services",
                        "id": META["service"]["id"]}
                    }
                }
            }
        ],
        "included": [
            META["person"],
            META["service"],
            META["deal"]
        ]
    })

    model = process_metadata(response)
    assert META["service"]["id"] in model.services
    assert len(model.services) == 1
    assert model.services[META["service"]["id"]]["name"] == \
        META["service"]["attributes"]["name"]
    assert model.services[META["service"]["id"]]["deal"] == \
        META["deal"]["attributes"]["name"]


def test_process_response_raise_for_status():
    """Test the process_response raises ValueError for non-200 responses."""
    response = MockResponse({})
    response.status_code = 400
    try:
        process_response(response, None)
        assert False, "Expected ValueError for non-200 response"
    except ValueError as exc:
        assert str(exc) == "Unexpected response status code: 400"


def test_process_response_missing_data():
    """Test the process_response raises ValueError for missing 'data' key."""
    response = MockResponse({})
    try:
        process_response(response, None)
        assert False, "Expected ValueError for missing 'data' key"
    except ValueError as exc:
        assert str(exc) == "Response JSON does not contain 'data' key: {}"


def test_process_response_malformed_item():
    """Test the process_response raises ValueError for malformed items."""
    response = MockResponse({
        "data": [
            {
                "type": "time_entries",
                "attributes": {"time": 120},
                "relationships": {
                    "person": {"data": {
                        "type": "people",
                        "id": config['PERSON_ID']}
                    },
                    # Missing service relationship
                }
            }
        ],
        "included": []
    })
    model = process_metadata(response)
    try:
        process_response(response, model)
        assert False, "Expected ValueError for malformed item"
    except ValueError as exc:
        assert str(exc).startswith("Malformed response item:")


def test_process_response_valid():
    """Test the process_response function with valid data."""
    response = MockResponse({
        "data": [
            {
                "type": "time_entries",
                "attributes": {"time": 480},
                "relationships": {
                    "person": {"data": {
                        "type": "people",
                        "id": META["person"]["id"]}
                    },
                    "service": {"data": {
                        "type": "services",
                        "id": META["service"]["id"]}
                    }
                }
            },
            {
                "type": "time_entries",
                "attributes": {"time": 480},
                "relationships": {
                    "person": {"data": {
                        "type": "people",
                        "id": META["person"]["id"]}
                    },
                    "service": {"data": {
                        "type": "services",
                        "id": META["service"]["id"]}
                    }
                }
            }
        ],
        "included": [
            META["person"],
            META["service"],
            META["deal"]
        ]
    })

    model = process_metadata(response)
    process_response(response, model)
    project = META["deal"]["attributes"]["name"]
    assert len(model.data) == 1
    assert model.data[project].total == 16
