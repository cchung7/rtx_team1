# backend/routes/counties.py

import logging
from flask import Blueprint, jsonify
from .aqi_utils import ds, log_event

bp = Blueprint("counties", __name__)

@bp.get("/counties")
def get_counties():
    try:
        log_event(logging.INFO, "Fetching counties", operation="ingestion")
        source = ds()
        if source is None:
            return jsonify({"success": False, "error": "Data source not available"}), 500
        counties = source.get_counties()
        log_event(logging.INFO, f"Counties retrieved: {len(counties)}", operation="ingestion")
        return jsonify({"success": True, "counties": counties, "count": len(counties), "source": "csv"})
    except Exception as e:
        from .aqi_utils import logger
        logger().exception("Error fetching counties", extra={"operation": "ingestion"})
        return jsonify({"success": False, "error": str(e)}), 500
