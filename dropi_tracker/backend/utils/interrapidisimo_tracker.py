import requests
import os

API_URL = "https://api.track123.com/gateway/open-api/tk/v2/track/query"
API_KEY = os.environ.get("TRACK123_API_KEY", "Test") # Use "Test" as a default for development

def track_packages(tracking_numbers):
    """
    Tracks multiple packages using the Track123 API.
    """
    headers = {
        "Track123-Api-Secret": API_KEY,
        "Content-Type": "application/json"
    }

    data = {
        "trackNos": tracking_numbers
    }

    try:
        response = requests.post(API_URL, json=data, headers=headers)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)

        api_response = response.json()

        if api_response.get("code") == "00000" and "data" in api_response and "accepted" in api_response["data"]:
            return process_tracking_data(api_response["data"]["accepted"])
        else:
            # Handle cases where the API returns an error or unexpected format
            return {num: {"status": "Error", "details": api_response.get("msg", "Unknown API error")} for num in tracking_numbers}

    except requests.exceptions.RequestException as e:
        # Handle network errors
        return {num: {"status": "Error", "details": str(e)} for num in tracking_numbers}

def process_tracking_data(tracking_data):
    """
    Processes the successful response from the Track123 API into a structured format.
    """
    processed_trackings = {}

    # The 'accepted' key contains a dictionary, not a list, so we access its 'content'
    content = tracking_data.get("content", [])

    for item in content:
        tracking_number = item.get("trackNo")
        last_event = "No information yet"

        # Check for local logistics info and tracking details
        local_info = item.get("localLogisticsInfo")
        if local_info and "trackingDetails" in local_info and local_info["trackingDetails"]:
            last_event = local_info["trackingDetails"][0].get("eventDetail", "Status not available")

        processed_trackings[tracking_number] = {
            "status": item.get("trackingStatus", "Unknown"),
            "last_event": last_event,
            "raw_data": item # Include raw data for potential future use
        }

    return processed_trackings
