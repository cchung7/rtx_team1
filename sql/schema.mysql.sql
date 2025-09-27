--Cities lookup (join key + geo + tz)
CREATE TABLE IF NOT EXISTS cities (
  city_id VARCHAR(32) PRIMARY KEY,   -- e.g., "DAL-TX"
  name    VARCHAR(128) NOT NULL,
  lat     DOUBLE NOT NULL,
  lon     DOUBLE NOT NULL,
  tz      VARCHAR(64) NOT NULL
);

--EPA AQS daily AQI - history
CREATE TABLE IF NOT EXISTS aqi_daily (
  city_id VARCHAR(32) NOT NULL,
  date    DATE NOT NULL,             
  aqi_value INT,
  aqi_category VARCHAR(32),          --Good/Moderate/USG/Unhealthy/Very Unhealthy/Hazardous
  primary_pollutant VARCHAR(64),
  PRIMARY KEY (city_id, date),
  CONSTRAINT fk_city_aqi FOREIGN KEY (city_id) REFERENCES cities(city_id)
);

--NWS forecast features for a target day - t+1
CREATE TABLE IF NOT EXISTS wx_forecast (
  city_id VARCHAR(32) NOT NULL,
  date    DATE NOT NULL,             
  features_json JSON NOT NULL,      
  PRIMARY KEY (city_id, date),
  CONSTRAINT fk_city_wx FOREIGN KEY (city_id) REFERENCES cities(city_id)
);

CREATE INDEX idx_aqi_city_cat ON aqi_daily (city_id, aqi_category);
