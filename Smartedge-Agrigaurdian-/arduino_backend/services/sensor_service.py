"""
SmartEdge AgriGuardian — Sensor Service
=========================================
services/sensor_service.py

Business logic layer for sensor data.

Responsibilities:
  - Request raw readings from hardware/sensor_manager (hardware abstraction)
  - Convert raw ADC values to meaningful engineering units (%)
  - Validate reading quality
  - Return a clean, API-ready dictionary to the route layer

This service contains NO hardware knowledge.
It does NOT know about ADC pins, MCU methods, or bridge sockets.
All hardware interaction is delegated to hardware/sensor_manager.py.
"""

import logging
from typing import Dict

from hardware import sensor_manager, pump_manager
from config import MOISTURE_DRY_ADC, MOISTURE_WET_ADC

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Internal: unit conversion
# ─────────────────────────────────────────────────────────────────────────────

def _adc_to_moisture_pct(raw_adc: int) -> float:
    """
    Converts a raw 10-bit ADC value (0–1023) to soil moisture percentage.

    Mapping is linear between calibrated dry and wet reference points.
    Output is clamped to [0.0, 100.0] to handle out-of-range readings.
    Calibration constants are set in config.py (MOISTURE_DRY_ADC / WET_ADC).
    """
    span = MOISTURE_DRY_ADC - MOISTURE_WET_ADC
    if span == 0:
        logger.warning("Moisture calibration span is 0 — check MOISTURE_DRY_ADC / WET_ADC in config.py")
        return 0.0
    pct = (MOISTURE_DRY_ADC - raw_adc) / span * 100.0
    return round(max(0.0, min(100.0, pct)), 1)


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def get_sensor_data() -> Dict:
    """
    Returns a complete, API-ready sensor snapshot.

    Calls hardware/sensor_manager for raw hardware values, applies business
    logic (unit conversion, validation), and merges the current pump state.

    Returns:
        {
            "soil_moisture": float,   ← 0.0–100.0 % (converted from ADC)
            "temperature":   float,   ← degrees Celsius
            "humidity":      float,   ← 0.0–100.0 %
            "pump":          bool,    ← current pump/relay state
        }

    Raises:
        RuntimeError: Propagated from sensor_manager if hardware read fails.
    """
    logger.debug("sensor_service: fetching raw readings from sensor_manager")

    raw = sensor_manager.get_raw_readings()

    return {
        "soil_moisture": _adc_to_moisture_pct(raw["moisture_adc"]),
        "temperature":   round(raw["temperature_c"], 1),
        "humidity":      round(raw["humidity_pct"], 1),
        "pump":          pump_manager.get_state(),
    }
