"""
Flask REST API for CLAP system
Provides endpoints for AQI predictions and dashboard data
"""
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import logging
import os
import traceback
import json

from config import Config
from ml_model import AQIPredictor

# Database functionality removed - using CSV files instead
USE_DATABASE = False

# Import CSV data source
from data_source import get_data_source

# -------------------------------
# Structured logging (JSON) setup
# -------------------------------

from logging.handlers import RotatingFileHandler

# Ensure logs directory exists
os.makedirs("logs", exist_ok=True)

class JsonFormatter(logging.Formatter):
    """Structured JSON log formatter (timestamp, level, operation, message, error)."""
    def format(self, record):
        payload = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "operation": getattr(record, "operation", "general"),
            "message": record.getMessage()
        }
        if record.exc_info:
            payload["error"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)

# Build logger with JSON file handler + simple console handler
logger = logging.getLogger("CLAP")  # [CHANGED] use named logger instead of __name__
logger.setLevel(logging.INFO)

# File handler (structured JSON)
file_handler = RotatingFileHandler("logs/app.log", maxBytes=5_000_000, backupCount=3)  # [ADDED]
file_handler.setFormatter(JsonFormatter())

# Console handler (human-readable short)
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))  # [ADDED]

# Replace handlers (avoid duplicate handlers on reload)
logger.handlers = [file_handler, console_handler]
logger.propagate = False

def log_event(level, message, operation="general", **extra_kv):
    """Helper to emit structured logs with an 'operation' tag."""
    logger.log(level, message, extra={"operation": operation, **extra_kv})

# -------------------------------
# Initialize Flask app
# -------------------------------

app = Flask(__name__, static_folder='../frontend', static_url_path='')
app.config.from_object(Config)
CORS(app)

# -------------------------------
# Initialize CSV data source
# -------------------------------

try:
    data_source = get_data_source(data_path='../data/')
    log_event(logging.INFO, f"CSV data source loaded: {len(data_source.df)} records", operation="ingestion")  # [ADDED]
except Exception as e:
    logger.exception("Failed to load CSV data source", extra={"operation": "ingestion"})  # [CHANGED]
    data_source = None

# -------------------------------
# Load ML models
# -------------------------------

predictors = {}
model_paths = {
    'prototype': '../models/prototype_lightgbm_model.pkl',
    'balanced': '../models/balanced_lightgbm_model.pkl'
}

for model_name, model_path in model_paths.items():
    try:
        predictor = AQIPredictor(model_path='../models/')
        if model_name == 'prototype':
            # Load prototype model with different filename
            if os.path.exists(model_path):
                predictor.load_model(model_path)
                predictors[model_name] = predictor
                log_event(logging.INFO, f"{model_name.title()} model loaded successfully", operation="prediction")  # [ADDED]
            else:
                log_event(logging.WARNING, f"Prototype model not found at {model_path}", operation="prediction")     # [ADDED]
        elif model_name == 'balanced':
            # Load balanced model with different filename
            if os.path.exists(model_path):
                predictor.load_model(model_path)
                predictors[model_name] = predictor
                log_event(logging.INFO, f"{model_name.title()} model loaded successfully", operation="prediction")  # [ADDED]
            else:
                log_event(logging.WARNING, f"Balanced model not found at {model_path}", operation="prediction")     # [ADDED]
        else:
            # Load improved model (default)
            if predictor.load_model():
                predictors[model_name] = predictor
                log_event(logging.INFO, f"{model_name.title()} model loaded successfully", operation="prediction")  # [ADDED]
            else:
                log_event(logging.WARNING, f"No {model_name} model found", operation="prediction")                   # [ADDED]
    except Exception as e:
        logger.exception(f"Failed to load {model_name} model", extra={"operation": "prediction"})  # [CHANGED]

# Set default predictor
predictor = predictors.get('balanced')

# -------------------------------
# Routes
# -------------------------------

@app.route('/')
def index():
    """Serve frontend dashboard"""
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'model_loaded': bool(predictor and predictor.model is not None),
        'database_connected': False  # Using CSV files instead
    })


