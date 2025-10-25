# backend/routes/index.py

from flask import Blueprint, current_app, send_from_directory

bp = Blueprint("index", __name__)

@bp.route("/")
def index():
    return send_from_directory(current_app.static_folder, "index.html")
