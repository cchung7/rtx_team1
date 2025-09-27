import json, sys, re, math

RE_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
VALID = ["Good","Moderate","USG","Unhealthy+"]

def fail(msg: str):
    sys.exit(f"Error: {msg}")

#Load
try:
    with open("data/tomorrow.json") as f:
        pred = json.load(f)
except FileNotFoundError:
    fail("tomorrow.json missing")
except json.JSONDecodeError as e:
    fail(f"tomorrow.json invalid JSON: {e}")

#Required keys
for key in ["date","predicted_category","proba","model_version"]:
    if key not in pred:
        fail(f"Missing key: {key}")

date = pred["date"]
if not isinstance(date, str) or not RE_DATE.match(date):
    fail("date must be YYYY-MM-DD string")

mv = pred["model_version"]
if not isinstance(mv, str) or not mv.strip():
    fail("model_version must be a non-empty string")

#Category checks
pc = pred["predicted_category"]
if pc not in VALID:
    fail(f"Invalid category {pc}")

#Probabilities
proba = pred["proba"]
if not isinstance(proba, dict):
    fail("proba must be an object/dict")

#Keys/4 labels
keys = set(proba.keys())
if keys != set(VALID):
    missing = set(VALID) - keys
    extra = keys - set(VALID)
    if missing:
        fail(f"proba missing labels: {sorted(missing)}")
    if extra:
        fail(f"proba has unknown labels: {sorted(extra)}")

#Values/numeric & finite
vals = []
for k, v in proba.items():
    if not isinstance(v, (int, float)) or not math.isfinite(v):
        fail(f"proba[{k}] must be a finite number")
    vals.append(float(v))

s = sum(vals)
if not 0.95 <= s <= 1.05:
    fail(f"proba sums to {s:.6f}, not ~1")

argmax = max(proba, key=proba.get)
if argmax != pc:
    fail(f"predicted_category ({pc}) != argmax(proba) ({argmax})")

print("Success: tomorrow.json passed check")
