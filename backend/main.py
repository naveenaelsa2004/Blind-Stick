"""
FastAPI Backend for IoT-Based Smart Blind Stick.
Provides REST API endpoints for telemetry ingestion, querying, and serves the real-time dashboard.
"""

import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Query, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator, model_validator

from database import (
    check_db_health,
    get_connection,
    get_db_path,
    get_latest_reading,
    get_recent_readings,
    init_db,
    insert_reading,
)

# Ensure database schema is ready immediately on import as well as lifespan
init_db()

# Optional API Key for securing cloud telemetry ingestion (configured via environment or render.yaml)
API_KEY = os.getenv("API_KEY", "").strip()

# -----------------------------------------------------------------------------
# Lifespan Context Manager (Initializes DB on startup)
# -----------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQLite schema and indices
    init_db()
    yield


# -----------------------------------------------------------------------------
# FastAPI Application Configuration
# -----------------------------------------------------------------------------
app = FastAPI(
    title="IoT Smart Blind Stick Telemetry API",
    description="Containerized backend API collecting HC-SR04 obstacle distance data from ESP32",
    version="1.0.0",
    lifespan=lifespan,
)

# Enable CORS for local development flexibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------------------------------------------
# Pydantic Request Validation Models
# -----------------------------------------------------------------------------
class SensorReadingPayload(BaseModel):
    device_id: str = Field(..., min_length=1, max_length=64, description="Unique identifier of the ESP32 device")
    distance_cm: Optional[float] = Field(None, description="Measured obstacle distance in centimeters (2.0 to 400.0)")
    status: str = Field(..., description="Sensor reading status: 'valid' or 'unknown'")

    @field_validator("device_id")
    @classmethod
    def validate_device_id(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("device_id cannot be blank or whitespace")
        return trimmed

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        normalized = v.strip().lower()
        if normalized not in ("valid", "unknown"):
            raise ValueError("status must be either 'valid' or 'unknown'")
        return normalized

    @model_validator(mode="after")
    def validate_distance_for_status(self):
        if self.status == "valid":
            if self.distance_cm is None:
                raise ValueError("distance_cm must be provided when status is 'valid'")
            if self.distance_cm < 2.0 or self.distance_cm > 400.0:
                raise ValueError(
                    f"distance_cm ({self.distance_cm}) is outside valid HC-SR04 physical range [2.0, 400.0] cm"
                )
            self.distance_cm = round(self.distance_cm, 2)
        elif self.status == "unknown":
            # For unknown status, ensure distance is None so fake distances are never stored
            self.distance_cm = None
        return self


# -----------------------------------------------------------------------------
# API Endpoints
# -----------------------------------------------------------------------------
@app.get("/api/health", tags=["Health"])
async def get_health() -> Dict[str, Any]:
    """
    Health check endpoint returning system status and verifying database connectivity.
    """
    db_ok = check_db_health()
    if not db_ok:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "database": "disconnected",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "version": "1.0.0",
            },
        )

    return {
        "status": "healthy",
        "database": "connected",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0",
    }


@app.post("/api/readings", status_code=status.HTTP_201_CREATED, tags=["Readings"])
async def post_reading(payload: SensorReadingPayload, request: Request) -> Dict[str, Any]:
    """
    Accepts telemetry readings from ESP32, validates payload, and persists to SQLite.
    Verifies x-api-key if API_KEY is configured on the backend.
    """
    # Enforce API Key authentication if configured on Render / environment
    if API_KEY:
        provided_key = request.headers.get("x-api-key") or request.query_params.get("api_key")
        if provided_key != API_KEY:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing API key. Please provide 'x-api-key' header.",
            )

    try:
        inserted_id = insert_reading(
            device_id=payload.device_id,
            distance_cm=payload.distance_cm,
            status=payload.status,
        )
        return {
            "success": True,
            "id": inserted_id,
            "message": "Sensor reading recorded successfully",
            "recorded": {
                "device_id": payload.device_id,
                "distance_cm": payload.distance_cm,
                "status": payload.status,
            },
        }
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record sensor reading: {str(exc)}",
        )


@app.get("/api/readings", tags=["Readings"])
async def get_readings(
    limit: int = Query(50, ge=1, le=500, description="Max number of readings to return"),
    device_id: Optional[str] = Query(None, description="Filter by device identifier"),
) -> Dict[str, Any]:
    """
    Returns recent readings in chronological ascending order (oldest to newest),
    ideal for graphing time-series data without overloading client memory.
    """
    try:
        readings = get_recent_readings(limit=limit, device_id=device_id)
        return {
            "count": len(readings),
            "limit": limit,
            "device_id": device_id,
            "readings": readings,
        }
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to query readings: {str(exc)}",
        )


@app.get("/api/latest", tags=["Readings"])
async def get_latest(
    device_id: Optional[str] = Query(None, description="Filter by device identifier"),
) -> Dict[str, Any]:
    """
    Returns the single most recent reading for the specified device (or overall).
    Includes a staleness evaluation flag (stale if > 5 seconds old).
    """
    try:
        reading = get_latest_reading(device_id=device_id)
        if not reading:
            return {
                "reading": None,
                "is_stale": True,
                "message": "No sensor readings recorded yet",
            }

        # Calculate if reading is stale (more than 5 seconds old)
        is_stale = False
        try:
            ts_str = reading["timestamp"]
            ts = datetime.fromisoformat(ts_str)
            now = datetime.now(timezone.utc)
            delta = (now - ts).total_seconds()
            is_stale = delta > 5.0
        except Exception:
            is_stale = False

        return {
            "reading": reading,
            "is_stale": is_stale,
            "age_seconds": round(delta, 1) if "delta" in locals() else None,
        }
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to query latest reading: {str(exc)}",
        )


# -----------------------------------------------------------------------------
# Static Files & Frontend Mount
# -----------------------------------------------------------------------------
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.get("/", include_in_schema=False)
    async def serve_index():
        index_file = os.path.join(static_dir, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return {"message": "IoT Smart Blind Stick API is running. Static index.html not found."}


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    print(f"Starting Smart Blind Stick backend server on http://{host}:{port}")
    uvicorn.run("main:app", host=host, port=port, reload=True)
