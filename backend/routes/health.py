# backend/routes/health.py

from flask import Blueprint, jsonify, current_app
from datetime import datetime

bp = Blueprint("health", __name__)

@bp.get("/health")
def health_check():
    predictors = current_app.extensions.get("predictors", {})
    default_key = current_app.extensions.get("default_predictor_key", "balanced")
    predictor = predictors.get(default_key)
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "model_loaded": bool(predictor and predictor.model is not None),
        "database_connected": False  # CSV mode
    })
