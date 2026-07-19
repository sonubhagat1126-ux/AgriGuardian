"""
SmartEdge AgriGuardian - Weather Advisory Module
==================================================
Yeh module OpenWeatherMap API se weather data fetch karta hai aur uske
basis pe irrigation recommendation + season-based crop suggestion deta hai.
"""

import requests
from datetime import datetime

# ---------------------------------------------------
# CONFIG -  API key 
# ---------------------------------------------------

API_KEY = "ea3139aba0b4b2c5c9cfe9160623ac6f"  # <-- Isko apni key se replace karo
BASE_URL = "https://api.openweathermap.org/data/2.5"


# ---------------------------------------------------
# Step 1: Current Weather Fetch Karo
# ---------------------------------------------------

def get_current_weather(city="Ghaziabad", country_code="IN"):
    """
    Current weather data fetch karta hai city ke naam se.

    Returns:
        dict: {temperature, humidity, description, rain_now} ya None agar error aaye
    """
    url = f"{BASE_URL}/weather"
    params = {
        "q": f"{city},{country_code}",
        "appid": API_KEY,
        "units": "metric"  # Celsius mein temperature chahiye
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        

        return {
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "description": data["weather"][0]["description"],
            "rain_now": "rain" in data  # Agar abhi baarish ho rahi hai
        }
    except requests.exceptions.RequestException as e:
        print(f"Weather fetch error: {e}")
        return None


# ---------------------------------------------------
# Step 2: 5-Day Forecast Fetch Karo (Rain Prediction Ke Liye)
# ---------------------------------------------------

def get_rain_forecast(city="Ghaziabad", country_code="IN"):
    """
    Agle 24-48 ghante ka rain forecast check karta hai.

    Returns:
        dict: {
            "rain_expected": bool,
            "rain_probability": float (0-100),
            "expected_rainfall_mm": float,
            "forecast_time": str
        }
    """
    url = f"{BASE_URL}/forecast"
    params = {
        "q": f"{city},{country_code}",
        "appid": API_KEY,
        "units": "metric"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Agle 8 forecast entries dekho (yeh roughly agle 24 ghante hote hain, 3-hour gaps mein)
        next_entries = data["list"][:8]

        max_rain_prob = 0
        total_rain_mm = 0
        rain_time = None

        for entry in next_entries:
            pop = entry.get("pop", 0) * 100  # Probability of precipitation (0-1 -> 0-100%)
            if pop > max_rain_prob:
                max_rain_prob = pop
                rain_time = entry["dt_txt"]

            if "rain" in entry:
                total_rain_mm += entry["rain"].get("3h", 0)

        return {
            "rain_expected": max_rain_prob > 50,
            "rain_probability": round(max_rain_prob, 1),
            "expected_rainfall_mm": round(total_rain_mm, 1),
            "forecast_time": rain_time
        }

    except requests.exceptions.RequestException as e:
        print(f"Forecast fetch error: {e}")
        return None


# ---------------------------------------------------
# Step 3: Irrigation Recommendation (Weather + Soil Moisture Combine)
# ---------------------------------------------------

def get_irrigation_recommendation(soil_moisture_percent, city="Ghaziabad"):
    """
    Soil moisture aur rain forecast dono ko combine karke
    irrigation ka final decision deta hai.

    Args:
        soil_moisture_percent (float): Arduino se aaya hua moisture reading (0-100)
        city (str): Farmer ka location

    Returns:
        dict: {recommendation, reason, priority}
    """

    forecast = get_rain_forecast(city)

    # Agar weather data na mil paye, sirf soil moisture pe decide karo
    if forecast is None:
        if soil_moisture_percent < 30:
            return {
                "recommendation": "Irrigation zaroori hai",
                "reason": "Soil moisture kaafi kam hai (weather data available nahi)",
                "priority": "high"
            }
        return {
            "recommendation": "Abhi irrigation ki zarurat nahi",
            "reason": "Soil moisture theek hai",
            "priority": "low"
        }

    # Case 1: Baarish ka strong chance hai -> irrigation postpone karo
    if forecast["rain_expected"]:
        return {
            "recommendation": "Aaj irrigation skip karo",
            "reason": f"Baarish ka {forecast['rain_probability']}% chance hai "
                      f"({forecast['expected_rainfall_mm']}mm expected). "
                      f"Paani waste mat karo.",
            "priority": "low"
        }

    # Case 2: Baarish nahi hai, lekin soil moisture bahut low hai -> urgent
    if soil_moisture_percent < 30:
        return {
            "recommendation": "Turant irrigation karo (15-20 minute)",
            "reason": f"Soil moisture sirf {soil_moisture_percent}% hai aur "
                      f"baarish ka koi chance nahi hai",
            "priority": "high"
        }

    # Case 3: Soil moisture medium hai
    if soil_moisture_percent < 50:
        return {
            "recommendation": "Halka irrigation karo (8-10 minute)",
            "reason": f"Soil moisture {soil_moisture_percent}% hai, thoda paani chahiye",
            "priority": "medium"
        }

    # Case 4: Sab theek hai
    return {
        "recommendation": "Abhi irrigation ki zarurat nahi",
        "reason": f"Soil moisture {soil_moisture_percent}% hai, achha hai",
        "priority": "low"
    }


# ---------------------------------------------------
# Step 4: Season-Based Crop Recommendation (Rule-Based)
# ---------------------------------------------------

CROP_CALENDAR = {
    "kharif": {
        "months": [6, 7, 8, 9],  # June-September
        "crops": ["Rice (Dhan)", "Maize (Makka)", "Cotton (Kapas)", "Soybean", "Bajra"],
        "condition": "High rainfall aur garam temperature ke liye best"
    },
    "rabi": {
        "months": [10, 11, 12, 1, 2, 3],  # October-March
        "crops": ["Wheat (Gehu)", "Mustard (Sarson)", "Gram (Chana)", "Peas (Matar)"],
        "condition": "Thanda temperature aur kam paani ke liye best"
    },
    "zaid": {
        "months": [4, 5],  # April-May
        "crops": ["Watermelon (Tarbooz)", "Cucumber (Kheera)", "Muskmelon"],
        "condition": "Garmi aur irrigation-supported crops ke liye"
    }
}


def get_crop_recommendation(current_month=None, current_temp=None):
    """
    Current season ke hisab se best crops suggest karta hai.

    Args:
        current_month (int, optional): 1-12, agar nahi diya toh aaj ki date use karega
        current_temp (float, optional): Current temperature, extra context ke liye

    Returns:
        dict: {season, recommended_crops, note}
    """

    if current_month is None:
        current_month = datetime.now().month

    for season, info in CROP_CALENDAR.items():
        if current_month in info["months"]:
            note = info["condition"]
            if current_temp is not None:
                note += f" (Current temp: {current_temp}°C)"

            return {
                "season": season.capitalize(),
                "recommended_crops": info["crops"],
                "note": note
            }

    return {
        "season": "Unknown",
        "recommended_crops": [],
        "note": "Season determine nahi ho paya"
    }


# ---------------------------------------------------
# Step 5: Combined Dashboard Summary (Sab Kuch Ek Saath)
# ---------------------------------------------------

def get_weather_dashboard_summary(city, soil_moisture_percent):
    """
    Dashboard ke liye ek combined summary deta hai -
    current weather + irrigation advice + crop recommendation sab ek saath.
    """

    current = get_current_weather(city)
    irrigation = get_irrigation_recommendation(soil_moisture_percent, city)
    crop_advice = get_crop_recommendation(
        current_temp=current["temperature"] if current else None
    )

    return {
        "current_weather": current,
        "irrigation_advice": irrigation,
        "crop_recommendation": crop_advice
    }


# ---------------------------------------------------
# Step 6: Test Karne Ke Liye
# ---------------------------------------------------

if __name__ == "__main__":
    CITY = "Ghaziabad"
    TEST_SOIL_MOISTURE = 28  # Example value, jaise Arduino se aaya

    print("=" * 55)
    print("WEATHER ADVISORY MODULE - TEST")
    print("=" * 55)

    print("\n1. Current Weather:")
    weather = get_current_weather(CITY)
    print(weather)

    print("\n2. Rain Forecast (Next 24hr):")
    forecast = get_rain_forecast(CITY)
    print(forecast)

    print("\n3. Irrigation Recommendation:")
    irrigation = get_irrigation_recommendation(TEST_SOIL_MOISTURE, CITY)
    print(irrigation)

    print("\n4. Crop Recommendation:")
    crop = get_crop_recommendation(current_temp=weather["temperature"] if weather else None)
    print(crop)

    print("\n5. Full Dashboard Summary:")
    summary = get_weather_dashboard_summary(CITY, TEST_SOIL_MOISTURE)
    print(summary)