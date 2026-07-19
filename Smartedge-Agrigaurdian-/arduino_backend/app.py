"""
SmartEdge AgriGuardian — Arduino UNO Q Central Server
=======================================================
app.py  |  Flask application factory + entry point

The Arduino UNO Q is the MAIN SERVER for the entire AgriGuardian system.
The Flutter Android app communicates ONLY with this server over WiFi.

Architecture (top to bottom):
    Flutter App  ──HTTP──▶  Flask (this file)
                                 │
                          ┌──────┴───────┐
                      routes/       routes/
                   sensor_routes  pump_routes  system_routes
                          │
                       services/
                  sensor_service  pump_service  system_service
                          │
                       hardware/
                  sensor_manager  pump_manager  device_manager
                          │
                   [arduino-router]  ← official Arduino Bridge daemon
                          │
                   STM32U585 MCU    ← Arduino Sketch (Bridge.provide)
                          │
                 Sensors + Relay + Pump

Future modules (reserved, not yet active):
    modules/ai, knowledge_base, weather, leaf_detection, sarvam_ai, analytics
    Each module registers its own Blueprint below when activated.

Run locally (dev / testing):
    cd arduino_backend
    python app.py
    → http://localhost:5001

Deploy on Arduino UNO Q:
    python3 app.py
    → http://<board-wifi-ip>:5001
"""

import logging
import sys
import os

from flask import Flask
from flask_cors import CORS

# Ensure arduino_backend/ is on sys.path for relative imports
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from routes.sensor_routes import sensor_bp
from routes.pump_routes import pump_bp
from routes.system_routes import system_bp
from config import FLASK_HOST, FLASK_PORT, FLASK_DEBUG, DEVICE_NAME

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG if FLASK_DEBUG else logging.INFO,
    format="%(asctime)s  [%(levelname)-8s]  %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


# ── App Factory ───────────────────────────────────────────────────────────────

def create_app() -> Flask:
    """
    Creates and fully configures the Flask application.

    Blueprint registration order:
      1. Core API blueprints (sensor, pump, system) — always active
      2. Module blueprints — registered here when each phase is activated

    CORS is enabled for all origins so Flutter can reach the board
    from any IP without browser/app security blocks.
    """
    app = Flask(__name__)
    CORS(app)

    # ── Core blueprints (Phase 1 + 2) ────────────────────────────────────────
    app.register_blueprint(sensor_bp)
    app.register_blueprint(pump_bp)
    app.register_blueprint(system_bp)

    # ── Module blueprints (register here when each phase begins) ─────────────
    # Phase 3 — Knowledge Base:
    #   from modules.knowledge_base.routes import kb_bp
    #   app.register_blueprint(kb_bp, url_prefix="/kb")

    # Phase 4 — Weather:
    #   from modules.weather.routes import weather_bp
    #   app.register_blueprint(weather_bp, url_prefix="/weather")

    # Phase 5 — Leaf Detection:
    from modules.leaf_detection.routes import leaf_bp
    app.register_blueprint(leaf_bp, url_prefix="/leaf")

    # Phase 6 & 7 — AI Crop Doctor, Sarvam AI, Knowledge Base, Weather:
    from modules.ai.routes import ai_bp
    app.register_blueprint(ai_bp, url_prefix="/ai")

    logger.info("AgriGuardian app created — core blueprints: sensor, pump, system, leaf, ai")
    return app



# ── Entry Point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = create_app()

    logger.info("=" * 60)
    logger.info("  SmartEdge AgriGuardian — %s", DEVICE_NAME)
    logger.info("  Central REST Server")
    logger.info("=" * 60)
    logger.info("  Host   : %s", FLASK_HOST)
    logger.info("  Port   : %s", FLASK_PORT)
    logger.info("  Debug  : %s", FLASK_DEBUG)
    logger.info("-" * 60)
    logger.info("  Core API Endpoints:")
    logger.info("    GET  /health   → Device liveness probe")
    logger.info("    GET  /sensor   → Soil moisture, temp, humidity, pump")
    logger.info("    GET  /status   → Uptime, bridge mode, pump state")
    logger.info("    POST /pump/on  → Activate water pump relay")
    logger.info("    POST /pump/off → Deactivate water pump relay")
    logger.info("    POST /leaf/detect → On-device leaf disease detection")
    logger.info("-" * 60)
    logger.info("  Local URL  : http://localhost:%d", FLASK_PORT)
    logger.info("  Network URL: http://<uno-q-wifi-ip>:%d", FLASK_PORT)
    logger.info("=" * 60)

    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)
