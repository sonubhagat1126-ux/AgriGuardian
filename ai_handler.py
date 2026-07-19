"""
SmartEdge AgriGuardian — Sarvam AI Advisory & Knowledge Base Handler
===================================================================
File: ai_handler.py

Implements local Sarvam AI and Knowledge Base query handler.
Replaces the proxy endpoints by executing requests directly on the FastAPI server.
"""

import os
import json
import logging
import requests
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# Sarvam AI endpoint
SARVAM_API_URL = "https://api.sarvam.ai/v1/chat/completions"

SYSTEM_PROMPT = """You are SmartEdge AgriGuardian AI Crop Doctor.
Rules:
1. Answer the farmer's question DIRECTLY, CONCISELY, and briefly in simple Hindi (Kisan friendly).
2. Keep your response extremely short (maximum 2 to 3 sentences, or a very brief bullet list).
3. Do NOT output the entire action plan or unrelated general details. Focus ONLY on answering the specific question asked.
4. Never identify diseases (YOLO does this). Never contradict the detected disease or Knowledge Base object.
5. Use the supplied Knowledge Base and sensor data only if they relate directly to the question.
"""

HERE = os.path.dirname(os.path.abspath(__file__))
# Check standard locations for knowledge_base.json
possible_paths = [
    os.path.join(HERE, "Smartedge-Agrigaurdian-", "knowledge-base", "knowledge_base.json"),
    os.path.join(HERE, "Smartedge-Agrigaurdian-", "arduino_backend", "modules", "knowledge_base", "knowledge_base.json"),
    os.path.join(HERE, "knowledge_base.json")
]

KB_FILE_PATH = None
for path in possible_paths:
    if os.path.exists(path):
        KB_FILE_PATH = path
        break

_disease_index: Dict[str, Dict] = {}


def _init_index() -> None:
    """Loads knowledge_base.json into memory and indexes by disease ID and name."""
    global _disease_index
    if _disease_index:
        return

    logger.info(f"Indexing Knowledge Base from: {KB_FILE_PATH}")
    if not KB_FILE_PATH or not os.path.exists(KB_FILE_PATH):
        logger.error("Knowledge Base file could not be found in workspace path.")
        return

    try:
        with open(KB_FILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            diseases = data.get("diseases", [])
            for item in diseases:
                d_id = item.get("id", "").lower()
                d_name = item.get("name", "").lower()
                d_disease = item.get("disease", "").lower()
                
                # Index by multiple keys for reliable matching
                if d_id:
                    _disease_index[d_id] = item
                if d_name:
                    _disease_index[d_name] = item
                if d_disease:
                    _disease_index[d_disease] = item

        logger.info(f"Successfully indexed {len(diseases)} disease objects from Knowledge Base.")
    except Exception as exc:
        logger.error(f"Failed to parse Knowledge Base JSON: {exc}")


def get_disease(query: str) -> Optional[Dict]:
    """
    Retrieves the matching disease object (including action_plan) for a given disease ID or class name.
    """
    _init_index()
    if not query:
        return None

    query_clean = query.strip().lower()
    
    # 1. Direct key match
    if query_clean in _disease_index:
        return _disease_index[query_clean]

    # 2. Fuzzy substring match against keys
    for key, obj in _disease_index.items():
        if query_clean in key or key in query_clean:
            return obj
            
    # 3. Clean underscores and match
    normalized = query_clean.replace("___", "_").replace("__", "_")
    for key, obj in _disease_index.items():
        key_norm = key.replace("___", "_").replace("__", "_")
        if normalized in key_norm or key_norm in normalized:
            return obj

    logger.warning(f"No Knowledge Base match found for query: '{query}'")
    return None


def get_current_weather(lat: float, lon: float) -> Dict:
    """
    Fetches real-time weather indicators from Open-Meteo.
    """
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}&"
        f"current=temperature_2m,relative_humidity_2m,rain,wind_speed_10m&"
        f"hourly=precipitation_probability&forecast_days=1"
    )

    try:
        response = requests.get(url, timeout=5)
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


