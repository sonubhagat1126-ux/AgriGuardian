"""
SmartEdge AgriGuardian — Weather Integration Service
=====================================================
File: modules/weather/weather_service.py

Fetches current weather (Temperature, Humidity, Rain Probability, Wind Speed)
using the free Open-Meteo API. Provides clean offline fallback handling if internet
is unavailable.
"""

import logging
import requests
from typing import Dict

logger = logging.getLogger(__name__)

# Default coordinates: Ghaziabad / Delhi NCR agricultural belt
DEFAULT_LAT = 28.6692
DEFAULT_LON = 77.4538


def get_current_weather(lat: float = DEFAULT_LAT, lon: float = DEFAULT_LON) -> Dict:
    """
    Fetches real-time weather indicators from Open-Meteo.

    Returns:
        Dict containing temperature, humidity, rain probability, wind speed, condition.
        If offline, returns {"status": "offline"}.
    """
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}&"
        f"current=temperature_2m,relative_humidity_2m,rain,wind_speed_10m&"
        f"hourly=precipitation_probability&forecast_days=1"
    )

    try:
        response = requests.get(url, timeout=4)
        if response.status_code == 200:
            data = response.json()
            current = data.get("current", {})
            hourly = data.get("hourly", {})
            
            rain_probs = hourly.get("precipitation_probability", [0])
            rain_prob = max(rain_probs) if rain_probs else 0
            
            temp = current.get("temperature_2m", 28.0)
            humidity = current.get("relative_humidity_2m", 65.0)
            wind_speed = current.get("wind_speed_10m", 12.0)
            rain_amount = current.get("rain", 0.0)

            # Determine human-readable condition
            if rain_amount > 0 or rain_prob > 60:
                condition = "Rainy / High Humidity"
            elif humidity > 80:
                condition = "Humid & Overcast"
            elif temp > 35:
                condition = "Hot & Dry Heatwave"
            else:
                condition = "Clear / Fair Weather"

            return {
                "status": "online",
                "temperature": round(temp, 1),
                "humidity": round(humidity, 1),
                "rain_probability": int(rain_prob),
                "wind_speed": round(wind_speed, 1),
                "condition": condition,
            }
    except Exception as exc:
        logger.warning(f"Weather API unreachable (offline mode active): {exc}")

    # Offline fallback
    return {
        "status": "offline",
        "temperature": 28.0,
        "humidity": 65.0,
        "rain_probability": 0,
        "wind_speed": 10.0,
        "condition": "Weather Data Unavailable (Offline)",
    }
