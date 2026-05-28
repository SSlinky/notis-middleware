"""Test cases for the API."""
from app import api
from dotenv import dotenv_values


config = dotenv_values(".env")


def test_get_time_entries():
    """Test the get_time_entries function."""
    options = {
        "api_key": config['API_KEY'],
        "org_id": config['ORG_ID'],
        "person_id": config['PERSON_ID']
    }
    response = api.get_time_entries(options)
    assert response.status_code == 200

    json = response.json()
    assert "data" in json
    assert "included" in json

    included_types = {}
    for item in json["included"]:
        item_type = item.get("type")
        if item_type:
            included_types[item_type] = True

    assert "people" in included_types
    assert "services" in included_types
    assert "deals" in included_types
