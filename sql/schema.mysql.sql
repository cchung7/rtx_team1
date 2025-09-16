
-- This defines the raw input tables for MySQL
--  cities: lookup table for city metadata (id, name, lat/lon, tz)
--  aqi_daily: observed daily AQI values (value + category + pollutant)
--  wx_forecast: daily weather forecast JSON blobs (mean temp, humidity, wind, etc.)
-- Notes:
--  Do NOT define features_train here. That is derived and rebuilt each run by app/features.py
--  Keep only stable input tables in schema files
--  Use this schema when running with a MySQL backend (web app backend)


--Cities
CREATE TABLE IF NOT EXISTS cities (
  city_id VARCHAR(32) PRIMARY KEY,   
  name    VARCHAR(128) NOT NULL,
  lat     DOUBLE NOT NULL,
  lon     DOUBLE NOT NULL,
  tz      VARCHAR(64) NOT NULL
);

--EPA AQS daily AQI
CREATE TABLE IF NOT EXISTS aqi_daily (
  city_id VARCHAR(32) NOT NULL,
  date    DATE NOT NULL,             
  aqi_value INT,
  aqi_category VARCHAR(32),          
  primary_pollutant VARCHAR(64),
  PRIMARY KEY (city_id, date),
  CONSTRAINT fk_city_aqi FOREIGN KEY (city_id) REFERENCES cities(city_id)
);

--NWS forecast t+1
CREATE TABLE IF NOT EXISTS wx_forecast (
  city_id VARCHAR(32) NOT NULL,
  date    DATE NOT NULL,             
  features_json JSON NOT NULL,       
  PRIMARY KEY (city_id, date),
  CONSTRAINT fk_city_wx FOREIGN KEY (city_id) REFERENCES cities(city_id)
);


CREATE INDEX idx_aqi_city_cat ON aqi_daily (city_id, aqi_category);
