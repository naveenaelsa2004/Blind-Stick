"""
Database module for IoT Smart Blind Stick backend.
Manages SQLite storage and parameterized queries for sensor telemetry.
"""

import os
import sqlite3
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

# Default database path can be overridden by environment variable
DEFAULT_DB_DIR = os.getenv("DATABASE_DIR", os.path.join(os.path.dirname(__file__), "..", "data"))
DEFAULT_DB_FILE = os.getenv("DATABASE_FILE", "sensor_readings.db")
DATABASE_PATH = os.getenv("DATABASE_PATH", os.path.join(DEFAULT_DB_DIR, DEFAULT_DB_FILE))


def get_db_path() -> str:
    """Return the absolute path to the SQLite database, ensuring its directory exists."""
    abs_path = os.path.abspath(DATABASE_PATH)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    return abs_path


def get_connection() -> sqlite3.Connection:
    """Return an open SQLite database connection with row factory enabled."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path, timeout=10.0)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """
    Initialize SQLite database schema and indices.
    Called automatically on backend startup.
    """
    db_path = get_db_path()
    conn = get_connection()
    try:
        with conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS sensor_readings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    device_id TEXT NOT NULL,
                    distance_cm REAL,
                    status TEXT NOT NULL,
                    timestamp DATETIME NOT NULL
                );
                """
            )
            # Create indices for fast chronological queries and device filtering
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_sensor_readings_timestamp 
                ON sensor_readings(timestamp);
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_sensor_readings_device 
                ON sensor_readings(device_id);
                """
            )
    finally:
        conn.close()


def insert_reading(device_id: str, distance_cm: Optional[float], status: str) -> int:
    """
    Insert a verified sensor reading into SQLite using parameterized query.
    Returns the newly inserted row ID.
    """
    now_utc = datetime.now(timezone.utc).isoformat()
    conn = get_connection()
    try:
        with conn:
            cursor = conn.execute(
                """
                INSERT INTO sensor_readings (device_id, distance_cm, status, timestamp)
                VALUES (?, ?, ?, ?);
                """,
                (device_id, distance_cm, status, now_utc),
            )
            return cursor.lastrowid
    finally:
        conn.close()


def get_recent_readings(limit: int = 50, device_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Retrieve the most recent sensor readings in chronological order (oldest -> newest)
    suitable for charts and time-series plotting.
    """
    conn = get_connection()
    try:
        if device_id:
            query = """
                SELECT id, device_id, distance_cm, status, timestamp
                FROM sensor_readings
                WHERE device_id = ?
                ORDER BY id DESC
                LIMIT ?;
            """
            rows = conn.execute(query, (device_id, limit)).fetchall()
        else:
            query = """
                SELECT id, device_id, distance_cm, status, timestamp
                FROM sensor_readings
                ORDER BY id DESC
                LIMIT ?;
            """
            rows = conn.execute(query, (limit,)).fetchall()

        # Reverse so readings are in chronological ascending order
        readings = [dict(row) for row in reversed(rows)]
        return readings
    finally:
        conn.close()


def get_latest_reading(device_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Retrieve the single most recent reading for a given device (or overall).
    """
    conn = get_connection()
    try:
        if device_id:
            query = """
                SELECT id, device_id, distance_cm, status, timestamp
                FROM sensor_readings
                WHERE device_id = ?
                ORDER BY id DESC
                LIMIT 1;
            """
            row = conn.execute(query, (device_id,)).fetchone()
        else:
            query = """
                SELECT id, device_id, distance_cm, status, timestamp
                FROM sensor_readings
                ORDER BY id DESC
                LIMIT 1;
            """
            row = conn.execute(query).fetchone()

        return dict(row) if row else None
    finally:
        conn.close()


def check_db_health() -> bool:
    """Check database accessibility by executing a lightweight query."""
    try:
        conn = get_connection()
        conn.execute("SELECT 1;").fetchone()
        conn.close()
        return True
    except Exception:
        return False
