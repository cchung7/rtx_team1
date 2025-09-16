# This file builds the derived training dataset i.e. features_train
# - Reads the tables aqi_daily and wx_forecast and adds lagged AQI values and forecast attributes
# - It then aligns them with tomorrow’s observed AQI category, writes features_train and replaces the table each run
# Notes:
# - Do not edit features_train.csv. It’s auto generated.
# - Allows future extenions with new feature engineering


import json
import pandas as pd
from sqlalchemy import text
from .db import get_engine

FEATURE_COLS = [
    "city_id","date",
    "aqi_val_t","aqi_val_t_1","aqi_val_t_2",
    "wx_mean_temp_t1","wx_mean_rh_t1","wx_mean_wind_t1",
    "y_cat_t1",
]

def build_features():
    eng = get_engine()

    #Tables
    with eng.connect() as c:
        aqi = pd.read_sql(text("SELECT city_id, date, aqi_value, aqi_category FROM aqi_daily"), c, parse_dates=["date"])
        wx  = pd.read_sql(text("SELECT city_id, date, features_json FROM wx_forecast"), c, parse_dates=["date"])

    #Sort/compute lags per city
    aqi = aqi.sort_values(["city_id","date"]).copy()
    aqi["aqi_val_t"]   = aqi["aqi_value"]
    aqi["aqi_val_t_1"] = aqi.groupby("city_id")["aqi_value"].shift(1)
    aqi["aqi_val_t_2"] = aqi.groupby("city_id")["aqi_value"].shift(2)

    #y at t+1 
    y_next = aqi[["city_id","date","aqi_category"]].rename(
        columns={"date":"d_t1","aqi_category":"y_cat_t1"}
    )

    #JSON to numeric columns
    if not wx.empty:
        fj = wx["features_json"].map(lambda s: s if isinstance(s, dict) else json.loads(s))
        wx_feats = pd.DataFrame({
            "city_id": wx["city_id"].values,
            "d_t1":    wx["date"].values,  # forecast target day = t+1
            "wx_mean_temp_t1": fj.map(lambda d: d.get("mean_temp")),
            "wx_mean_rh_t1":   fj.map(lambda d: d.get("mean_rh")),
            "wx_mean_wind_t1": fj.map(lambda d: d.get("mean_wind")),
        })
    else:
        wx_feats = pd.DataFrame(columns=["city_id","d_t1","wx_mean_temp_t1","wx_mean_rh_t1","wx_mean_wind_t1"])

    #Align features 
    base = aqi.rename(columns={"date":"t"})[[
        "city_id","t","aqi_val_t","aqi_val_t_1","aqi_val_t_2"
    ]].copy()
    base["d_t1"] = base["t"] + pd.Timedelta(days=1)

    feat = (base
            .merge(wx_feats, on=["city_id","d_t1"], how="left")
            .merge(y_next,    on=["city_id","d_t1"], how="left"))

    out = feat.rename(columns={"t":"date"})[
        ["city_id","date","aqi_val_t","aqi_val_t_1","aqi_val_t_2",
         "wx_mean_temp_t1","wx_mean_rh_t1","wx_mean_wind_t1","y_cat_t1"]
    ].sort_values(["city_id","date"])

    #Replace table every run
    with eng.begin() as c:
        out.to_sql("features_train", c, if_exists="replace", index=False)

    try:
        with eng.begin() as c:
            c.exec_driver_sql("CREATE INDEX IF NOT EXISTS idx_feat_city_date ON features_train(city_id, date)")
    except Exception:
        pass

    print(f"[features] wrote features_train with {len(out)} rows")

if __name__ == "__main__":
    build_features()
