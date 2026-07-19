"""
SmartEdge AgriGuardian — Sensor Manager
=========================================
hardware/sensor_manager.py

Hardware abstraction for all sensor reads on the Arduino UNO Q.
This is the only file that knows about sensor wiring and MCU function names.

Sensors managed:
  - Soil Moisture Sensor  → MCU analog pin A0 (10-bit ADC, 0–1023)
  - DHT22                 → MCU digital pin D2 (temperature + humidity)

Communication:
  All reads go through device_manager.call("read_sensors").
  The MCU sketch returns a JSON string from the Bridge.provide() handler.

Expected MCU response when hardware is enabled:
  '{"moisture":490,"temperature":29.5,"humidity":63.2,"dht_error":false}'

Current State: MOCK
  get_raw_readings() returns hardcoded realistic values.
  No MCU call is made until hardware is confirmed and device_manager activates.

Swap point:
  Replace the body of _read_from_hardware() with device_manager.call().
  The rest of sensor_manager — and everything above it — stays unchanged.
"""

import json
import logging
from typing import Dict

from hardware import device_manager

logger = logging.getLogger(__name__)

# MCU RPC method name (must match Bridge.provide("read_sensors", ...) in sketch)
_MCU_METHOD_READ_SENSORS = "read_sensors"


# ─────────────────────────────────────────────────────────────────────────────
# Internal: hardware read (the ONLY swap point for this file)
# ─────────────────────────────────────────────────────────────────────────────

def _read_from_hardware() -> Dict:
    """
    Reads the raw sensor values from the MCU via the Arduino Bridge RPC method 'read_sensors'.

    Returns:
        A dictionary containing moisture_adc, temperature_c, and humidity_pct.
    """
    raw = device_manager.call(_MCU_METHOD_READ_SENSORS)
    if raw is None:
        raise RuntimeError("MCU returned None from 'read_sensors'")
    
    # MessagePack might return string or bytes
    raw_str = raw if isinstance(raw, str) else raw.decode("utf-8")
    
    try:
        data = json.loads(raw_str)
    except (json.JSONDecodeError, TypeError) as exc:
        raise RuntimeError(f"Failed to parse 'read_sensors' payload as JSON: {exc}. Raw payload: {raw_str!r}")

    if data.get("dht_error", False):
        raise RuntimeError(
            "DHT22 sensor reported an error on the MCU side. Check sensor connection on D2."
        )

    try:
        return {
            "moisture_adc": int(data["moisture"]),
            "temperature_c": float(data["temperature"]),
            "humidity_pct":  float(data["humidity"]),
        }
    except (KeyError, ValueError, TypeError) as exc:
        raise RuntimeError(f"Sensor payload from MCU was malformed: {exc}. Data received: {data}")



# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def get_raw_readings() -> Dict:
    """
    Returns raw sensor readings from the MCU (or mock values in stub mode).

    Returns:
        {
            "moisture_adc": int,    ← raw ADC 0–1023 (convert to % in service)
            "temperature_c": float, ← degrees Celsius
            "humidity_pct":  float, ← 0.0–100.0 %
        }

    Raises:
        RuntimeError: If the hardware read fails (only when hardware is active).
    """
    return _read_from_hardware()
