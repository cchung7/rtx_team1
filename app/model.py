import json, pathlib
import pandas as pd
from collections import Counter

DATA_DIR = pathlib.Path("data")

CLASSES = ["Good","Moderate","USG","Unhealthy+"] 

def maj_base_mac_f1(df: pd.DataFrame) -> float:
    from sklearn.metrics import f1_score
    y = df["y_cat_t1"].values
    maj = Counter(y).most_common(1)[0][0]
    y_hat = [maj]*len(y)
    return f1_score(y, y_hat, average="macro")

def train_logreg(df: pd.DataFrame) -> dict:
    #Temp - actual training w/ scikit-learn?
    meta = {
        "version": "YYYY-MM-DD",
        "features": [c for c in df.columns if c not in ("city_id","date","y_cat_t1")],
        "metrics": {"macro_f1": 0.00, "majority_macro_f1": maj_base_mac_f1(df)},
        # fill with coefficients later
        "explanations": {}  
    }
    (DATA_DIR.parent / "models").mkdir(exist_ok=True)
    (DATA_DIR.parent / "models" / "model_meta.json").write_text(json.dumps(meta, indent=2))
    return meta

# **** Future extension, city_id multiple cities ****
def predict_tomorrow(city_id: str = "DAL-TX"):
    #Temp - load trained model + real features
    out = {
        "date": "YYYY-MM-DD",
        "predicted_category": "Moderate",
        "proba": {"Good":0.25,"Moderate":0.50,"USG":0.15,"Unhealthy+":0.10},
        "model_version": "YYYY-MM-DD"
    }
    (DATA_DIR / "tomorrow.json").write_text(json.dumps(out, indent=2))
    return out

if __name__ == "__main__":
    print("[model] stubs ready.")
