-- This defines raw tables for EPA AQI and NWS forecasts
-- cities: lookup table for city metadata
-- aqi_daily: observed AQI values by date
-- wx_forecast: weather forecast JSON by date
-- Notes:
--  DO NOT add features_train here. It is derived in Python
--  Keep schemas minimal and engine specific i.e., SQLite/MySQL


PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;

--Cities
CREATE TABLE IF NOT EXISTS cities (
  city_id TEXT PRIMARY KEY,   
  name    TEXT NOT NULL,
  lat     REAL NOT NULL,
  lon     REAL NOT NULL,
  tz      TEXT NOT NULL
);

--EPA AQS daily AQI
CREATE TABLE IF NOT EXISTS aqi_daily (
  city_id TEXT NOT NULL,
  date    TEXT NOT NULL,     
  aqi_value INTEGER,
  aqi_category TEXT,          
  primary_pollutant TEXT,
  PRIMARY KEY (city_id, date),
  FOREIGN KEY (city_id) REFERENCES cities(city_id)
);

--NWS forecast t+1
CREATE TABLE IF NOT EXISTS wx_forecast (
  city_id TEXT NOT NULL,
  date    TEXT NOT NULL,      
  features_json TEXT NOT NULL, 
  PRIMARY KEY (city_id, date),
  FOREIGN KEY (city_id) REFERENCES cities(city_id)
);


CREATE INDEX IF NOT EXISTS idx_aqi_city_cat   ON aqi_daily(city_id, aqi_category);
CREATE INDEX IF NOT EXISTS idx_wx_city_date   ON wx_forecast(city_id, date);


