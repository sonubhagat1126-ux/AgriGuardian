"""
SmartEdge AgriGuardian — hardware package
==========================================
The hardware layer is the only layer in the project that knows about:
  - MCU pin assignments
  - Arduino Bridge RPC method names
  - arduino-router socket communication

Nothing outside this package should import socket, msgpack, or /dev paths.
Routes and services interact with hardware exclusively through this package.
"""
