import sqlite3
import os
import time
from datetime import datetime
from typing import Dict, Any, List

class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Interactions and Events
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS event_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP,
                    event_type TEXT,
                    details TEXT
                )
            ''')
            # Activity logs
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS activity_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP,
                    app_name TEXT,
                    window_title TEXT,
                    duration REAL
                )
            ''')
            conn.commit()

    def log_event(self, event_type: str, details: str = ""):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO event_logs (timestamp, event_type, details) VALUES (?, ?, ?)",
                         (datetime.now().isoformat(), event_type, details))
            conn.commit()

    def log_activity(self, app: str, title: str, duration: float):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO activity_logs (timestamp, app_name, window_title, duration) VALUES (?, ?, ?, ?)",
                         (datetime.now().isoformat(), app, title, duration))
            conn.commit()

class ShortTermMemory:
    """Stores temporary session variables and timestamps."""
    def __init__(self):
        self.data: Dict[str, Any] = {
            "last_greeting_time": 0,
            "last_user_seen": 0,
            "current_focus_start": 0,
            "switch_count": 0,
            "last_switch_time": 0,
            "is_user_present": False
        }

    def update(self, key: str, value: Any):
        self.data[key] = value

    def get(self, key: str, default: Any = None):
        return self.data.get(key, default)
