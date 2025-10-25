# backend/routes/aqi_utils.py

import logging
from datetime import datetime, timedelta
import numpy as np
import os
import pickle
from flask import current_app

def logger():
    return current_app.extensions["logger"]

def log_event(level, msg, operation="general", **kv):
    current_app.extensions["log_event"](level, msg, operation, **kv)

def ds():
    return current_app.extensions.get("data_source")

def predictors():
    return current_app.extensions.get("predictors", {})

def get_predictor(model_key: str):
    return predictors().get(model_key)

def build_features_from_recent(recent_df):
    recent_df = recent_df.sort_values("Date")
    aqi = recent_df["AQI"]
    feats = {
        "aqi_lag_1": aqi.iloc[-1],
        "aqi_lag_2": aqi.iloc[-2] if len(aqi) >= 2 else aqi.iloc[-1],
        "aqi_lag_3": aqi.iloc[-3] if len(aqi) >= 3 else aqi.iloc[-1],
        "aqi_lag_7": aqi.iloc[-7] if len(aqi) >= 7 else aqi.iloc[-1],
        "aqi_rolling_7": aqi.tail(7).mean(),
        "aqi_rolling_14": aqi.tail(14).mean() if len(aqi) >= 14 else aqi.tail(7).mean(),
        "aqi_rolling_30": aqi.mean(),
    }
    return feats, recent_df

def vector_for_model(model_type, features, county_row, when: datetime):
    if model_type == "prototype":
        state_code = county_row.get("State Code", 1)
        county_code = county_row.get("County Code", 1)
        X = np.array([[
            state_code, county_code,
            0, 0, 0, 0, 0,
            features["aqi_lag_1"],
            features["aqi_lag_3"],
            features["aqi_lag_7"],
        ]])
        scaler_path = "../models/prototype_pipeline.pkl"
    elif model_type == "balanced":
        state_code = county_row.get("State Code", 1)
        county_code = county_row.get("County Code", 1)
        aqi_rolling_3 = features.get("aqi_rolling_3", features["aqi_lag_1"])
        aqi_std_7 = features.get("aqi_std_7", 0)
        X = np.array([[
            state_code, county_code,
            features["aqi_lag_1"],
            features["aqi_lag_3"],
            features["aqi_lag_7"],
            features.get("aqi_lag_14", features["aqi_lag_7"]),
            features["aqi_rolling_7"],
            when.weekday(),
            when.month,
            aqi_rolling_3,
            aqi_std_7,
        ]])
        scaler_path = "../models/balanced_pipeline.pkl"
    else:
        raise ValueError(f"Unknown model type: {model_type}")

    # Scale
    try:
        with open(scaler_path, "rb") as f:
            scaler = pickle.load(f)
        X_scaled = scaler.transform(X)
    except Exception:
        logger().exception("Failed to load scaler", extra={"operation": "feature_generation"})
        raise
    return X_scaled

def iterative_forecast(selected_predictor, model_type, recent_df, base_features, days, county, state):
    predictions = []
    current_date = datetime.utcnow()
    current_features = base_features.copy()

    for day in range(days):
        forecast_date = current_date + timedelta(days=day + 1)
        county_row = recent_df.iloc[0]
        X_day_scaled = vector_for_model(model_type, current_features, county_row, forecast_date)

        day_pred = selected_predictor.forecast(
            X_day_scaled,
            county_name=county,
            state_name=state,
            forecast_date=forecast_date,
            store_predictions=False,
        )
        predictions.append(day_pred)

        # Feedback loop
        yhat = day_pred["predicted_aqi"]
        current_features["aqi_lag_7"] = current_features["aqi_lag_3"]
        current_features["aqi_lag_3"] = current_features["aqi_lag_1"]
        current_features["aqi_lag_1"] = yhat
        if "aqi_rolling_7" in current_features:
            current_features["aqi_rolling_7"] = (current_features["aqi_rolling_7"] * 6 + yhat) / 7
        if "aqi_rolling_14" in current_features:
            current_features["aqi_rolling_14"] = (current_features["aqi_rolling_14"] * 13 + yhat) / 14
        if "aqi_rolling_30" in current_features:
            current_features["aqi_rolling_30"] = (current_features["aqi_rolling_30"] * 29 + yhat) / 30

    return predictions
