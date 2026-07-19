"""
SmartEdge AgriGuardian — System Service
=========================================
services/system_service.py

Business logic for system-level status and health reporting.

Provides:
  - Health summary (device identity + liveness)
  - Full status snapshot (uptime, pump state, bridge connectivity)

All hardware-level checks are delegated to hardware/device_manager.
All pump state queries are delegated to hardware/pump_manager.
This service has NO hardware knowledge of its own.
"""

import logging
import time
from typing import Dict

from hardware import device_manager, pump_manager
from config import DEVICE_NAME

logger = logging.getLogger(__name__)

# Server start time — used to calculate uptime
_START_TIME: float = time.time()


def get_health() -> Dict:
    """
    Lightweight liveness check response.

    Always succeeds as long as the Flask process is alive.
    Does NOT check bridge connectivity (would be too slow for a health probe).

    Returns:
        {"status": "ok", "device": "Arduino UNO Q"}
    """
    return {
        "status": "ok",
        "device": DEVICE_NAME,
    }


def get_status() -> Dict:
    """
    Full system status snapshot.

    Aggregates bridge connectivity, pump state, and uptime into one response.

    Returns:
        {
            "device":           str,    ← board name from config
            "uptime_sec":       float,  ← seconds since Flask started
            "pump_on":          bool,   ← current pump/relay state
            "bridge_connected": bool,   ← is arduino-router reachable?
            "bridge_mode":      str,    ← "hardware" | "mock"
        }
    """
    info = device_manager.get_info()

    return {
        "device":           info["device"],
        "uptime_sec":       round(time.time() - _START_TIME, 1),
        "pump_on":          pump_manager.get_state(),
        "bridge_connected": info["connected"],
        "bridge_mode":      info["mode"],
    }
