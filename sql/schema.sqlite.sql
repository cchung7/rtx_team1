PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;

--Cities lookup - join key + geo + tz
CREATE TABLE IF NOT EXISTS cities (
  city_id TEXT PRIMARY KEY,   
  name    TEXT NOT NULL,
  lat     REAL NOT NULL,
  lon     REAL NOT NULL,
  tz      TEXT NOT NULL
);

--EPA AQS daily AQI - history
CREATE TABLE IF NOT EXISTS aqi_daily (
  city_id TEXT NOT NULL,
  date    TEXT NOT NULL,      
  aqi_value INTEGER,
  aqi_category TEXT,          --Good/Moderate/USG/Unhealthy/Very Unhealthy/Hazardous
  primary_pollutant TEXT,
  PRIMARY KEY (city_id, date),
  FOREIGN KEY (city_id) REFERENCES cities(city_id)
);

--NWS forecast features for a target day - t+1
CREATE TABLE IF NOT EXISTS wx_forecast (
  city_id TEXT NOT NULL,
  date    TEXT NOT NULL,      
  features_json TEXT NOT NULL, 
  PRIMARY KEY (city_id, date),
  FOREIGN KEY (city_id) REFERENCES cities(city_id)
);

CREATE INDEX IF NOT EXISTS idx_aqi_city_cat   ON aqi_daily(city_id, aqi_category);
CREATE INDEX IF NOT EXISTS idx_wx_city_date   ON wx_forecast(city_id, date);

--NOTE: Do NOT define features_train here.
--It is a derived table that app/features.py (pandas) rebuilds each run via to_sql(if_exists='replace').
