"""
SmartEdge AgriGuardian — Sarvam AI Advisory Engine
===================================================
File: modules/sarvam_ai/sarvam_service.py

Connects to Sarvam AI to generate natural Hindi advisory responses for Indian farmers.
Strictly adheres to system prompts:
  1. Never identifies diseases (YOLO does this).
  2. Never contradicts the Knowledge Base ground truth.
  3. Uses simple Hindi.
  4. Provides offline fallback directly from knowledge_base.json if network is down.
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
        "model": "sarvam-30b",  # Updated to sarvam-30b for valid completions
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt_context}
        ],
        "temperature": 0.3,
        "max_tokens": 4000
    }

    try:
        response = requests.post(SARVAM_API_URL, headers=headers, json=body, timeout=8)
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
    warning_signs = action_plan.get("warning_signs", ["Daag badhna"])
    expected_recovery = action_plan.get("expected_recovery", "10-14 Days")
    organic = disease_info.get("organic_treatment", ["Neem oil spray"])
    chemical = disease_info.get("chemical_treatment", ["Copper Oxychloride"])

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
            lines.append("\n💧 **सिंचाई सलाह**: मिट्टी में नमी कम है ({moisture}%)। आज हल्की सिंचाई करें।")
        elif moisture > 80:
            lines.append("\n🚫 **सिंचाई सलाह**: मिट्टी में अत्यधिक नमी है ({moisture}%)। सिंचाई तुरंत रोकें।")

    return "\n".join(lines)