@app.route('/api/counties', methods=['GET'])
def get_counties():
    """Get list of available counties"""
    try:
        log_event(logging.INFO, "Fetching counties", operation="ingestion")  # [ADDED]
        
        # Use CSV data source
        if data_source is None:
            return jsonify({'success': False, 'error': 'Data source not available'}), 500
        
        counties = data_source.get_counties()
        log_event(logging.INFO, f"Counties retrieved: {len(counties)}", operation="ingestion")  # [ADDED]
        
        return jsonify({'success': True, 'counties': counties, 'count': len(counties), 'source': 'csv'})
        
    except Exception as e:
        logger.exception("Error fetching counties", extra={"operation": "ingestion"})  # [CHANGED]
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/aqi/historical', methods=['GET'])
def get_historical_aqi():
    """
    Get historical AQI data for a county
    Query params: county, state, days (default: 30)
    """
    try:
        county = request.args.get('county')
        state = request.args.get('state')
        days = int(request.args.get('days', 30))

        log_event(logging.INFO, f"Historical request: county={county}, state={state}, days={days}",
                  operation="validation")
        
        if not county or not state:
            return jsonify({'success': False, 'error': 'County and state parameters are required'}), 400
        
        # Use CSV data source
        if data_source is None:
            return jsonify({'success': False, 'error': 'Data source not available'}), 500
        
        historical_data = data_source.get_historical_data(county, state, days)
        log_event(logging.INFO, f"Historical rows returned: {len(historical_data)}",
                  operation="ingestion")
        
        return jsonify({
            'success': True,
            'county': county,
            'state': state,
            'days': days,
            'data': historical_data,
            'count': len(historical_data),
            'source': 'csv'
        })
        
    except Exception as e:
        logger.exception("Error fetching historical data", extra={"operation": "ingestion"})  # [CHANGED]
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/aqi/predict', methods=['POST'])
def predict_aqi():
    """
    Predict next-day AQI for a county
    Body: { "county": "string", "state": "string", "model": "string", "days": int }
    """
    try:
        t0 = datetime.utcnow()
        data = request.get_json()
        county = data.get('county')
        state = data.get('state')
        model_type = data.get('model', 'balanced')  # Default to balanced model
        days = data.get('days', 1)  # Number of days to forecast

        log_event(logging.INFO, f"Prediction request: county={county}, state={state}, model={model_type}, days={days}",
                  operation="validation")
        
        if not county or not state:
            return jsonify({'success': False, 'error': 'County and state are required'}), 400
        
        # Get the selected model
        selected_predictor = predictors.get(model_type)
        if selected_predictor is None or selected_predictor.model is None:
            return jsonify({'success': False, 'error': f'{model_type.title()} model not loaded. Please train model first.'}), 503
        
        # Get recent data for features
        if data_source is None:
            return jsonify({'success': False, 'error': 'Data source not available'}), 500
        
        recent_df = data_source.get_recent_data_for_prediction(county, state, 30)
        if recent_df is None or len(recent_df) < 7:
            return jsonify({'success': False, 'error': f'Insufficient historical data for {county}, {state}. Need at least 7 days.'}), 400
        
        recent_df = recent_df.sort_values('Date')
        log_event(logging.INFO, f"Recent rows for features: {len(recent_df)}",
                  operation="feature_generation")
        
        # Create lag & rolling features (simplified)
        features = {
            'aqi_lag_1': recent_df['AQI'].iloc[-1],
            'aqi_lag_2': recent_df['AQI'].iloc[-2] if len(recent_df) >= 2 else recent_df['AQI'].iloc[-1],
            'aqi_lag_3': recent_df['AQI'].iloc[-3] if len(recent_df) >= 3 else recent_df['AQI'].iloc[-1],
            'aqi_lag_7': recent_df['AQI'].iloc[-7] if len(recent_df) >= 7 else recent_df['AQI'].iloc[-1],
            'aqi_rolling_7': recent_df['AQI'].tail(7).mean(),
            'aqi_rolling_14': recent_df['AQI'].tail(14).mean() if len(recent_df) >= 14 else recent_df['AQI'].tail(7).mean(),
            'aqi_rolling_30': recent_df['AQI'].mean()
        }
        log_event(logging.INFO, "Lag/rolling features prepared", operation="feature_generation")  # [ADDED]
        
        # Create feature vector based on selected model
        if model_type == 'prototype':
            # Prototype model expects exactly 10 features: State Code, County Code, 5 Defining Parameters, 3 lag features
            # Get county and state codes
            county_data = recent_df.iloc[0]
            state_code = county_data.get('State Code', 1)
            county_code = county_data.get('County Code', 1)
            X_forecast = np.array([[
                state_code, county_code,
                0, 0, 0, 0, 0,
                features['aqi_lag_1'], features['aqi_lag_3'], features['aqi_lag_7']
            ]])
        elif model_type == 'balanced':
            county_data = recent_df.iloc[0]
            state_code = county_data.get('State Code', 1)  # Default to 1 if not found
            county_code = county_data.get('County Code', 1)  # Default to 1 if not found
            # Calculate additional features for balanced model
            aqi_rolling_3 = recent_df['AQI'].tail(3).mean() if len(recent_df) >= 3 else features['aqi_lag_1']
            aqi_std_7 = recent_df['AQI'].tail(7).std() if len(recent_df) >= 7 else 0
            # Get current date for temporal features
            current_date = datetime.utcnow()
            day_of_week = current_date.weekday()
            month = current_date.month
            X_forecast = np.array([[
                state_code, county_code,
                features['aqi_lag_1'], features['aqi_lag_3'], features['aqi_lag_7'],
                features.get('aqi_lag_14', features['aqi_lag_7']),
                features['aqi_rolling_7'],
                day_of_week, month,
                aqi_rolling_3, aqi_std_7
            ]])
        else:
            # Improved model features
            X_forecast = np.array([[
                features['aqi_lag_1'], features['aqi_lag_2'], features['aqi_lag_3'],
                features['aqi_lag_7'], features['aqi_rolling_7'],
                features['aqi_rolling_14'], features['aqi_rolling_30']
            ]])
            if selected_predictor.feature_names and len(selected_predictor.feature_names) > X_forecast.shape[1]:
                padding = np.zeros((1, len(selected_predictor.feature_names) - X_forecast.shape[1]))
                X_forecast = np.hstack([X_forecast, padding])

        # Scale features
        if model_type == 'prototype':
            # Load prototype scaler
            try:
                import pickle
                with open('../models/prototype_pipeline.pkl', 'rb') as f:
                    prototype_scaler = pickle.load(f)
                X_forecast_scaled = prototype_scaler.transform(X_forecast)
            except Exception:
                logger.exception("Failed to load prototype scaler", extra={"operation": "feature_generation"})  # [CHANGED]
                return jsonify({'success': False, 'error': 'Failed to load prototype model scaler'}), 500
        elif model_type == 'balanced':
            # Load balanced scaler
            try:
                import pickle
                with open('../models/balanced_pipeline.pkl', 'rb') as f:
                    balanced_scaler = pickle.load(f)
                X_forecast_scaled = balanced_scaler.transform(X_forecast)
            except Exception:
                logger.exception("Failed to load balanced scaler", extra={"operation": "feature_generation"})  # [CHANGED]
                return jsonify({'success': False, 'error': 'Failed to load balanced model scaler'}), 500
        else:
            # Use improved model's built-in scaling
            X_forecast_scaled = X_forecast
        
        # Multi-day iterative forecasting
        predictions = []
        current_date = datetime.utcnow()
        # Use current features as starting point
        current_features = features.copy()
        
        for day in range(days):
            forecast_date = current_date + timedelta(days=day + 1)
            # Create feature vector for this day
            if model_type == 'prototype':
                county_data = recent_df.iloc[0]
                state_code = county_data.get('State Code', 1)
                county_code = county_data.get('County Code', 1)
                X_day = np.array([[
                    state_code, county_code, 0, 0, 0, 0, 0,  # Defining parameters
                    current_features['aqi_lag_1'],
                    current_features['aqi_lag_3'],
                    current_features['aqi_lag_7']
                ]])
                # Scale with prototype scaler
                with open('../models/prototype_pipeline.pkl', 'rb') as f:
                    prototype_scaler = pickle.load(f)
                X_day_scaled = prototype_scaler.transform(X_day)
            elif model_type == 'balanced':
                county_data = recent_df.iloc[0]
                state_code = county_data.get('State Code', 1)
                county_code = county_data.get('County Code', 1)
                aqi_rolling_3 = current_features.get('aqi_rolling_3', current_features['aqi_lag_1'])
                aqi_std_7 = current_features.get('aqi_std_7', 0)
                X_day = np.array([[
                    state_code, county_code,
                    current_features['aqi_lag_1'],
                    current_features['aqi_lag_3'],
                    current_features['aqi_lag_7'],
                    current_features.get('aqi_lag_14', current_features['aqi_lag_7']),
                    current_features['aqi_rolling_7'],
                    forecast_date.weekday(),
                    forecast_date.month,
                    aqi_rolling_3,
                    aqi_std_7
                ]])
                # Scale with balanced scaler
                with open('../models/balanced_pipeline.pkl', 'rb') as f:
                    balanced_scaler = pickle.load(f)
                X_day_scaled = balanced_scaler.transform(X_day)
            else:
                raise ValueError(f"Unknown model type: {model_type}")
            # Make prediction for this day
            day_prediction = selected_predictor.forecast(
                X_day_scaled,
                county_name=county,
                state_name=state,
                forecast_date=forecast_date,
                # Don't store intermediate predictions
                store_predictions=False
            )
            
            predictions.append(day_prediction)
            # Update features for next iteration (feedback loop)
            predicted_aqi = day_prediction['predicted_aqi']
            # Shift lag features
            current_features['aqi_lag_7'] = current_features['aqi_lag_3']
            current_features['aqi_lag_3'] = current_features['aqi_lag_1']
            current_features['aqi_lag_1'] = predicted_aqi
            # Update rolling averages (simplified)
            if 'aqi_rolling_7' in current_features:
                current_features['aqi_rolling_7'] = (current_features['aqi_rolling_7'] * 6 + predicted_aqi) / 7
            if 'aqi_rolling_14' in current_features:
                current_features['aqi_rolling_14'] = (current_features['aqi_rolling_14'] * 13 + predicted_aqi) / 14
            if 'aqi_rolling_30' in current_features:
                current_features['aqi_rolling_30'] = (current_features['aqi_rolling_30'] * 29 + predicted_aqi) / 30
        
        elapsed_ms = int((datetime.utcnow() - t0).total_seconds() * 1000)  # [ADDED]
        log_event(logging.INFO, f"Prediction completed in {elapsed_ms} ms (days={days})",
                  operation="prediction")  # [ADDED]
        
        # Return single prediction for 1 day, array for multiple days
        if days == 1:
            return jsonify({
                'success': True,
                'county': county,
                'state': state,
                'forecast_date': predictions[0]['forecast_date'],
                'prediction': predictions[0]
            })
        else:
            return jsonify({
                'success': True,
                'county': county,
                'state': state,
                'forecast_days': days,
                'predictions': predictions
            })
        
    except Exception as e:
        logger.exception("Error making prediction", extra={"operation": "prediction"})  # [CHANGED]
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/aqi/refresh', methods=['POST'])
def refresh_data():
    """
    Refresh dashboard data - re-run pipeline and generate new predictions
    Body: { "county": "string", "state": "string" }
    """
    try:
        data = request.get_json()
        county = data.get('county')
        state = data.get('state')

        log_event(logging.INFO, f"Refresh request: county={county}, state={state}", operation="validation")  # [ADDED]
        
        if not county or not state:
            return jsonify({'success': False, 'error': 'County and state are required'}), 400
        
        log_event(logging.INFO, "Refreshing historical data", operation="ingestion")  # [ADDED]
        # Get fresh historical data
        historical_response = get_historical_aqi()
        historical_json = historical_response.get_json()
        
        log_event(logging.INFO, "Refreshing prediction", operation="prediction")  # [ADDED]
        # Generate new prediction
        predict_response = predict_aqi()
        prediction_json = predict_response.get_json()
        
        return jsonify({
            'success': True,
            'county': county,
            'state': state,
            'timestamp': datetime.utcnow().isoformat(),
            'historical': historical_json,
            'prediction': prediction_json
        })
        
    except Exception as e:
        logger.exception("Error refreshing data", extra={"operation": "ingestion"})  # [CHANGED]
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/model/metrics', methods=['GET'])
def get_model_metrics():
    """Get model performance metrics for all available models"""
    try:
        model_type = request.args.get('model', 'improved')
        selected_predictor = predictors.get(model_type)

        log_event(logging.INFO, f"Metrics request: model={model_type}", operation="validation")  # [ADDED]
        
        if selected_predictor and selected_predictor.metrics:
            return jsonify({
                'success': True,
                'model_type': model_type,
                'metrics': selected_predictor.metrics,
                'version': selected_predictor.model_version
            })
        else:
            return jsonify({'success': False, 'error': f'No metrics available for {model_type} model'}), 404
            
    except Exception as e:
        logger.exception("Error fetching metrics", extra={"operation": "validation"})  # [CHANGED]
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/categories', methods=['GET'])
def get_aqi_categories():
    """Get AQI category definitions and colors"""
    return jsonify({'success': True, 'categories': Config.AQI_CATEGORIES})


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'success': False, 'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'success': False, 'error': 'Internal server error'}), 500


if __name__ == '__main__':
    separator = "=" * 60
    log_event(logging.INFO, "Starting CLAP Flask API Server", operation="startup")  # [ADDED]
    logger.info(separator)
    logger.info(f"Environment: {Config.FLASK_ENV}")
    logger.info(f"Debug mode: {Config.DEBUG}")
    logger.info(f"Database: {Config.DB_NAME}")
    logger.info(separator)
    
    # Run Flask app
    app.run(host='0.0.0.0', port=5001, debug=Config.DEBUG)
