<!-- -------------------------------------------------------

This defines all project level data & API contracts
  - Documents schemas for raw + derived tables and documents JSON structures i.e. tomorrow.json
  - Records date/time rules i.e. local time zone, date: YYYY-MM-DD and establishes label set for classification
  -  This ensures everyone uses the same inputs/outputs and prevents silent breaking changes
Notes:
  - This file is versioned (v0.1)
  - Any breaking change requires a new ADR (docs/adr)
  - Contracts must stay stable once published
------------------------------------------------------- -->

# Contracts
- Dates: local TZ; formats YYYY-MM-DD
- Labels: {Good, Moderate, USG, Unhealthy+}

## Files
- data/features_train.csv → feature table (lags at t, forecast for t+1, y_cat_t1)
- data/tomorrow.json → {"date","predicted_category","proba":{...},"model_version"}
- models/model_meta.json → {"version","metrics":{"macro_f1":...},"explanations":{feature:score}}

## SQLite schemas (to follow)
- aqi_daily(date, aqi_value, aqi_category, primary_pollutant)
- wx_forecast(date, features_json)
- features_train(...)
