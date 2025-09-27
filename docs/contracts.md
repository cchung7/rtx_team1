<!-- -------------------------------------------------------
Contracts v0.2
This defines all project-level data & API contracts
  - Documents schemas for raw + derived tables
  - Defines JSON structures (e.g., tomorrow.json, model_meta.json)
  - Establishes label set for classification and time/date formats
  - Records baseline requirements for evaluation
Notes:
  - This file is version v0.2
  - Any breaking change requires a new ADR 
  - Contracts must stay stable once published
------------------------------------------------------- -->

# Contracts

- **Dates**: local TZ; format `YYYY-MM-DD`
- **Labels**: {Good, Moderate, USG, Unhealthy+}
- **Baseline policy**: All trained models must be evaluated against the **Majority Class Baseline**.

---

## Files

- **data/features_train.csv**  
  → Feature table (AQI lags at t, forecast features for t+1, derived calendar features, label `y_cat_t1`)

- **data/tomorrow.json**  
  → Daily prediction contract:
  ```json
  {
    "date": "YYYY-MM-DD",
    "predicted_category": "Moderate",
    "proba": {"Good": 0.18, "Moderate": 0.55, "USG": 0.19, "Unhealthy+": 0.08},
    "model_version": "rf_v1"
  }