def generate_crop_doctor_advisory(
    disease_info: Dict,
    confidence: float,
    sensor_data: Dict,
    weather_data: Dict,
    user_question: Optional[str] = None
) -> Dict:
    """
    Generates farmer-friendly advisory response in Hindi.
    Uses Sarvam AI if online and API key exists, otherwise falls back to Knowledge Base.
    """
    api_key = os.getenv("SARVAM_API_KEY", "sk_mi0780i0_MIK6OPTzvXk4rJLt4PP9qUXd").strip()
    
    # 1. Build Offline Fallback Advisory from Knowledge Base & Action Plan
    offline_advisory = _build_offline_advisory(disease_info, confidence, sensor_data, weather_data, user_question)

    if not api_key:
        logger.info("SARVAM_API_KEY not found in environment. Using Knowledge Base offline response.")
        return {
            "source": "knowledge_base_offline",
            "advisory_hindi": offline_advisory,
            "action_plan": disease_info.get("action_plan", {})
        }

    # 2. Prepare Payload for Sarvam AI
    action_plan = disease_info.get("action_plan", {})
    prompt_context = f"""
[DETECTED DISEASE METADATA]
Crop: {disease_info.get('crop', 'Crop')}
Disease: {disease_info.get('disease', 'Disease')}
Severity: {disease_info.get('severity', 'Medium')}
Confidence: {confidence * 100:.1f}%

[KNOWLEDGE BASE OBJECT]
Overview: {disease_info.get('overview', '')}
Symptoms: {', '.join(disease_info.get('symptoms', []))}
Organic Treatment: {', '.join(disease_info.get('organic_treatment', []))}
Chemical Treatment: {', '.join(disease_info.get('chemical_treatment', []))}
Recommended Fungicides: {', '.join(disease_info.get('recommended_fungicides', []))}
Watering Advice: {disease_info.get('watering_advice', '')}
Avoid Fertilizers: {', '.join(disease_info.get('avoid_fertilizers', []))}

[ACTION PLAN]
Today: {', '.join(action_plan.get('today', []))}
Next 3 Days: {', '.join(action_plan.get('next_3_days', []))}
Next Week: {', '.join(action_plan.get('next_week', []))}
Warning Signs: {', '.join(action_plan.get('warning_signs', []))}
Expected Recovery: {action_plan.get('expected_recovery', '10-14 Days')}

[CURRENT SENSOR DATA]
Soil Moisture: {sensor_data.get('soil_moisture', 'N/A')}%
Temperature: {sensor_data.get('temperature', 'N/A')}°C
Humidity: {sensor_data.get('humidity', 'N/A')}%

[CURRENT WEATHER]
Condition: {weather_data.get('condition', 'N/A')}
Temp: {weather_data.get('temperature', 'N/A')}°C
Rain Probability: {weather_data.get('rain_probability', 0)}%

[FARMER QUESTION]
{user_question if user_question else "Kripya kisan ko bataiye ki aaj kya kaam karna hai aur bimari se kaise bachna hai."}
"""

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    body = {
        "model": "sarvam-30b",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt_context}
        ],
        "temperature": 0.3,
        "max_tokens": 4000
    }

    try:
        response = requests.post(SARVAM_API_URL, headers=headers, json=body, timeout=12)
        if response.status_code == 200:
            res_json = response.json()
            choices = res_json.get("choices", [])
            if choices and "message" in choices[0]:
                ai_text = choices[0]["message"]["content"]
                return {
                    "source": "sarvam_ai",
                    "advisory_hindi": ai_text,
                    "action_plan": action_plan
                }
    except Exception as exc:
        logger.warning(f"Sarvam AI call failed or timed out ({exc}). Falling back to Knowledge Base.")

    return {
        "source": "knowledge_base_offline",
        "advisory_hindi": offline_advisory,
        "action_plan": action_plan
    }


def _build_offline_advisory(
    disease_info: Dict,
    confidence: float,
    sensor_data: Dict,
    weather_data: Dict,
    user_question: Optional[str]
) -> str:
    """Generates structured Hindi advisory directly from Knowledge Base."""
    crop = disease_info.get("crop", "Fasal")
    disease = disease_info.get("disease", "Bimari")
    severity = disease_info.get("severity", "Medium")
    action_plan = disease_info.get("action_plan", {})
    
    today_items = action_plan.get("today", ["Bimar pattiya hataayein"])
    next_3_days = action_plan.get("next_3_days", ["Pattiyo ko sookha rakhein"])
    organic = disease_info.get("organic_treatment", ["Neem oil spray"])
    chemical = disease_info.get("chemical_treatment", ["Copper Oxychloride"])
    expected_recovery = action_plan.get("expected_recovery", "10-14 Days")

    lines = []
    lines.append(f"🌿 **फसल बीमारी पहचानी गई**: {crop} - {disease}")
    lines.append(f"📊 **सटीकता (Confidence)**: {confidence * 100:.1f}%")
    lines.append(f"⚠️ **गंभीरता (Severity)**: {severity}\n")
    
    lines.append("📋 **आज का मुख्य कार्य (Today's Action):**")
    for item in today_items:
        lines.append(f"  • {item}")
        
    lines.append("\n🌱 **जैविक / ऑर्गेनिक उपचार (Organic Treatment):**")
    for item in organic:
        lines.append(f"  • {item}")

    lines.append("\n🧪 **रासायनिक उपचार (Chemical Treatment):**")
    for item in chemical:
        lines.append(f"  • {item}")

    lines.append("\n⏳ **अगले 3 दिनों की योजना (Next 3 Days):**")
    for item in next_3_days:
        lines.append(f"  • {item}")

    lines.append(f"\n🔄 **अनुमानित सुधार समय (Expected Recovery)**: {expected_recovery}")
    
    # Add sensor / weather advice
    moisture = sensor_data.get("soil_moisture")
    if moisture is not None and isinstance(moisture, (int, float)):
        if moisture < 30:
            lines.append(f"\n💧 **सिंचाई सलाह**: मिट्टी में नमी कम है ({moisture}%)। आज हल्की सिंचाई करें।")
        elif moisture > 80:
            lines.append(f"\n🚫 **सिंचाई सलाह**: मिट्टी में अत्यधिक नमी है ({moisture}%)। सिंचाई तुरंत रोकें।")

    return "\n".join(lines)
