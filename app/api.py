"""Helpers to call the Productive API."""
import datetime
import requests
from app.util import get_month_range

API = {
    "get_time_entries": "https://api.productive.io/api/v2/time_entries"
}

def get_time_entries(options: dict):
    """Gets the time entries from the Productive API

    Args:
        options (dict): The API call options.
    Returns:
        requests.Response: The API response.
    """
    headers = {
        "X-AUTH-TOKEN": options["api_key"],
        "X-Organization-Id": options["org_id"],
        "Content-Type": "application/vnd.api+json"
    }

    date = options.get("date", datetime.datetime.now())
    after, before = get_month_range(date)
    params = {
        "filter[after]": after,
        "filter[before]": before,
        "page[number]": options.get("page", 1),
        "page[size]": options.get("page_size", 200),
        "include": "person,service,service.deal"
    }

    if options.get("person_id"):
        params["filter[person_id]"] = options["person_id"]

    return requests.get(API["get_time_entries"], headers=headers, params=params, timeout=10)
