# backend/routes/predict.py

import logging
from datetime import datetime
from flask import Blueprint, request, jsonify
from .aqi_utils import ds, predictors, get_predictor, build_features_from_recent, iterative_forecast, log_event, logger

bp = Blueprint("predict", __name__)

@bp.post("/aqi/predict")
def predict_aqi():
    try:
        t0 = datetime.utcnow()
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

        log_event(logging.INFO, f"Prediction request: county={county}, state={state}, model={model_type}, days={days}",
                  operation="validation")

        if not county or not state:
            return jsonify({"success": False, "error": "County and state are required"}), 400

        selected_predictor = get_predictor(model_type)
        if selected_predictor is None or selected_predictor.model is None:
            return jsonify({"success": False, "error": f"{model_type.title()} model not loaded. Please train model first."}), 503

        source = ds()
        if source is None:
            return jsonify({"success": False, "error": "Data source not available"}), 500

        recent_df = source.get_recent_data_for_prediction(county, state, 30)
        if recent_df is None or len(recent_df) < 7:
            return jsonify({"success": False, "error": f"Insufficient historical data for {county}, {state}. Need at least 7 days."}), 400

        features, recent_df = build_features_from_recent(recent_df)
        log_event(logging.INFO, f"Recent rows for features: {len(recent_df)}", operation="feature_generation")

        preds = iterative_forecast(selected_predictor, model_type, recent_df, features, days, county, state)

        elapsed_ms = int((datetime.utcnow() - t0).total_seconds() * 1000)
        log_event(logging.INFO, f"Prediction completed in {elapsed_ms} ms (days={days})", operation="prediction")

        if days == 1:
            return jsonify({
                "success": True,
                "county": county,
                "state": state,
                "forecast_date": preds[0]["forecast_date"],
                "prediction": preds[0],
            })
        else:
            return jsonify({
                "success": True,
                "county": county,
                "state": state,
                "forecast_days": days,
                "predictions": preds,
            })

    except Exception as e:
        logger().exception("Error making prediction", extra={"operation": "prediction"})
        return jsonify({"success": False, "error": str(e)}), 500
