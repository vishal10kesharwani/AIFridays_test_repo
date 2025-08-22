import requests
import os
from dotenv import load_dotenv

load_dotenv()
MAPBOX_API_KEY = os.getenv("MAPBOX_API_KEY")

def get_location_name(lat, lon):
    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{lon},{lat}.json"
    params = {"access_token": MAPBOX_API_KEY}
    response = requests.get(url, params=params)
    data = response.json()

    if "features" in data and len(data["features"]) > 0:
        return data["features"][0]["place_name"]
    return "Unknown Location"
