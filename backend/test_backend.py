"""
Unit and integration tests for FastAPI backend and SQLite database.
"""

import os
import sys

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.dirname(__file__))

from fastapi.testclient import TestClient
from main import app
from database import get_connection, get_db_path

client = TestClient(app)

def run_tests():
    print("==================================================")
    print(" Running Automated Backend & Database Tests       ")
    print("==================================================")

    # Test 1: Health check endpoint
    response = client.get("/api/health")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    health_data = response.json()
    assert health_data["status"] == "healthy", f"Expected healthy, got {health_data}"
    assert health_data["database"] == "connected"
    print("[PASS] Test 1: GET /api/health returned 200 OK and database connected")

    # Test 2: POST valid sensor reading (e.g., 45.2 cm)
    payload_valid = {
        "device_id": "blind-stick-01",
        "distance_cm": 45.2,
        "status": "valid"
    }
    response = client.post("/api/readings", json=payload_valid)
    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["success"] is True
    assert "id" in data
    reading_id = data["id"]
    print(f"[PASS] Test 2: POST /api/readings accepted valid reading (ID: {reading_id})")

    # Test 3: POST second valid reading (e.g., 18.5 cm - danger range)
    payload_danger = {
        "device_id": "blind-stick-01",
        "distance_cm": 18.5,
        "status": "valid"
    }
    response = client.post("/api/readings", json=payload_danger)
    assert response.status_code == 201
    print("[PASS] Test 3: POST /api/readings accepted danger range reading (18.5 cm)")

    # Test 4: POST unknown / timeout reading
    payload_unknown = {
        "device_id": "blind-stick-01",
        "distance_cm": None,
        "status": "unknown"
    }
    response = client.post("/api/readings", json=payload_unknown)
    assert response.status_code == 201
    assert response.json()["recorded"]["distance_cm"] is None
    print("[PASS] Test 4: POST /api/readings handled 'unknown' reading safely with distance null")

    # Test 5: Reject invalid payload (status = 'invalid_state')
    payload_bad_status = {
        "device_id": "blind-stick-01",
        "distance_cm": 50.0,
        "status": "invalid_state"
    }
    response = client.post("/api/readings", json=payload_bad_status)
    assert response.status_code == 422, f"Expected 422, got {response.status_code}"
    print("[PASS] Test 5: POST /api/readings correctly rejected invalid status (HTTP 422)")

    # Test 6: Reject out-of-range distance (> 400 cm)
    payload_out_of_range = {
        "device_id": "blind-stick-01",
        "distance_cm": 550.0,
        "status": "valid"
    }
    response = client.post("/api/readings", json=payload_out_of_range)
    assert response.status_code == 422, f"Expected 422, got {response.status_code}"
    print("[PASS] Test 6: POST /api/readings correctly rejected distance out of physical range (HTTP 422)")

    # Test 7: GET /api/readings with limit
    response = client.get("/api/readings?limit=10")
    assert response.status_code == 200
    readings_list = response.json()
    assert readings_list["count"] >= 3
    print(f"[PASS] Test 7: GET /api/readings returned {readings_list['count']} chronological records")

    # Test 8: GET /api/latest
    response = client.get("/api/latest?device_id=blind-stick-01")
    assert response.status_code == 200
    latest = response.json()
    assert latest["reading"] is not None
    assert latest["reading"]["device_id"] == "blind-stick-01"
    print("[PASS] Test 8: GET /api/latest returned correct latest record")

    # Test 9: Verify direct SQLite database file persistence
    db_file = get_db_path()
    assert os.path.exists(db_file), f"Database file {db_file} does not exist!"
    conn = get_connection()
    count = conn.execute("SELECT COUNT(*) FROM sensor_readings;").fetchone()[0]
    conn.close()
    assert count >= 3, f"Expected >= 3 rows in database, found {count}"
    print(f"[PASS] Test 9: SQLite persistence verified in '{db_file}' (Row count: {count})")

    # Test 10: Verify frontend dashboard static route
    response = client.get("/")
    assert response.status_code == 200
    assert "Smart Blind Stick" in response.text
    print("[PASS] Test 10: GET / successfully serves real-time dashboard HTML")

    print("\n==================================================")
    print(" All Backend & Database Tests PASSED Successfully! ")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
