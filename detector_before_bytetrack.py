"""YOLO inference and persistence confirmation for people/vehicles."""
from collections import deque, Counter
import cv2
from ultralytics import YOLO
import config

# COCO classes: person, bicycle, car, motorcycle, bus, truck
TARGET_CLASSES = {0: "person", 1: "bicycle", 2: "car", 3: "motorcycle", 5: "bus", 7: "truck"}

class ThreatDetector:
    def __init__(self):
        self.model = YOLO(config.YOLO_MODEL)
        self.recent = deque(maxlen=max(config.PERSISTENCE_WINDOW, 1))

    def infer(self, frame):
        # CLAHE helps local contrast on some dark footage; retain original if conversion fails.
        try:
            lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            l = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(l)
            processed = cv2.cvtColor(cv2.merge((l, a, b)), cv2.COLOR_LAB2BGR)
        except cv2.error:
            processed = frame

        results = self.model.predict(
            source=processed, conf=config.CONFIDENCE_THRESHOLD,
            imgsz=config.IMAGE_SIZE, classes=list(TARGET_CLASSES.keys()), verbose=False
        )
        found = []
        result = results[0]
        if result.boxes is not None:
            for box in result.boxes:
                cls_id = int(box.cls.item())
                confidence = float(box.conf.item())
                if cls_id not in TARGET_CLASSES:
                    continue
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                found.append({
                    "class_id": cls_id,
                    "label": TARGET_CLASSES[cls_id],
                    "confidence": confidence,
                    "box": (x1, y1, x2, y2),
                })
        self.recent.append({d["label"] for d in found})
        counts = Counter(label for frame_labels in self.recent for label in frame_labels)
        confirmed = [d for d in found if counts[d["label"]] >= config.PERSISTENCE_HITS]
        return processed, found, confirmed
