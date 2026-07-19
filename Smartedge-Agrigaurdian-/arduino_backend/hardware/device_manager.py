"""
SmartEdge AgriGuardian — Device Manager
=========================================
hardware/device_manager.py

The SINGLE point of contact between Python (Linux / QRB2210) and the
STM32U585 MCU via the official Arduino Bridge (arduino-router).

Official Arduino UNO Q Communication Model
-------------------------------------------
  - The STM32U585 MCU runs an Arduino Sketch (Zephyr OS).
  - The sketch registers hardware functions via Bridge.provide("name", fn).
  - On the Linux side, the `arduino-router` daemon manages the internal UART
    link and exposes it as a Unix domain socket.
  - Python calls MCU functions by sending MessagePack-RPC messages to that socket.

  Wire format:
    Request  → [type=0, msg_id, "method_name", [params...]]
    Response → [type=1, msg_id, error, result]

  Socket path: /var/run/arduino-router.sock  (Linux side, on the UNO Q board)

  ⚠ NEVER open /dev/ttyHS1 directly.
  ⚠ NEVER use custom UART/serial protocols.
  ⚠ This is the ONLY file in the project that will contain socket code.

Current State: STUB
--------------------
  Hardware communication is NOT yet activated.
  All public functions return mock/safe defaults.

  When you confirm Arduino Bridge integration should begin:
    1. pip install msgpack
    2. Implement call() using socket.AF_UNIX + msgpack.packb/unpackb
    3. Implement is_alive() with a probe connection
    4. Nothing else in the project needs to change.
"""

import logging
from typing import Any, Optional

from config import ROUTER_SOCKET_PATH, BRIDGE_CALL_TIMEOUT_SEC, DEVICE_NAME

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Hardware mode flag
# Set to True ONLY after Arduino Bridge integration is confirmed and tested.
# ─────────────────────────────────────────────────────────────────────────────
_HARDWARE_ENABLED: bool = True


def call(method: str, *params: Any) -> Optional[Any]:
    """
    Invoke a function registered on the STM32 MCU via Bridge.provide().

    Connects to arduino-router Unix socket at ROUTER_SOCKET_PATH,
    sends a MessagePack-RPC request, and returns the decoded result.

    Args:
        method: RPC method name (must match Bridge.provide("name", ...) in sketch).
        *params: Arguments passed through to the MCU function.

    Returns:
        MCU function return value.

    Raises:
        RuntimeError: If the call fails, times out, or socket is unavailable.
    """
    if not _HARDWARE_ENABLED:
        logger.debug(
            "[DEVICE STUB] call('%s', %s) — hardware not yet enabled", method, params
        )
        return None

    import socket
    import msgpack

    if not hasattr(socket, "AF_UNIX"):
        raise RuntimeError(
            "Unix domain sockets (AF_UNIX) are not supported on this platform. "
            "The official Arduino Bridge RPC communication only runs on the Arduino UNO Q Linux environment."
        )

    # MessagePack-RPC Request: [type=0, msg_id=1, method_name, [params]]
    # We use a static msg_id or simple counter. Since we are synchronous per call, 1 is fine.
    msg_id = 1
    payload = msgpack.packb([0, msg_id, method, list(params)], use_bin_type=True)

    try:
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.settimeout(BRIDGE_CALL_TIMEOUT_SEC)
        client.connect(ROUTER_SOCKET_PATH)
        client.sendall(payload)

        # Unpack the response
        unpacker = msgpack.Unpacker(raw=False)
        while True:
            chunk = client.recv(4096)
            if not chunk:
                raise RuntimeError(
                    f"Bridge socket closed before receiving full response for '{method}'"
                )
            unpacker.feed(chunk)
            for response in unpacker:
                # MessagePack-RPC Response: [type=1, msg_id, error, result]
                if not isinstance(response, (list, tuple)) or len(response) != 4:
                    raise RuntimeError(
                        f"Malformed RPC response from MCU: {response!r}"
                    )
                _, resp_id, error, result = response
                if resp_id != msg_id:
                    logger.warning(
                        "RPC msg_id mismatch: sent %d, got %d", msg_id, resp_id
                    )
                if error is not None:
                    raise RuntimeError(
                        f"Bridge RPC error from MCU for '{method}': {error}"
                    )
                return result
    except FileNotFoundError:
        raise RuntimeError(
            f"arduino-router socket not found at '{ROUTER_SOCKET_PATH}'. "
            "Ensure the arduino-router service is running on the Arduino UNO Q: "
            "`systemctl status arduino-router`"
        )
    except socket.timeout:
        raise RuntimeError(
            f"Bridge RPC call '{method}' timed out after {BRIDGE_CALL_TIMEOUT_SEC}s."
        )
    except ConnectionRefusedError:
        raise RuntimeError(
            f"Connection refused by arduino-router on '{ROUTER_SOCKET_PATH}'. "
            "Try restarting the service: `systemctl restart arduino-router`"
        )
    except Exception as exc:
        raise RuntimeError(f"Bridge RPC call failed: {exc}")
    finally:
        try:
            client.close()
        except Exception:
            pass


def is_alive() -> bool:
    """
    Check whether the arduino-router service is reachable.

    Returns True only when hardware is enabled AND the socket is available.
    """
    if not _HARDWARE_ENABLED:
        return False

    import socket
    if not hasattr(socket, "AF_UNIX"):
        return False

    try:
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.settimeout(1.0)
        s.connect(ROUTER_SOCKET_PATH)
        s.close()
        return True
    except Exception:
        return False


def get_info() -> dict:
    """
    Returns device identity and bridge connectivity status.
    Used by system_service to build /health and /status responses.
    """
    alive = is_alive()
    return {
        "device":      DEVICE_NAME,
        "connected":   alive,
        "mode":        "hardware" if alive else "mock",
        "socket_path": ROUTER_SOCKET_PATH,
    }

