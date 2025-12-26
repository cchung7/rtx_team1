# backend/routes/aqi_utils.py

import logging
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
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
    # Normalize dates for time-based windows (defensive copy)
    recent_df = recent_df.copy()
    recent_df["Date"] = pd.to_datetime(recent_df["Date"], errors="coerce")
    recent_df = recent_df.dropna(subset=["Date"]).sort_values("Date")

    aqi = recent_df["AQI"]
    last_val = aqi.iloc[-1]

    # AQI-lags
    feats = {
        "aqi_lag_1": last_val,
        "aqi_lag_2": aqi.iloc[-2] if len(aqi) >= 2 else last_val,
        "aqi_lag_3": aqi.iloc[-3] if len(aqi) >= 3 else last_val,
        "aqi_lag_7": aqi.iloc[-7] if len(aqi) >= 7 else last_val,
        "aqi_lag_14": aqi.iloc[-14] if len(aqi) >= 14 else (aqi.iloc[-7] if len(aqi) >= 7 else last_val),
    }

    # Time-based rolling means
    end_date = recent_df["Date"].iloc[-1]

    def mean_last_days(days: int):
        start = end_date - pd.Timedelta(days=days)
        window = recent_df.loc[recent_df["Date"] > start, "AQI"]
        return window.mean() if not window.empty else aqi.mean()

    feats.update({
        "aqi_rolling_7": mean_last_days(7),
        "aqi_rolling_14": mean_last_days(14),
        "aqi_rolling_30": mean_last_days(30),
    })

    return feats, recent_df


def vector_for_model(model_type, features, county_row, when: datetime):
    """
    Convert features into the correct input vector for the selected model,
    then apply the appropriate preprocessing pipeline.
    """

    state_code = county_row.get("state_code", None)
    if state_code is None:
        state_code = county_row.get("State Code", None)

    county_code = county_row.get("county_code", None)
    if county_code is None:
        county_code = county_row.get("County Code", None)

    if state_code is None or county_code is None:
        raise KeyError(
            "Missing required fields for model vectorization. "
            "Expected columns: 'state_code' and 'county_code' "
            "(or legacy 'State Code' and 'County Code')."
        )

    if model_type == "prototype":
        X = np.array([[
            state_code,
            county_code,
            0, 0, 0, 0, 0,
            features["aqi_lag_1"],
            features["aqi_lag_3"],
            features["aqi_lag_7"],
        ]])

        with open("../models/prototype_pipeline.pkl", "rb") as f:
            pipeline = pickle.load(f)

    elif model_type == "balanced":
        # 11 Features for the balanced model
        X = np.array([[
            state_code,                               
            county_code,                               
            features["aqi_lag_1"],                  
            features["aqi_lag_3"],                
            features["aqi_lag_7"],                       
            features["aqi_lag_14"],                      
            features["aqi_rolling_7"],                   
            when.weekday(),                              
            when.month,                                  
            features.get("aqi_rolling_3", features["aqi_lag_1"]),  
            features.get("aqi_std_7", 0.0),                        
        ]])

        with open("../models/balanced_pipeline.pkl", "rb") as f:
            pipeline = pickle.load(f)

    else:
        raise ValueError(f"Unknown model type: {model_type}")

    return pipeline.transform(X)


def iterative_forecast(selected_predictor, model_type, recent_df, base_features, days, county, state):
    """
    Forecast AQI for the next N days using iterative autoregressive updates.
    """
    predictions = []
    current_date = datetime.utcnow()
    current_features = base_features.copy()

    # County row used for state/county codes
    county_row = recent_df.iloc[0]

    for day in range(days):
        forecast_date = current_date + timedelta(days=day + 1)

        X_day_scaled = vector_for_model(model_type, current_features, county_row, forecast_date)

        day_pred = selected_predictor.forecast(
            X_day_scaled,
            county_name=county,
            state_name=state,
            forecast_date=forecast_date,
            store_predictions=False
        )
        predictions.append(day_pred)

        # Feedback loop: shift lags forward
        yhat = day_pred["predicted_aqi"]

        # Maintain lag-14 as the previous lag-7 (closest approximation under iterative prediction)
        current_features["aqi_lag_14"] = current_features.get("aqi_lag_7", yhat)
        current_features["aqi_lag_7"] = current_features.get("aqi_lag_3", yhat)
        current_features["aqi_lag_3"] = current_features.get("aqi_lag_1", yhat)
        current_features["aqi_lag_1"] = yhat

        # Rolling updates
        if "aqi_rolling_7" in current_features:
            current_features["aqi_rolling_7"] = (current_features["aqi_rolling_7"] * 6 + yhat) / 7
        if "aqi_rolling_14" in current_features:
            current_features["aqi_rolling_14"] = (current_features["aqi_rolling_14"] * 13 + yhat) / 14
        if "aqi_rolling_30" in current_features:
            current_features["aqi_rolling_30"] = (current_features["aqi_rolling_30"] * 29 + yhat) / 30

    return predictions