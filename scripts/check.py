# This is a test for model output, tomorrow.json
# - Opens data/tomorrow.json, verifies required keys: date, predicted_category, proba, model_version and checks that predicted_category is in the valid AQI label set
# - It also ensures probabilities are numeric and sum ~1
#
# - This is used to guard against broken pipeline runs or bad JSON output 
# - Also used to ensure code that breaks the prediction contract (contracts.md) isn't merged. 


import json, sys


try:
    with open("data/tomorrow.json") as f:
        pred = json.load(f)
except FileNotFoundError:
    sys.exit("Error: tomorrow.json missing")

#Required keys
for key in ["date","predicted_category","proba","model_version"]:
    if key not in pred:
        sys.exit(f"Error: Missing key: {key}")

#Class check
valid = {"Good","Moderate","USG","Unhealthy+"}
if pred["predicted_category"] not in valid:
    sys.exit(f"Error: Invalid category {pred['predicted_category']}")

#Probability sanity
proba = pred.get("proba",{})
if not isinstance(proba, dict) or not proba:
    sys.exit("Error: probability invalid or empty")
if not all(isinstance(v,(int,float)) for v in proba.values()):
    sys.exit("Error: probability values must be numeric")
s = sum(proba.values())
if not 0.95 <= s <= 1.05:
    sys.exit(f"Error:  proba sums to {s:.3f}, not ~1")

print("Success: tomorrow.json passed check")
