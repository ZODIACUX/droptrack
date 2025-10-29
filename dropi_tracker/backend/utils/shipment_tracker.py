import requests
import os

API_URL = "https://api.track123.com/gateway/open-api/tk/v2/track/query"
API_KEY = os.environ.get("TRACK123_API_KEY", "Test")

# Mapeo de nombres de transportadoras de Dropi a códigos de Track123
CARRIER_CODE_MAP = {
    "INTER RAPIDISIMO": "inter-rapidisimo",
    "SERVIENTREGA": "servientrega",
    "COORDINADORA": "coordinadora",
    "ENVIA": "envia",
    "TCC": "tcc",
    # Añadir más transportadoras según sea necesario
}

def track_shipments(shipments):
    """
    Tracks multiple shipments using the Track123 API.
    'shipments' is a list of dicts, e.g., [{"number": "123", "carrier": "INTER RAPIDISIMO"}]
    """
    headers = {
        "Track123-Api-Secret": API_KEY,
        "Content-Type": "application/json"
    }

    # Crear la lista de trackNos para la API de Track123
    track_infos = []
    for shipment in shipments:
        carrier_code = CARRIER_CODE_MAP.get(shipment["carrier"].upper())
        track_infos.append({
            "trackNo": shipment["number"],
            "courierCode": carrier_code
        })

    data = {
        "trackNos": track_infos
    }

    try:
        response = requests.post(API_URL, json=data, headers=headers)
        response.raise_for_status()

        api_response = response.json()

        if api_response.get("code") == "00000" and "data" in api_response:
            return process_tracking_data(api_response["data"])
        else:
            error_msg = api_response.get("msg", "Unknown API error")
            return {s["number"]: {"status": "Error", "details": error_msg} for s in shipments}

    except requests.exceptions.RequestException as e:
        return {s["number"]: {"status": "Error", "details": str(e)} for s in shipments}

def process_tracking_data(tracking_data):
    """
    Processes the successful response from the Track123 API into a structured format.
    """
    processed_trackings = {}

    accepted_content = tracking_data.get("accepted", {}).get("content", [])

    for item in accepted_content:
        tracking_number = item.get("trackNo")
        last_event = "No information yet"

        local_info = item.get("localLogisticsInfo")
        if local_info and "trackingDetails" in local_info and local_info["trackingDetails"]:
            last_event = local_info["trackingDetails"][0].get("eventDetail", "Status not available")

        processed_trackings[tracking_number] = {
            "status": item.get("trackingStatus", "Unknown"),
            "last_event": last_event,
            "raw_data": item
        }

    # Handle rejected trackings
    rejected_content = tracking_data.get("rejected", [])
    for item in rejected_content:
        tracking_number = item.get("trackNo")
        error_msg = item.get("error", {}).get("msg", "Rejected by tracking provider")
        processed_trackings[tracking_number] = {
            "status": "Error",
            "last_event": error_msg
        }

    return processed_trackings
