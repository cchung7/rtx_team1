# backend/routes/model_metrics.py

import logging
from flask import Blueprint, request, jsonify
from .aqi_utils import predictors, log_event

bp = Blueprint("model_metrics", __name__)

@bp.get("/model/metrics")
def get_model_metrics():
    try:
        model_type = request.args.get("model", "improved")
        log_event(logging.INFO, f"Metrics request: model={model_type}", operation="validation")
        selected = predictors().get(model_type)
        if selected and getattr(selected, "metrics", None):
            return jsonify({
                "success": True,
                "model_type": model_type,
                "metrics": selected.metrics,
                "version": selected.model_version
            })
        return jsonify({"success": False, "error": f"No metrics available for {model_type} model"}), 404
    except Exception as e:
        from .aqi_utils import logger
        logger().exception("Error fetching metrics", extra={"operation": "validation"})
        return jsonify({"success": False, "error": str(e)}), 500
