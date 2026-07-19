"""
SmartEdge AgriGuardian — Sensor Routes
========================================
routes/sensor_routes.py

Registers:
    GET /sensor  — Returns live sensor readings + current pump state.

The route layer is intentionally thin:
  - It calls service functions only.
  - It merges pump state into the sensor payload (services stay single-purpose).
  - All business logic lives in services/; routes only handle HTTP concerns.
"""

import logging
from flask import Blueprint, jsonify

from services import sensor_service, pump_service

logger = logging.getLogger(__name__)

sensor_bp = Blueprint("sensor", __name__)


@sensor_bp.get("/sensor")
def get_sensor():
    """
    Returns the latest sensor readings merged with the current pump state.

    Success (200):
        {
            "soil_moisture": 45.0,
            "temperature":   29.3,
            "humidity":      65.2,
            "pump":          false
        }

    Error (503): Sensor read failed (only relevant when hardware is active).
        {"error": "sensor_unavailable", "detail": "..."}
    """
    try:
        data = sensor_service.get_sensor_data()

        # Merge pump state here so sensor_service stays hardware-only
        data["pump"] = pump_service.get_pump_state()

        return jsonify(data), 200

    except RuntimeError as exc:
        logger.error("Sensor read failed: %s", exc)
        return jsonify({"error": "sensor_unavailable", "detail": str(exc)}), 503
