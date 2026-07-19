"""
SmartEdge AgriGuardian — Pump Manager
=======================================
hardware/pump_manager.py

Hardware abstraction for the relay module and water pump on Arduino UNO Q.
This is the only file that knows about relay wiring and MCU function names.

Hardware:
  - Relay Module  → MCU digital pin D6 (active-LOW: LOW = pump ON)
  - Water Pump    → connected through relay NC/NO contacts

Communication:
  Relay state changes go through device_manager.call("set_pump", state).
  State queries go through device_manager.call("get_pump_state").

Current State: MOCK
  set_relay() logs the command but does not actuate any hardware.
  State is tracked in memory only.
  No MCU call is made until hardware is confirmed and device_manager activates.

Swap point:
  Replace the body of _set_relay() with device_manager.call().
  All state-tracking logic above it stays unchanged.
"""

import logging
import threading

from hardware import device_manager

logger = logging.getLogger(__name__)

# MCU RPC method names (must match Bridge.provide() calls in the sketch)
_MCU_METHOD_SET_PUMP       = "set_pump"
_MCU_METHOD_GET_PUMP_STATE = "get_pump_state"

# In-memory relay state (authoritative source when hardware is in mock mode)
_relay_on: bool = False
_relay_lock = threading.Lock()


# ─────────────────────────────────────────────────────────────────────────────
# Internal: relay actuator (the ONLY swap point for this file)
# ─────────────────────────────────────────────────────────────────────────────

def _set_relay(state: bool) -> None:
    """
    Sends the relay activation state command to the MCU via Arduino Bridge RPC.
    """
    result = device_manager.call(_MCU_METHOD_SET_PUMP, state)
    if result is None:
        raise RuntimeError("MCU did not acknowledge the set_pump command")



# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def activate() -> bool:
    """
    Energises the relay → water pump starts.

    Returns:
        True if the command was accepted (always True in mock mode).

    Raises:
        RuntimeError: If the MCU rejects the command (hardware mode only).
    """
    global _relay_on
    _set_relay(True)
    with _relay_lock:
        _relay_on = True
    logger.debug("Pump manager: relay activated")
    return True


def deactivate() -> bool:
    """
    De-energises the relay → water pump stops.

    Returns:
        True if the command was accepted (always True in mock mode).

    Raises:
        RuntimeError: If the MCU rejects the command (hardware mode only).
    """
    global _relay_on
    _set_relay(False)
    with _relay_lock:
        _relay_on = False
    logger.debug("Pump manager: relay deactivated")
    return True


def get_state() -> bool:
    """
    Returns the current relay state by querying the MCU via the Arduino Bridge RPC.
    Falls back to the local tracking state if the bridge query returns None.
    """
    try:
        mcu_state = device_manager.call(_MCU_METHOD_GET_PUMP_STATE)
        if mcu_state is not None:
            return bool(mcu_state)
    except Exception as exc:
        logger.warning("Failed to query pump state from MCU: %s. Falling back to local state.", exc)
    
    with _relay_lock:
        return _relay_on

