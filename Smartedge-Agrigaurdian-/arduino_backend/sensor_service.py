"""
SmartEdge AgriGuardian — Sensor Service
========================================
Fetches live soil moisture and DHT22 (temperature + humidity) readings
from the STM32 MCU by calling the 'read_sensors' RPC function via
the Arduino Bridge.

The MCU-side function (registered in the sketch as Bridge.provide) returns
a compact JSON string containing all sensor values in a single call,
minimising round-trips over the bridge.

Expected MCU response JSON:
    {
        "moisture": 490,          ← raw ADC value (0–1023)
        "temperature": 29.5,      ← °C from DHT22
        "humidity": 63.2,         ← % relative humidity from DHT22
        "dht_error": false        ← true if DHT22 failed to respond
    }

This service:
    - Converts raw ADC to soil moisture percentage using calibrated constants
    - Validates DHT22 readings and raises informative errors on failure
    - Returns synthetic data when SIMULATE=true (dev machine testing)
"""

import json
import logging
import random
from datetime import datetime
from typing import Dict, Any

import bridge_client
from config import (
    SIMULATE,
    MOISTURE_DRY_ADC,
    MOISTURE_WET_ADC,
)

logger = logging.getLogger(__name__)


def _adc_to_moisture_pct(raw_adc: int) -> float:
    """
    Converts a raw 10-bit ADC value to soil moisture percentage (0–100%).

    The mapping is linear between the calibrated dry (MOISTURE_DRY_ADC) and
    wet (MOISTURE_WET_ADC) reference points defined in config.py.

    Values are clamped to [0, 100] to handle out-of-range ADC readings
    (e.g., sensor not connected or partially submerged).

    Args:
        raw_adc: Integer ADC reading from the STM32 (0–1023).

    Returns:
        Soil moisture percentage as a float, clamped to 0.0–100.0.
    """
    if MOISTURE_DRY_ADC == MOISTURE_WET_ADC:
        # Guard against division-by-zero from misconfiguration
        logger.warning(
            "MOISTURE_DRY_ADC == MOISTURE_WET_ADC (%d). Check config.py calibration.",
            MOISTURE_DRY_ADC,
        )
        return 0.0

    pct = (MOISTURE_DRY_ADC - raw_adc) / (MOISTURE_DRY_ADC - MOISTURE_WET_ADC) * 100.0
    return round(max(0.0, min(100.0, pct)), 1)


def get_sensor_data() -> Dict[str, Any]:
    """
    Returns a dictionary of current sensor readings.

    Calls the 'read_sensors' function on the STM32 MCU via Arduino Bridge RPC,
    parses the JSON response, converts raw ADC to moisture %, and validates
    DHT22 sensor integrity.

    Returns:
        {
            "moisture_pct":       float,   ← 0.0–100.0 (converted from ADC)
            "raw_moisture_adc":   int,     ← raw ADC value (useful for calibration)
            "temperature_c":      float,   ← °C from DHT22
            "humidity_pct":       float,   ← % relative humidity from DHT22
            "timestamp":          str,     ← ISO-8601 timestamp of this reading
            "source":             str      ← "stm32_bridge" or "simulate"
        }

    Raises:
        RuntimeError: If the bridge call fails, the MCU response is malformed,
                      or the DHT22 sensor reports an error.
    """
    # ── Simulate mode (dev machine, no real hardware) ──────────────────────
    if SIMULATE:
        return _simulate_sensor_data()

    # ── Real hardware path ─────────────────────────────────────────────────
    # Call the MCU function registered as Bridge.provide("read_sensors", ...)
    logger.debug("Calling Bridge RPC: read_sensors")
    raw_result = bridge_client.call("read_sensors")

    # The sketch returns a JSON string (String type in Arduino C++)
    if raw_result is None:
        raise RuntimeError(
            "'read_sensors' returned None from MCU. "
            "Verify the sketch is uploaded and Bridge.begin() completed successfully."
        )

    # Decode bytes → str if necessary (msgpack may deliver as bytes)
    if isinstance(raw_result, (bytes, bytearray)):
        raw_result = raw_result.decode("utf-8")

    # Parse JSON
    try:
        data: Dict[str, Any] = json.loads(raw_result)
    except (json.JSONDecodeError, TypeError) as exc:
        raise RuntimeError(
            f"Failed to parse 'read_sensors' response as JSON. "
            f"Raw value: {raw_result!r}. Error: {exc}"
        )

    # ── DHT22 validation ───────────────────────────────────────────────────
    if data.get("dht_error", False):
        raise RuntimeError(
            "DHT22 sensor returned an error. "
            "Check wiring: DATA pin must be connected to D2 on the MCU, "
            "with a 10kΩ pull-up resistor between DATA and 3.3V."
        )

    # ── Extract and validate fields ────────────────────────────────────────
    try:
        raw_adc     = int(data["moisture"])
        temperature = float(data["temperature"])
        humidity    = float(data["humidity"])
    except (KeyError, TypeError, ValueError) as exc:
        raise RuntimeError(
            f"'read_sensors' response missing expected fields. "
            f"Received: {data}. Error: {exc}"
        )

    return {
        "moisture_pct":     _adc_to_moisture_pct(raw_adc),
        "raw_moisture_adc": raw_adc,
        "temperature_c":    round(temperature, 1),
        "humidity_pct":     round(humidity, 1),
        "timestamp":        datetime.now().isoformat(timespec="seconds"),
        "source":           "stm32_bridge",
    }


def _simulate_sensor_data() -> Dict[str, Any]:
    """
    Returns realistic synthetic sensor data for development/testing.
    Only called when SIMULATE=true in the environment.
    """
    raw_adc = random.randint(MOISTURE_WET_ADC, MOISTURE_DRY_ADC)
    return {
        "moisture_pct":     _adc_to_moisture_pct(raw_adc),
        "raw_moisture_adc": raw_adc,
        "temperature_c":    round(random.uniform(24.0, 38.0), 1),
        "humidity_pct":     round(random.uniform(45.0, 85.0), 1),
        "timestamp":        datetime.now().isoformat(timespec="seconds"),
        "source":           "simulate",
    }
