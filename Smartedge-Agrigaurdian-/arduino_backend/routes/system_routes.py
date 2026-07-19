"""
SmartEdge AgriGuardian — System Routes
========================================
routes/system_routes.py

Registers:
    GET /health  — Lightweight liveness probe (Flutter ping / health-check).
    GET /status  — Full system status (pump, bridge, uptime, mode).

Routes delegate entirely to system_service.
No business logic lives here.
"""

import logging
from flask import Blueprint, jsonify

from services import system_service

logger = logging.getLogger(__name__)

system_bp = Blueprint("system", __name__)


@system_bp.get("/health")
def health():
    """
    Liveness check — always 200 if the server is running.

    Flutter calls this first to verify the Arduino UNO Q is reachable
    before loading the dashboard.

    Response (200):
        {"status": "ok", "device": "Arduino UNO Q"}
    """
    return jsonify(system_service.get_health()), 200


@system_bp.get("/status")
def status():
    """
    Full system status snapshot for the Flutter status panel.

    Response (200):
        {
            "device":           "Arduino UNO Q",
            "uptime_sec":       1234.5,
            "pump_on":          false,
            "bridge_connected": false,
            "bridge_mode":      "mock"
        }
    """
    return jsonify(system_service.get_status()), 200
