"""
SmartEdge AgriGuardian — Leaf Detection Routes
================================================
File: modules/leaf_detection/routes.py

Registers:
    POST /detect  — Predicts crop plant disease from uploaded image.

Routes are registered under the '/leaf' prefix.
Endpoint is accessible as POST http://<uno-q-ip>:5001/leaf/detect.
"""

import logging
from flask import Blueprint, jsonify, request

from modules.leaf_detection import leaf_service

logger = logging.getLogger(__name__)

leaf_bp = Blueprint("leaf", __name__)


@leaf_bp.post("/detect")
def detect_disease():
    """
    Classifies a crop leaf image upload using the trained on-device TFLite model.

    Multipart Body:
        image: File data (binary JPEG/PNG image)

    Success Response (200 OK):
        {
            "status": "success",
            "disease": "Tomato_Early_blight",
            "confidence": 0.9842,
            "plant_type": "Tomato",
            "is_healthy": false
        }

    Errors:
        400 Bad Request: Image parameter missing or invalid image bytes.
        503 Service Unavailable: Model files missing or inference failure.
    """
    # Verify file is attached
    if "image" not in request.files:
        return jsonify({
            "status": "error",
            "message": "Missing required field 'image' in multipart upload request"
        }), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({
            "status": "error",
            "message": "Empty file name submitted"
        }), 400

    # Read binary bytes
    try:
        image_bytes = file.read()
    except Exception as exc:
        logger.error(f"Failed to read image upload stream: {exc}")
        return jsonify({
            "status": "error",
            "message": f"Failed to read uploaded file: {exc}"
        }), 400

    # Run YOLO11 prediction service
    try:
        prediction = leaf_service.classify_leaf(image_bytes)
        return jsonify(prediction), 200

    except ValueError as exc:
        logger.warning(f"Validation error during classification: {exc}")
        return jsonify({
            "status": "error",
            "message": str(exc)
        }), 400

    except (RuntimeError, ImportError) as exc:
        logger.error(f"System error during classification: {exc}")
        return jsonify({
            "status": "error",
            "message": "Inference engine is currently unavailable",
            "detail": str(exc)
        }), 503
