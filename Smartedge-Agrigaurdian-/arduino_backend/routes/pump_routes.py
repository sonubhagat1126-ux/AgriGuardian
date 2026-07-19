"""
SmartEdge AgriGuardian — Pump Routes
======================================
routes/pump_routes.py

Registers:
    POST /pump/on   — Turn the water pump ON (optional duration_sec in body).
    POST /pump/off  — Turn the water pump OFF immediately.

Body for /pump/on (optional):
    Content-Type: application/json
    {"duration_sec": 60}

If duration_sec is omitted, the server-side safety cap (MAX_PUMP_ON_SEC)
is used automatically. Values exceeding the cap are silently clamped.
"""

import logging
from flask import Blueprint, jsonify, request

from services import pump_service

logger = logging.getLogger(__name__)

pump_bp = Blueprint("pump", __name__)


@pump_bp.post("/pump/on")
def pump_on():
    """
    Turns the water pump ON.

    Success (200):
        {"pump": true, "auto_off_in_sec": 300}

    Error (400): Invalid duration_sec value.
        {"error": "invalid_duration", "detail": "..."}

    Error (503): Relay control failed (only relevant when hardware is active).
        {"error": "pump_control_failed", "detail": "..."}
    """
    body = request.get_json(silent=True) or {}
    duration_sec = body.get("duration_sec")

    # Validate duration_sec if provided
    if duration_sec is not None:
        try:
            duration_sec = int(duration_sec)
            if duration_sec <= 0:
                raise ValueError("Must be a positive integer")
        except (TypeError, ValueError) as exc:
            return jsonify({"error": "invalid_duration", "detail": str(exc)}), 400

    try:
        result = pump_service.turn_pump_on(duration_sec=duration_sec)
        return jsonify(result), 200
    except RuntimeError as exc:
        logger.error("Pump ON failed: %s", exc)
        return jsonify({"error": "pump_control_failed", "detail": str(exc)}), 503


@pump_bp.post("/pump/off")
def pump_off():
    """
    Turns the water pump OFF immediately, cancelling any auto-off timer.

    Success (200):
        {"pump": false}

    Error (503): Relay control failed (only relevant when hardware is active).
        {"error": "pump_control_failed", "detail": "..."}
    """
    try:
        result = pump_service.turn_pump_off()
        return jsonify(result), 200
    except RuntimeError as exc:
        logger.error("Pump OFF failed: %s", exc)
        return jsonify({"error": "pump_control_failed", "detail": str(exc)}), 503
