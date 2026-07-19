"""
SmartEdge AgriGuardian — Pump Service
=======================================
services/pump_service.py

Business logic layer for pump/relay control.

Responsibilities:
  - Validate and clamp duration_sec against the safety cap
  - Manage the auto-off timer (threading.Timer)
  - Track and expose pump state for other services (e.g. sensor_service)
  - Delegate all physical relay commands to hardware/pump_manager

This service contains NO hardware knowledge.
It does NOT know about GPIO pins, MCU methods, or bridge sockets.
All hardware interaction is delegated to hardware/pump_manager.py.
"""

import logging
import threading
from typing import Dict, Optional

from hardware import pump_manager
from config import MAX_PUMP_ON_SEC

logger = logging.getLogger(__name__)

# Auto-off timer handle (one global timer — only one pump activation at a time)
_auto_off_timer: Optional[threading.Timer] = None
_timer_lock = threading.Lock()


# ─────────────────────────────────────────────────────────────────────────────
# Internal: auto-off callback
# ─────────────────────────────────────────────────────────────────────────────

def _auto_off_callback() -> None:
    """Fired by the threading.Timer when auto-off duration expires."""
    global _auto_off_timer
    logger.info("pump_service: auto-off timer expired — deactivating pump")
    try:
        pump_manager.deactivate()
    except Exception as exc:
        logger.error("pump_service: hardware deactivate failed during auto-off: %s", exc)
    with _timer_lock:
        _auto_off_timer = None


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def turn_pump_on(duration_sec: Optional[int] = None) -> Dict:
    """
    Turns the pump ON via pump_manager and schedules an auto-off timer.

    The duration is always clamped to MAX_PUMP_ON_SEC (from config.py).
    If no duration is given, MAX_PUMP_ON_SEC is used as the default.
    Any existing auto-off timer is cancelled before the new one is started.

    Args:
        duration_sec: Optional number of seconds before auto-off.

    Returns:
        {"pump": True, "auto_off_in_sec": int}

    Raises:
        RuntimeError: Propagated from pump_manager if hardware command fails.
    """
    global _auto_off_timer

    # Clamp / default
    effective = min(
        int(duration_sec) if duration_sec is not None else MAX_PUMP_ON_SEC,
        MAX_PUMP_ON_SEC,
    )

    # Cancel any existing timer before starting a new activation
    with _timer_lock:
        if _auto_off_timer is not None:
            _auto_off_timer.cancel()
            _auto_off_timer = None

    # Delegate hardware command
    pump_manager.activate()

    # Schedule auto-off
    with _timer_lock:
        _auto_off_timer = threading.Timer(effective, _auto_off_callback)
        _auto_off_timer.daemon = True
        _auto_off_timer.start()

    logger.info("pump_service: pump ON — auto-off in %ds", effective)
    return {"pump": True, "auto_off_in_sec": effective}


def turn_pump_off() -> Dict:
    """
    Turns the pump OFF immediately via pump_manager.
    Cancels any pending auto-off timer.

    Returns:
        {"pump": False}

    Raises:
        RuntimeError: Propagated from pump_manager if hardware command fails.
    """
    global _auto_off_timer

    with _timer_lock:
        if _auto_off_timer is not None:
            _auto_off_timer.cancel()
            _auto_off_timer = None

    pump_manager.deactivate()

    logger.info("pump_service: pump OFF")
    return {"pump": False}


def get_pump_state() -> bool:
    """
    Returns the current pump state without issuing any hardware command.
    Reads directly from pump_manager (hardware or in-memory state).
    """
    return pump_manager.get_state()
