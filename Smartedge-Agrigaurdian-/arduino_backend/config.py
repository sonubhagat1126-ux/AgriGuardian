"""
SmartEdge AgriGuardian — Arduino UNO Q Backend
================================================
config.py  |  Central configuration — single source of truth.

All tunable constants live here. No magic numbers anywhere else.
To reconfigure the server (port, host, limits), change only this file.
"""

import os

# ── Flask Server ──────────────────────────────────────────────────────────────
FLASK_HOST: str = os.getenv("FLASK_HOST", "0.0.0.0")
FLASK_PORT: int = int(os.getenv("FLASK_PORT", "5001"))
FLASK_DEBUG: bool = os.getenv("FLASK_DEBUG", "true").lower() == "true"

# Device identity returned in /health and /status responses
DEVICE_NAME: str = "Arduino UNO Q"

# ── Soil Moisture Sensor Calibration ─────────────────────────────────────────
# Resistive / capacitive modules output an analog voltage mapped to 0–1023 ADC.
# Calibrate by recording the ADC value in dry air and in water.
# These constants are referenced by sensor_service.py only.
MOISTURE_DRY_ADC: int = int(os.getenv("MOISTURE_DRY_ADC", "780"))
MOISTURE_WET_ADC: int = int(os.getenv("MOISTURE_WET_ADC", "300"))

# ── Pump Safety Cap ───────────────────────────────────────────────────────────
# Maximum time (seconds) the pump may run in a single activation.
# The pump service enforces this even when no duration is given.
MAX_PUMP_ON_SEC: int = int(os.getenv("MAX_PUMP_ON_SEC", "300"))

# ── Arduino Bridge (future use) ───────────────────────────────────────────────
# These constants are NOT used yet — bridge_service.py is a stub until
# you confirm Arduino Bridge integration should begin.
ROUTER_SOCKET_PATH: str = "/var/run/arduino-router.sock"
BRIDGE_CALL_TIMEOUT_SEC: float = 5.0
