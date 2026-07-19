"""
SmartEdge AgriGuardian — Arduino Bridge Client
===============================================
Thin, thread-safe wrapper around the arduino-router Unix domain socket.

The arduino-router daemon (running on the QRB2210 Linux side) manages the
internal UART link to the STM32U585 MCU and exposes it as a Unix socket
using the MessagePack-RPC wire protocol.

This module provides:
    call(method, *params)    — Invoke a function registered via Bridge.provide()
                               in the Arduino sketch. Returns the result value.
    is_bridge_alive()        — Quick liveness check for the router socket.

Wire Protocol (MessagePack-RPC):
    Request  → [type=0, msg_id, method_name, [params]]
    Response → [type=1, msg_id, error, result]

References:
    https://msgpack.org/
    Arduino_RouterBridge library (by Arduino)

⚠  NEVER open /dev/ttyHS1 directly from Python — it is reserved for the
   arduino-router service. Only communicate via the Unix socket below.
"""

import socket
import threading
import logging
from typing import Any, Optional

import msgpack

from config import ROUTER_SOCKET_PATH, BRIDGE_CALL_TIMEOUT_SEC

logger = logging.getLogger(__name__)

# ── Thread Safety ─────────────────────────────────────────────────────────────
# The arduino-router socket is a single connection point. Multiple Flask
# request threads must not interleave their reads/writes on the socket.
# A reentrant lock serialises all RPC calls.
_socket_lock = threading.Lock()

# ── Message ID Counter ────────────────────────────────────────────────────────
# MessagePack-RPC requires a unique uint16 ID per in-flight request.
# Since we serialise with _socket_lock, IDs do not need to be globally unique
# across concurrent calls — but we increment anyway for clean logging.
_msg_id: int = 0
_msg_id_lock = threading.Lock()


def _next_id() -> int:
    """Returns the next monotonic message ID, wrapping at 0xFFFF."""
    global _msg_id
    with _msg_id_lock:
        _msg_id = (_msg_id + 1) & 0xFFFF
        return _msg_id


def call(method: str, *params: Any) -> Any:
    """
    Calls a function registered on the STM32 MCU via arduino-router RPC.

    The function must have been exposed in the Arduino sketch using:
        Bridge.provide("method_name", your_function);

    Args:
        method:  The RPC method name (matches the string in Bridge.provide).
        *params: Arguments forwarded to the sketch function, in order.

    Returns:
        The value returned by the sketch function (bool, int, float, str, etc.).

    Raises:
        RuntimeError: If the socket is unavailable, the call times out,
                      or the MCU returns an error.
    """
    msg_id = _next_id()

    # MessagePack-RPC Request: [type=0, msg_id, method, params_list]
    payload = msgpack.packb([0, msg_id, method, list(params)], use_bin_type=True)

    with _socket_lock:
        client: Optional[socket.socket] = None
        try:
            client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            client.settimeout(BRIDGE_CALL_TIMEOUT_SEC)
            client.connect(ROUTER_SOCKET_PATH)
            client.sendall(payload)

            # ── Receive full response ─────────────────────────────────────
            # Use msgpack.Unpacker for incremental decoding — handles cases
            # where the OS delivers the response in multiple TCP segments.
            unpacker = msgpack.Unpacker(raw=False)
            while True:
                chunk = client.recv(4096)
                if not chunk:
                    # Connection closed before we got a full response
                    raise RuntimeError(
                        f"Bridge connection closed mid-response for '{method}'"
                    )
                unpacker.feed(chunk)
                for response in unpacker:
                    # MessagePack-RPC Response: [type=1, msg_id, error, result]
                    if not isinstance(response, (list, tuple)) or len(response) != 4:
                        raise RuntimeError(
                            f"Unexpected bridge response format: {response!r}"
                        )
                    _, resp_id, error, result = response
                    if resp_id != msg_id:
                        logger.warning(
                            "Bridge msg_id mismatch: sent %d, got %d", msg_id, resp_id
                        )
                    if error is not None:
                        raise RuntimeError(
                            f"Bridge RPC error from MCU for '{method}': {error}"
                        )
                    logger.debug("Bridge call '%s' → %r", method, result)
                    return result

        except FileNotFoundError:
            raise RuntimeError(
                f"arduino-router socket not found at '{ROUTER_SOCKET_PATH}'. "
                "Ensure the arduino-router service is active: "
                "`systemctl status arduino-router`"
            )
        except socket.timeout:
            raise RuntimeError(
                f"Bridge call '{method}' timed out after {BRIDGE_CALL_TIMEOUT_SEC}s. "
                "Check that the Arduino sketch is running and Bridge.begin() was called."
            )
        except ConnectionRefusedError:
            raise RuntimeError(
                f"arduino-router refused connection on '{ROUTER_SOCKET_PATH}'. "
                "Try: `systemctl restart arduino-router`"
            )
        finally:
            if client:
                try:
                    client.close()
                except Exception:
                    pass


def is_bridge_alive() -> bool:
    """
    Quick liveness check: attempts to connect to the arduino-router socket.

    Returns:
        True  if the socket exists and accepts connections.
        False if the router is down, the socket is missing, or connection fails.
    """
    try:
        probe = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        probe.settimeout(1.0)
        probe.connect(ROUTER_SOCKET_PATH)
        probe.close()
        return True
    except Exception:
        return False
