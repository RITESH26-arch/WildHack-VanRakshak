"""Small SQLite audit log for detections and alert attempts."""
import sqlite3
from pathlib import Path
DB_PATH = Path("vanrakshak_demo.db")

def init_db():
    with sqlite3.connect(DB_PATH) as con:
        con.execute("""CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            camera_id TEXT NOT NULL,
            label TEXT NOT NULL,
            confidence REAL NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            maps_url TEXT NOT NULL,
            evidence_path TEXT NOT NULL,
            alert_status TEXT NOT NULL,
            demo_mode INTEGER NOT NULL
        )""")

def record_alert(row):
    with sqlite3.connect(DB_PATH) as con:
        con.execute("""INSERT INTO alerts
        (timestamp,camera_id,label,confidence,latitude,longitude,maps_url,evidence_path,alert_status,demo_mode)
        VALUES (?,?,?,?,?,?,?,?,?,?)""", (
            row["timestamp"], row["camera_id"], row["label"], row["confidence"],
            row["latitude"], row["longitude"], row["maps_url"], row["evidence_path"],
            row["alert_status"], int(row["demo_mode"])
        ))
