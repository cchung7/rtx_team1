# Decision: Logistic Regression baseline

Status: Accepted (YYYY-MM-DD)
## Context: 
  - Need explainability + fast retrain
## Options: 
  - LogReg / Decision Tree / XGBoost
## Decision: 
  - Multiclass LogReg (softmax)
  - expose coefficients
## Consequences: 
  - +Transparent
  – May underperform GBMs (MVP)