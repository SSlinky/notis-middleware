"""The main api entrypoint."""
import requests
from app.api import get_time_entries
from app.model import HoursSubTotal, ResponseModel
from fastapi import FastAPI, Header, HTTPException


app = FastAPI()


def process_metadata(response: requests.Response):
    """Process the metadata from the Productive API response."""
    json = response.json()
    included = json.get("included", [])
    services = {}
    deals = {}
    for item in included:
        if item["type"] == "services":
            services[item["id"]] = {
                "name": item["attributes"]["name"],
                "deal": item["relationships"]["deal"]["data"]["id"]
            }
        elif item["type"] == "deals":
            deals[item["id"]] = item["attributes"]["name"]

    model = ResponseModel()
    model.services = {
        id: {
            "name": service["name"],
            "deal": deals.get(service["deal"], "Unknown Deal")
        }
        for id, service in services.items()
    }
    return model


def process_response(response: requests.Response, model: ResponseModel):
    """Process a 200 response from the Productive API."""
    if response.status_code != 200:
        msg = f"Unexpected response status code: {response.status_code}"
        raise ValueError(msg)

    json = response.json()
    if "data" not in json:
        msg = f"Response JSON does not contain 'data' key: {json}"
        raise ValueError(msg)

    for item in json["data"]:
        try:
            minutes: float = item["attributes"]["time"]
            related_service_id = item["relationships"]["service"]["data"]["id"]
            service = model.get_service(related_service_id)
        except KeyError as exc:
            msg = f"Malformed response item: {item}"
            raise ValueError(msg) from exc
        project = model.data.get(service["project"]) or HoursSubTotal(
            service=service["name"],
            project=service["project"],
            total=0.0
        )
        project.add_minutes(minutes)
        model.data[service["project"]] = project


@app.get("/hours", response_model=ResponseModel)
async def hours():
    """Endpoint that returns the billable hours logged in Productive.

    Args:
        api_key (str): The API key to authorise requests.
        org_id (str): The organisation ID to get hours from.
        person_id (str, optional): The person ID to get hours for.
    """
    if api_key is None:
        raise HTTPException(status_code=400, detail="Missing x-api-key header")

    # Build the options.
    options = {
        "api_key": os.getenv("API_KEY"),
        "org_id": os.getenv("ORG_ID"),
        "person_id": os.getenv("PERSON_ID"),
        "page": 1,
    }

    # Validate we have the required environment variables.
    if options["api_key"] is None or options["org_id"] is None:
        raise HTTPException(
            status_code=400,
            detail="Missing required environment variables"
        )

    # Get and process the first response.
    response = get_time_entries(options)
    model = process_metadata(response)
    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.text
        )
    process_response(response, model)

    # Process the remaining pages.
    # TODO: Response links isn't a thing.
    while response.status_code == 200 and "next" in response.links:
        options["page"] = options["page"] + 1
        response = get_time_entries(options)
        process_response(response, model)

    return model
