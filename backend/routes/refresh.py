# backend/routes/refresh.py

import logging
from datetime import datetime
from flask import Blueprint, request, jsonify
from .aqi_utils import ds, get_predictor, build_features_from_recent, iterative_forecast, log_event, logger

bp = Blueprint("refresh", __name__)

@bp.post("/aqi/refresh")
def refresh_data():
    """
    Recompute historical + prediction without internally calling HTTP endpoints.
    Body: { "county": "string", "state": "string", "model": "balanced", "days": 1 }
    """
    try:
        payload = request.get_json(force=True) or {}
        county = payload.get("county")
        state = payload.get("state")
        model_type = payload.get("model", "balanced")
        
        # Validate days parameter
        days_input = payload.get("days", 1)
        try:
            days = int(days_input)
        except (ValueError, TypeError):
            return jsonify({
                "success": False, 
                "error": f"Invalid 'days' parameter: '{days_input}'. Must be an integer."
            }), 400
        
        # Valid days values: 1, 3, 7, or 14
        valid_days = [1, 3, 7, 14]
        if days not in valid_days:
            return jsonify({
                "success": False, 
                "error": f"Invalid 'days' value: {days}. Must be one of: {', '.join(map(str, valid_days))}"
            }), 400

        log_event(logging.INFO, f"Refresh request: county={county}, state={state}, model={model_type}, days={days}", operation="validation")
        if not county or not state:
            return jsonify({"success": False, "error": "County and state are required"}), 400

        # Historical
        source = ds()
        if source is None:
            return jsonify({"success": False, "error": "Data source not available"}), 500
        log_event(logging.INFO, "Refreshing historical data", operation="ingestion")
        historical_data = source.get_historical_data(county, state, int(payload.get("history_days", 30)))

        # Prediction
        log_event(logging.INFO, "Refreshing prediction", operation="prediction")
        recent_df = source.get_recent_data_for_prediction(county, state, 30)
        if recent_df is None or len(recent_df) < 7:
            return jsonify({"success": False, "error": f"Insufficient historical data for {county}, {state}. Need at least 7 days."}), 400

        features, recent_df = build_features_from_recent(recent_df)
        predictor = get_predictor(model_type)
        if predictor is None or predictor.model is None:
            return jsonify({"success": False, "error": f"{model_type.title()} model not loaded. Please train model first."}), 503

        preds = iterative_forecast(predictor, model_type, recent_df, features, days, county, state)

        return jsonify({
            "success": True,
            "county": county,
            "state": state,
            "timestamp": datetime.utcnow().isoformat(),
            "historical": {
                "success": True,
                "county": county,
                "state": state,
                "data": historical_data,
                "count": len(historical_data),
                "source": "csv",
            },
            "prediction": (
                {
                    "success": True,
                    "county": county,
                    "state": state,
                    "forecast_date": preds[0]["forecast_date"],
                    "prediction": preds[0],
                } if days == 1 else {
                    "success": True,
                    "county": county,
                    "state": state,
                    "forecast_days": days,
                    "predictions": preds,
                }
            ),
        })
    except Exception as e:
        logger().exception("Error refreshing data", extra={"operation": "ingestion"})
        return jsonify({"success": False, "error": str(e)}), 500
