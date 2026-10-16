"""Environment-backed configuration for VanRakshak demo."""
import os
from dotenv import load_dotenv

load_dotenv()

def _float(name, default):
    try:
        return float(os.getenv(name, default))
    except (TypeError, ValueError):
        return float(default)

def _int(name, default):
    try:
        return int(os.getenv(name, default))
    except (TypeError, ValueError):
        return int(default)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()
VIDEO_SOURCE = os.getenv("VIDEO_SOURCE", "videos/sample.mp4").strip()
YOLO_MODEL = os.getenv("YOLO_MODEL", "yolo11s.pt").strip()
CONFIDENCE_THRESHOLD = _float("CONFIDENCE_THRESHOLD", 0.35)
IMAGE_SIZE = _int("IMAGE_SIZE", 960)
PERSISTENCE_HITS = _int("PERSISTENCE_HITS", 3)
PERSISTENCE_WINDOW = _int("PERSISTENCE_WINDOW", 5)
FRAME_STRIDE = max(1, _int("FRAME_STRIDE", 5))
ALERT_COOLDOWN_SECONDS = max(1, _int("ALERT_COOLDOWN_SECONDS", 60))
DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() in ("1", "true", "yes")
DEMO_CAMERA_ID = os.getenv("DEMO_CAMERA_ID", "CAM-DEMO-01")
DEMO_LOCATION_NAME = os.getenv("DEMO_LOCATION_NAME", "Simulated demo zone")
DEMO_LAT_MIN = _float("DEMO_LAT_MIN", 20.05)
DEMO_LAT_MAX = _float("DEMO_LAT_MAX", 20.35)
DEMO_LON_MIN = _float("DEMO_LON_MIN", 79.20)
DEMO_LON_MAX = _float("DEMO_LON_MAX", 79.55)
RANGER_EXEMPT_CAMERA_IDS = {
    x.strip() for x in os.getenv("RANGER_EXEMPT_CAMERA_IDS", "").split(",") if x.strip()
}
ALERTS_ENABLED = os.getenv("ALERTS_ENABLED", "true").lower() in ("1", "true", "yes")
