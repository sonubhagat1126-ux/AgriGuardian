"""
SmartEdge AgriGuardian — Bridge Service (Stub)
===============================================
services/bridge_service.py

This module is the ONLY place that will communicate with the Arduino
UNO Q hardware via the official Arduino Bridge (RPC over arduino-router).

Current state: STUB — returns mock connectivity data.
No real hardware calls are made yet.

─────────────────────────────────────────────────────────────────────────
  HOW TO ACTIVATE REAL BRIDGE COMMUNICATION (do this when confirmed):
  1. Install msgpack:  pip install msgpack
  2. Replace call() with a real unix-socket + MessagePack-RPC client.
  3. The arduino-router service on the board manages /var/run/arduino-router.sock
  4. Never open /dev/ttyHS1 directly — it is reserved by arduino-router.
─────────────────────────────────────────────────────────────────────────

The public API of this module (call, is_bridge_alive) must not change
when real hardware is connected — only the internals change.
"""

import logging
from typing import Any, Optional

from config import ROUTER_SOCKET_PATH, BRIDGE_CALL_TIMEOUT_SEC

logger = logging.getLogger(__name__)


def call(method: str, *params: Any) -> Optional[Any]:
    """
    [STUB] Invoke a function registered on the MCU via Bridge.provide().

    When Bridge integration is active, this will:
      - Connect to the unix socket at ROUTER_SOCKET_PATH
      - Send a MessagePack-RPC request: [0, msg_id, method, params]
      - Receive and decode the response: [1, msg_id, error, result]
      - Return the result value

    Args:
        method: The RPC method name matching Bridge.provide("name", ...) in sketch.
        *params: Arguments forwarded to the sketch function.

    Returns:
        None  ← stub always returns None (no real MCU call made yet)
    """
    logger.debug(
        "[BRIDGE STUB] call('%s', %s) — no hardware call made (stub mode)", method, params
    )
    return None


def is_bridge_alive() -> bool:
    """
    [STUB] Returns False — arduino-router socket not available on dev machine.

    When Bridge integration is active, this will attempt a connection to
    ROUTER_SOCKET_PATH and return True only if the router service is reachable.
    """
    return False


def get_bridge_status() -> dict:
    """
    Returns the current bridge connectivity status for use in /status responses.
    """
    alive = is_bridge_alive()
    return {
        "bridge_connected": alive,
        "socket_path": ROUTER_SOCKET_PATH,
        "mode": "hardware" if alive else "mock",
    }
