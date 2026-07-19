"""
SmartEdge AgriGuardian — AI Crop Doctor & Knowledge Base Routes
===============================================================
File: modules/ai/routes.py

Registers:
  POST /ai/crop-doctor  — Generates complete Crop Doctor advisory (Hindi text + Action Plan)
  POST /ai/chat         — Interactive AI Chatbot endpoint for farmer follow-up questions
  GET  /kb/<disease_id> — Retrieves Knowledge Base disease object & action plan
  GET  /weather         — Retrieves real-time weather indicators
"""

import logging
from flask import Blueprint, jsonify, request

from modules.knowledge_base import kb_service
from modules.weather import weather_service
from modules.sarvam_ai import sarvam_service
from services import sensor_service

logger = logging.getLogger(__name__)

ai_bp = Blueprint("ai", __name__)


def _fetch_safe_sensor_data() -> dict:
    """Helper to fetch sensor data or fallback gracefully on dev environments."""
    try:
        return sensor_service.get_sensor_data()
    except Exception as exc:
        logger.debug(f"Hardware sensors unavailable ({exc}). Using standard fallback sensor values.")
        return {
            "soil_moisture": 45.0,
            "temperature": 28.5,
            "humidity": 62.0,
            "light_intensity": "Normal Sunlight",
            "water_tank_level": "80%",
            "pump": False
        }



@ai_bp.post("/crop-doctor")
def crop_doctor_advisory():
    """
    Generates the complete AI Crop Doctor advisory response.

    JSON Body:
        disease: Disease name / YOLO class string (required)
        confidence: Confidence float (optional, default 0.95)
        question: Optional farmer question string
        sensor_data: Optional dict (if omitted, reads real-time sensors)

    Response (200 OK):
        {
            "status": "success",
            "source": "sarvam_ai" | "knowledge_base_offline",
            "disease_name": "Potato Late Blight",
            "advisory_hindi": "...",
            "action_plan": { ... },
            "disease_info": { ... },
            "sensor_data": { ... },
            "weather": { ... }
        }
    """
    data = request.get_json(silent=True) or {}
    disease_query = data.get("disease", "").strip()
    confidence = float(data.get("confidence", 0.95))
    user_question = data.get("question", "")

    if not disease_query:
        return jsonify({
            "status": "error",
            "message": "Missing required field 'disease' in JSON body"
        }), 400

    # 1. Retrieve Knowledge Base Object & Action Plan
    disease_info = kb_service.get_disease(disease_query)
    if not disease_info:
        logger.warning(f"Disease '{disease_query}' not found in Knowledge Base. Using fallback object.")
        disease_info = {
            "crop": "Crop",
            "disease": disease_query,
            "severity": "Medium",
            "overview": "Information unavailable",
            "action_plan": {
                "today": ["Perform field inspection", "Remove damaged foliage"],
                "next_3_days": ["Keep leaves dry"],
                "expected_recovery": "10-14 Days"
            }
        }

    # 2. Get Sensor Data
    sensor_data = data.get("sensor_data")
    if not sensor_data:
        sensor_data = _fetch_safe_sensor_data()

    # 3. Get Real-time Weather
    weather = weather_service.get_current_weather()

    # 4. Generate Sarvam AI / Offline Advisory
    advisory_res = sarvam_service.generate_crop_doctor_advisory(
        disease_info=disease_info,
        confidence=confidence,
        sensor_data=sensor_data,
        weather_data=weather,
        user_question=user_question
    )

    return jsonify({
        "status": "success",
        "disease_name": disease_info.get("name", disease_query),
        "confidence": confidence,
        "source": advisory_res.get("source"),
        "advisory_hindi": advisory_res.get("advisory_hindi"),
        "action_plan": disease_info.get("action_plan", {}),
        "disease_info": disease_info,
        "sensor_data": sensor_data,
        "weather": weather
    }), 200


@ai_bp.post("/chat")
def ai_chatbot():
    """
    Interactive AI Crop Doctor Chatbot Q&A endpoint.

    JSON Body:
        question: Farmer question string (required, e.g. "What fertilizer should I use?")
        disease: Optional current detected disease string
        sensor_data: Optional dict
    """
    data = request.get_json(silent=True) or {}
    question = data.get("question", "").strip()
    disease_query = data.get("disease", "Tomato_healthy")

    if not question:
        return jsonify({
            "status": "error",
            "message": "Missing required field 'question'"
        }), 400

    disease_info = kb_service.get_disease(disease_query) or {
        "crop": "Crop", "disease": disease_query, "severity": "Low"
    }

    sensor_data = data.get("sensor_data") or _fetch_safe_sensor_data()
    weather = weather_service.get_current_weather()

    advisory_res = sarvam_service.generate_crop_doctor_advisory(
        disease_info=disease_info,
        confidence=0.90,
        sensor_data=sensor_data,
        weather_data=weather,
        user_question=question
    )

    return jsonify({
        "status": "success",
        "reply_hindi": advisory_res.get("advisory_hindi"),
        "source": advisory_res.get("source")
    }), 200


@ai_bp.get("/kb/<disease_id>")
def get_kb_disease(disease_id: str):
    """Retrieves single disease object and action plan from Knowledge Base."""
    disease_info = kb_service.get_disease(disease_id)
    if not disease_info:
        return jsonify({
            "status": "error",
            "message": f"Disease '{disease_id}' not found in Knowledge Base"
        }), 444 if False else 404

    return jsonify({
        "status": "success",
        "disease_info": disease_info
    }), 200


@ai_bp.get("/weather")
def get_weather():
    """Retrieves real-time weather indicators."""
    weather = weather_service.get_current_weather()
    return jsonify({
        "status": "success",
        "weather": weather
    }), 200
