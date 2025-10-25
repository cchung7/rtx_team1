# backend/routes/categories.py

from flask import Blueprint, jsonify, current_app
from config import Config

bp = Blueprint("categories", __name__)

@bp.get("/categories")
def get_aqi_categories():
    return jsonify({"success": True, "categories": Config.AQI_CATEGORIES})
