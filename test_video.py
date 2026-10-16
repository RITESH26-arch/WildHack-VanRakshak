"""VanRakshak end-to-end demo: video -> YOLO -> evidence -> Telegram."""
from collections import defaultdict
from datetime import datetime
from pathlib import Path
import time
import cv2

import config
from alerts import send_telegram_alert
from detector import ThreatDetector
from location import generate_demo_location
from storage import init_db, record_alert

EVIDENCE_DIR = Path("static/evidence")
EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

def main():
    init_db()
    if not config.DEMO_MODE:
        raise SystemExit("This backup build is demo-only. Set DEMO_MODE=true for synthetic coordinates.")
    source = config.VIDEO_SOURCE
    # Accept webcam index if configured as a numeric string; otherwise a file/stream URL.
    cap = cv2.VideoCapture(int(source) if source.isdigit() else source)
    if not cap.isOpened():
        raise SystemExit(f"Could not open VIDEO_SOURCE={source!r}. Check the path or stream URL.")
    detector = ThreatDetector()
    camera_id = config.DEMO_CAMERA_ID
    location = generate_demo_location()  # generated once per run, stable for this simulated camera
    print(f"[DEMO] {camera_id}: {location['latitude']}, {location['longitude']}")
    print(f"[DEMO] Google Maps: {location['maps_url']}")
    print("Press Q in the video window to stop.")

    frame_index = 0
    last_alert = defaultdict(float)
    while True:
        ok, frame = cap.read()
        if not ok:
            print("Video ended or frame could not be read.")
            break
        frame_index += 1
        if frame_index % config.FRAME_STRIDE != 0:
            cv2.imshow("VanRakshak | DEMO", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
            continue

        processed, detections, confirmed = detector.infer(frame)
        for d in detections:
            x1, y1, x2, y2 = d["box"]
            cv2.rectangle(processed, (x1, y1), (x2, y2), (0, 200, 255), 2)
            cv2.putText(processed, f"{d['label']} {d['confidence']:.2f}",
                        (x1, max(20, y1 - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 200, 255), 2)

        now = time.time()
        # If a patrol/ranger exception is configured for this camera, suppress notifications.
        exempt = camera_id in config.RANGER_EXEMPT_CAMERA_IDS
        sent_this_frame = set()
        for d in confirmed:
            key = f"{camera_id}:{d['label']}"
            if exempt:
                print(f"[RANGER EXCEPTION] {camera_id}: suppressing {d['label']} alert")
                continue
            if key in sent_this_frame or now - last_alert[key] < config.ALERT_COOLDOWN_SECONDS:
                continue
            sent_this_frame.add(key)
            stamp = datetime.now().astimezone().isoformat(timespec="seconds")
            filename = f"{camera_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{d['label']}.jpg"
            evidence_path = EVIDENCE_DIR / filename
            cv2.imwrite(str(evidence_path), processed)
            status_label = "POSSIBLE INTRUSION"
            message = (
                f"🚨 VANRAKSHAK DEMO ALERT\n"
                f"Status: {status_label} (YOLO detection; ranger verification required)\n"
                f"Object: {d['label']}\nConfidence: {d['confidence']:.0%}\n"
                f"Camera: {camera_id}\nTime: {stamp}\n"
                f"Location: {location['location_name']}\n"
                f"Coordinates: {location['latitude']}, {location['longitude']}\n"
                f"Location type: SIMULATED — not extracted from video\n"
                f"Google Maps: {location['maps_url']}"
            )
            success, detail = send_telegram_alert(message, str(evidence_path))
            last_alert[key] = now
            row = {
                "timestamp": stamp, "camera_id": camera_id, "label": d["label"],
                "confidence": d["confidence"], "latitude": location["latitude"],
                "longitude": location["longitude"], "maps_url": location["maps_url"],
                "evidence_path": str(evidence_path), "alert_status": detail if success else f"FAILED: {detail}",
                "demo_mode": True,
            }
            record_alert(row)
            print(f"[ALERT] {d['label']} {d['confidence']:.2f} | {detail} | {location['maps_url']}")

        cv2.imshow("VanRakshak | DEMO", processed)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
