# backend/app.py
"""
Flask REST API for CLAP system (modularized)
- Initializes logger, config, CSV data source, and ML models
- Registers Blueprints from routes/
"""
from flask import Flask, send_from_directory, abort
from flask_cors import CORS
from datetime import datetime
import logging
import os
import json
from logging.handlers import RotatingFileHandler

from config import Config
from routes import register_blueprints
from ml_model import AQIPredictor
from data_source import get_data_source

# MIME mapping override for Flask 
import mimetypes
mimetypes.add_type("text/javascript", ".js")
mimetypes.add_type("text/javascript", ".mjs")
mimetypes.add_type("text/css", ".css")
mimetypes.add_type("application/wasm", ".wasm")

# Structured logging
os.makedirs("logs", exist_ok=True)

class JsonFormatter(logging.Formatter):
    def format(self, record):
        payload = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "operation": getattr(record, "operation", "general"),
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["error"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)

def build_logger():
    logger = logging.getLogger("CLAP")
    logger.setLevel(logging.INFO)

    file_handler = RotatingFileHandler("logs/app.log", maxBytes=5_000_000, backupCount=3)
    file_handler.setFormatter(JsonFormatter())

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

    logger.handlers = [file_handler, console_handler]
    logger.propagate = False
    return logger

def log_event(logger, level, message, operation="general", **extra_kv):
    logger.log(level, message, extra={"operation": operation, **extra_kv})


# App factory
def create_app():
    app = Flask(__name__, static_folder="../frontend/dist", static_url_path="/")
    app.config.from_object(Config)
    CORS(app)

    # Logger
    logger = build_logger()
    app.extensions = getattr(app, "extensions", {})
    app.extensions["logger"] = logger
    app.extensions["log_event"] = lambda level, msg, operation="general", **kv: log_event(
        logger, level, msg, operation, **kv
    )

    # Load CSV Data Source
    try:
        ds = get_data_source(data_path="../data/")
        app.extensions["data_source"] = ds
        app.extensions["log_event"](
            logging.INFO, f"CSV data source loaded: {len(ds.df)} records", operation="ingestion"
        )
    except Exception:
        logger.exception("Failed to load CSV data source", extra={"operation": "ingestion"})
        app.extensions["data_source"] = None

    # Load ML models
    predictors = {}
    model_paths = {
        "balanced":  "../models/balanced_lightgbm_model.pkl",
    }

    for name, path in model_paths.items():
        try:
            predictor = AQIPredictor(model_path="../models/")
            if os.path.exists(path):
                predictor.load_model(path)
                predictors[name] = predictor
                app.extensions["log_event"](
                    logging.INFO, f"{name.title()} model loaded successfully", operation="prediction"
                )
            else:
                app.extensions["log_event"](
                    logging.WARNING, f"{name.title()} model not found at {path}", operation="prediction"
                )
        except Exception:
            logger.exception(f"Failed to load {name} model", extra={"operation": "prediction"})

    app.extensions["predictors"] = predictors
    app.extensions["default_predictor_key"] = "balanced"

    register_blueprints(app)

    sep = "=" * 60
    logger.info(sep)
    logger.info(f"Environment: {Config.FLASK_ENV}")
    logger.info(f"Debug mode: {Config.DEBUG}")
    logger.info(f"Database: {Config.DB_NAME}")
    logger.info(sep)

    # SPA static serving
    @app.route("/")
    def index():
        return send_from_directory(app.static_folder, "index.html")

    @app.route("/<path:path>")
    def static_proxy(path):
        if path.startswith("api/"):
            abort(404)
        full = os.path.join(app.static_folder, path)
        if os.path.exists(full) and os.path.isfile(full):
            return send_from_directory(app.static_folder, path)
        return send_from_directory(app.static_folder, "index.html")

    return app

if __name__ == "__main__":
    app = create_app()
    app.extensions["log_event"](logging.INFO, "Starting CLAP Flask API Server", operation="startup")
    app.run(host="0.0.0.0", port=5001, debug=app.config.get("DEBUG", False))
