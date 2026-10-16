"""Simulated demo-camera coordinates and Google Maps URL helpers."""
import random
from urllib.parse import quote
import config

def generate_demo_location():
    """Generate a plausible point inside the configured demo bounding box.

    This is synthetic metadata, not GPS extracted from the video.
    """
    lat = random.uniform(config.DEMO_LAT_MIN, config.DEMO_LAT_MAX)
    lon = random.uniform(config.DEMO_LON_MIN, config.DEMO_LON_MAX)
    return {
        "latitude": round(lat, 6),
        "longitude": round(lon, 6),
        "location_name": config.DEMO_LOCATION_NAME,
        "maps_url": f"https://www.google.com/maps?q={lat:.6f},{lon:.6f}",
        "location_type": "SIMULATED DEMO COORDINATES",
    }
