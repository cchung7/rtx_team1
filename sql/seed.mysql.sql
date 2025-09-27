
--Test data for AQI Predictor pipeline via MySQL

--Clear existing rows
DELETE FROM features_train;
DELETE FROM wx_forecast;
DELETE FROM aqi_daily;

--AQI history - 3 days
INSERT INTO aqi_daily (city_id, date, aqi_value, aqi_category, primary_pollutant)
VALUES
  ('DAL-TX', '2025-09-09', 60, 'Moderate', 'PM2.5'),
  ('DAL-TX', '2025-09-10', 48, 'Good', 'PM2.5'),
  ('DAL-TX', '2025-09-11', 82, 'Moderate', 'Ozone');

--Weather forecast for next day - t+1 = 2025-09-12
INSERT INTO wx_forecast (city_id, date, features_json)
VALUES
  ('DAL-TX', '2025-09-12',
   JSON_OBJECT(
     'max_temp', 91,
     'min_temp', 75,
     'mean_temp', 83,
     'mean_rh', 0.55,
     'mean_wind', 9.0,
     'max_pop', 0.2,
     'has_smoke', 0,
     'has_haze', 0,
     'has_rain', 0
   ));
