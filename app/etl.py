from sqlalchemy import text
from .db import get_engine

def fetch_aqi(city_id: str):
    eng = get_engine()
    #Temp t - replace with EPA data
    samp = [
        {"date": "2025-09-09", "aqi_value": 60, "aqi_category": "Moderate", "primary_pollutant": "PM2.5"},
        {"date": "2025-09-10", "aqi_value": 48, "aqi_category": "Good",     "primary_pollutant": "PM2.5"},
        {"date": "2025-09-11", "aqi_value": 82, "aqi_category": "Moderate", "primary_pollutant": "Ozone"},
    ]
    with eng.begin() as c:
        for r in samp:
            c.exec_driver_sql(
                "INSERT INTO aqi_daily (city_id,date,aqi_value,aqi_category,primary_pollutant) "
                "VALUES (:city,:date,:val,:cat,:pol) "
                "ON CONFLICT(city_id,date) DO UPDATE SET "
                "aqi_value=excluded.aqi_value, aqi_category=excluded.aqi_category, primary_pollutant=excluded.primary_pollutant"
                if eng.url.get_backend_name()=="sqlite" else
                "INSERT INTO aqi_daily (city_id,date,aqi_value,aqi_category,primary_pollutant) "
                "VALUES (:city,:date,:val,:cat,:pol) "
                "ON DUPLICATE KEY UPDATE aqi_value=VALUES(aqi_value), aqi_category=VALUES(aqi_category), primary_pollutant=VALUES(primary_pollutant)",
                {"city": city_id, "date": r["date"], "val": r["aqi_value"], "cat": r["aqi_category"], "pol": r["primary_pollutant"]},
            )

def fetch_weather(city_id: str):
    eng = get_engine()
    #Temp t + 1
    features_json = {
        "max_temp": 91, "min_temp": 75, "mean_temp": 83,
        "mean_rh": 0.55, "mean_wind": 9.0, "max_pop": 0.2,
        "has_smoke": 0, "has_haze": 0, "has_rain": 0
    }
    with eng.begin() as c:
        c.exec_driver_sql(
            "INSERT INTO wx_forecast (city_id,date,features_json) VALUES (:city,:date, :js) "
            "ON CONFLICT(city_id,date) DO UPDATE SET features_json=:js"
            if eng.url.get_backend_name()=="sqlite" else
            "INSERT INTO wx_forecast (city_id,date,features_json) VALUES (:city,:date, CAST(:js AS JSON)) "
            "ON DUPLICATE KEY UPDATE features_json=VALUES(features_json)",
            {"city": city_id, "date": "2025-09-12", "js": str(features_json).replace("'", '"')},
        )
