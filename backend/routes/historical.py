# backend/routes/historical.py

import logging
from flask import Blueprint, request, jsonify
from .aqi_utils import ds, log_event, logger

bp = Blueprint("historical", __name__)

@bp.get("/aqi/historical")
def get_historical_aqi():
    try:
        county = request.args.get("county")
        state = request.args.get("state")
        days = int(request.args.get("days", 30))

        log_event(logging.INFO, f"Historical request: county={county}, state={state}, days={days}", operation="validation")
        if not county or not state:
            return jsonify({"success": False, "error": "County and state parameters are required"}), 400

        source = ds()
        if source is None:
            return jsonify({"success": False, "error": "Data source not available"}), 500

        historical_data = source.get_historical_data(county, state, days)
        log_event(logging.INFO, f"Historical rows returned: {len(historical_data)}", operation="ingestion")

        return jsonify({
            "success": True,
            "county": county,
            "state": state,
            "days": days,
            "data": historical_data,
            "count": len(historical_data),
            "source": "csv"
        })
    except Exception as e:
        logger().exception("Error fetching historical data", extra={"operation": "ingestion"})
        return jsonify({"success": False, "error": str(e)}), 500
