"""
SmartEdge AgriGuardian - Backend API Server
=============================================
This wraps kb_matcher.py and weather_advisor.py behind a simple HTTP API,
so the Flutter mobile app (running on the phone) can call them over the
local WiFi network (phone and PC connected to the same network).

Run this on your PC (or the Snapdragon X PC at the hackathon):
    python app.py

Then find your PC's local IP address (run `ipconfig` on Windows,
look for "IPv4 Address" under your active WiFi adapter, e.g. 192.168.1.5)
and use that IP in the Flutter app's API base URL, e.g.:
    http://192.168.1.5:5000
"""

from flask import Flask, request, jsonify
from flask_cors import CORS

from kb_matcher import get_advisory_response
from weather_advisor import (
    get_current_weather,
    get_irrigation_recommendation,
    get_crop_recommendation,
    get_weather_dashboard_summary,
)

app = Flask(__name__)
CORS(app)  # Allow requests from the Flutter app


@app.route("/", methods=["GET"])
def health_check():
    """Simple endpoint to confirm the server is running."""
    return jsonify({"status": "ok", "message": "SmartEdge AgriGuardian backend is running"})


@app.route("/advisory", methods=["POST"])
def advisory():
    """
    Main endpoint for the AI Crop Doctor / Voice Assistant feature.

    Expected JSON body:
    {
        "query": "My potato leaves have white spots",
        "crop_hint": "potato",          (optional)
        "sensor_context": {              (optional)
            "moisture": 28,
            "temperature": 32
        }
    }
    """
    data = request.get_json(force=True) or {}
    query = data.get("query", "")
    crop_hint = data.get("crop_hint")
    sensor_context = data.get("sensor_context")

    if not query:
        return jsonify({"error": "Missing 'query' field"}), 400

    result = get_advisory_response(query, crop_hint=crop_hint, sensor_context=sensor_context)
    return jsonify(result)


@app.route("/weather/current", methods=["GET"])
def weather_current():
    """
    Returns current weather for a city.
    Usage: /weather/current?city=Ghaziabad
    """
    city = request.args.get("city", "Ghaziabad")
    weather = get_current_weather(city)
    if weather is None:
        return jsonify({"error": "Could not fetch weather data"}), 502
    return jsonify(weather)


@app.route("/irrigation", methods=["GET"])
def irrigation():
    """
    Returns an irrigation recommendation based on soil moisture and rain forecast.
    Usage: /irrigation?moisture=28&city=Ghaziabad
    """
    moisture = request.args.get("moisture", type=float)
    city = request.args.get("city", "Ghaziabad")

    if moisture is None:
        return jsonify({"error": "Missing 'moisture' parameter"}), 400

    result = get_irrigation_recommendation(moisture, city)
    return jsonify(result)


@app.route("/crop-recommendation", methods=["GET"])
def crop_recommendation():
    """Returns season-based crop recommendation."""
    result = get_crop_recommendation()
    return jsonify(result)


@app.route("/dashboard", methods=["GET"])
def dashboard():
    """
    Combined endpoint for the Home Dashboard screen -
    returns weather + irrigation advice + crop recommendation in one call.
    Usage: /dashboard?moisture=28&city=Ghaziabad
    """
    moisture = request.args.get("moisture", type=float, default=45.0)
    city = request.args.get("city", "Ghaziabad")

    result = get_weather_dashboard_summary(city, moisture)
    return jsonify(result)


if __name__ == "__main__":
    # host="0.0.0.0" makes the server reachable from other devices on the same network
    # (like your phone), not just from this PC itself.
    app.run(host="0.0.0.0", port=5000, debug=True)