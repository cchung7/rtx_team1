import json
import pathlib
from datetime import date, datetime
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from joblib import dump, load

try:
    from .db import get_engine, engine_flavor
    HAVE_DB = True
except Exception:
    HAVE_DB = False

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
MODELS_DIR = ROOT / "models"

CLASSES: List[str] = ["Good", "Moderate", "USG", "Unhealthy+"]
VALID = set(CLASSES)

MODEL_PATH = MODELS_DIR / "model_rf.pkl"
META_PATH = MODELS_DIR / "model_meta.json"
BASELINE_PATH = MODELS_DIR / "majority_baseline.json"
TOMORROW_PATH = DATA_DIR / "tomorrow.json"
FEATURES_CSV = DATA_DIR / "features_train.csv"


# Utilities
def _ensure_dirs():
    DATA_DIR.mkdir(exist_ok=True, parents=True)
    MODELS_DIR.mkdir(exist_ok=True, parents=True)


def _today_str() -> str:
    return date.today().isoformat()


def _load_features_df() -> pd.DataFrame:
    #Load training feature table. 
    #Priority: CSV at data/features_train.csv. Fallback:  DB table features_train

    if FEATURES_CSV.exists():
        df = pd.read_csv(FEATURES_CSV, parse_dates=["date"])
        return df
    if HAVE_DB:
        eng = get_engine()
        with eng.connect() as c:
            df = pd.read_sql("SELECT * FROM features_train", c, parse_dates=["date"])
        return df
    raise FileNotFoundError("features_train not found (CSV or DB). Run app.features first.")


def _filter_valid_labels(df: pd.DataFrame) -> pd.DataFrame:
    y = df["y_cat_t1"].astype("string")
    mask = y.notna() & y.isin(VALID)
    dropped = int((~mask).sum())
    if dropped:
        print(f"[model] dropped {dropped} rows with invalid/missing y_cat_t1")
    out = df.loc[mask].copy()
    out["y_cat_t1"] = out["y_cat_t1"].astype("string")
    return out


def _get_features_and_target(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series, List[str]]:
    #numeric feature columns by rule: everything except identifiers + target
    exclude = {"city_id", "date", "y_cat_t1"}
    feature_cols = [c for c in df.columns if c not in exclude]
    X = df[feature_cols].copy()

    #errors='coerce'. Fill NaNs with column medians
    for c in feature_cols:
        X[c] = pd.to_numeric(X[c], errors="coerce")
    X = X.fillna(X.median(numeric_only=True))

    y = df["y_cat_t1"].astype("string")
    return X, y, feature_cols


def majority_class_report(y_true: pd.Series) -> Dict[str, object]:
    s = pd.Series(y_true, dtype="string").dropna()
    s = s[s.isin(VALID)]
    if s.empty:
        return {"class": "—", "support": 0, "macro_f1": 0.0, "accuracy": 0.0}
    maj = s.value_counts().idxmax()
    y_hat = pd.Series([maj] * len(s), index=s.index)
    return {
        "class": str(maj),
        "support": int(len(s)),
        "macro_f1": float(f1_score(s, y_hat, average="macro")),
        "accuracy": float(accuracy_score(s, y_hat)),
    }


def _fit_label_encoder(y: pd.Series) -> LabelEncoder:
    le = LabelEncoder()
    le.fit(CLASSES)  #enforce fixed class order
    return le


# ---------- Training ----------
def train_rf(df: pd.DataFrame) -> Dict[str, object]:
    #RandomForest. Compute and store majority class baseline metrics
    #Writes models/model_rf.pkl, models/model_meta.json, models/majority_baseline.json
    
    _ensure_dirs()

    df = _filter_valid_labels(df)
    if df.empty:
        raise ValueError("No valid rows with target labels to train on. Check features build.")

    X, y_str, feature_cols = _get_features_and_target(df)

    baseline = majority_class_report(y_str)

    le = _fit_label_encoder(y_str)
    y = le.transform(y_str)

    #Train/validation split for quick metrics - stratified 
    try:
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
    except ValueError:
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

    #Fit
    clf = RandomForestClassifier(
        n_estimators=300,
        max_depth=None,
        min_samples_leaf=2,
        n_jobs=-1,
        random_state=42,
        class_weight=None,  #we can keep baseline as majority via sponsors RF can handle some imbalance
    )
    clf.fit(X_train, y_train)

    #Eval
    y_val_pred = clf.predict(X_val)
    y_val_proba = clf.predict_proba(X_val)

    macro_f1 = float(f1_score(y_val, y_val_pred, average="macro"))
    acc = float(accuracy_score(y_val, y_val_pred))

    dump({"model": clf, "label_encoder": le, "features": feature_cols}, MODEL_PATH)

    importances = getattr(clf, "feature_importances_", None)
    if importances is not None and len(importances) == len(feature_cols):
        importances = {f: float(w) for f, w in zip(feature_cols, importances)}
    else:
        importances = {}

    meta = {
        "version": _today_str(),
        "features": feature_cols,
        "metrics": {
            "macro_f1": macro_f1,
            "accuracy": acc,
            "n_train": int(len(X_train)),
            "n_val": int(len(X_val)),
            "majority_macro_f1": baseline["macro_f1"],
            "majority_accuracy": baseline["accuracy"],
        },
        "explanations": {"feature_importances": importances},
        "classes": CLASSES,
        "model_path": str(MODEL_PATH.relative_to(ROOT)),
    }
    META_PATH.write_text(json.dumps(meta, indent=2))

    BASELINE_PATH.write_text(json.dumps(baseline, indent=2))
    print(f"[model] wrote {META_PATH}, {BASELINE_PATH} and {MODEL_PATH}")
    return meta


# ---------- Single-day feature builder for prediction ----------
def _build_single_feature_row(city_id: str) -> Tuple[pd.DataFrame, pd.Timestamp]:
    if not HAVE_DB:
        raise RuntimeError("Database not configured; cannot build live features for prediction.")

    eng = get_engine()
    with eng.connect() as c:
        aqi = pd.read_sql(
            "SELECT city_id, date, aqi_value FROM aqi_daily WHERE city_id=%s ORDER BY date",
            c,
            params=[city_id],
            parse_dates=["date"],
        )
        wx = pd.read_sql(
            "SELECT city_id, date, features_json FROM wx_forecast WHERE city_id=%s",
            c,
            params=[city_id],
            parse_dates=["date"],
        )

    if aqi.empty:
        raise ValueError(f"No AQI history for {city_id}. Run app.etl fetch_aqi --city {city_id}.")

    aqi = aqi.sort_values("date").copy()
    t = aqi["date"].max()
    d_t1 = t + pd.Timedelta(days=1)

    #compute lags at t
    aqi["aqi_val_t"] = aqi["aqi_value"]
    aqi["aqi_val_t_1"] = aqi["aqi_value"].shift(1)
    aqi["aqi_val_t_2"] = aqi["aqi_value"].shift(2)
    lag_row = aqi.loc[aqi["date"] == t, ["aqi_val_t", "aqi_val_t_1", "aqi_val_t_2"]].iloc[0]

    #get weather features for d_t1
    if not wx.empty:
        def _to_dict(x):
            if isinstance(x, dict):
                return x
            try:
                return json.loads(x)
            except Exception:
                return {}
        wx["js"] = wx["features_json"].map(_to_dict)
        wx_row = wx.loc[wx["date"] == d_t1]
        if not wx_row.empty:
            js = wx_row["js"].iloc[0]
        else:
            js = {}
    else:
        js = {}

    row = pd.DataFrame(
        {
            "city_id": [city_id],
            "date": [t],  # base day t
            "aqi_val_t": [lag_row.get("aqi_val_t", np.nan)],
            "aqi_val_t_1": [lag_row.get("aqi_val_t_1", np.nan)],
            "aqi_val_t_2": [lag_row.get("aqi_val_t_2", np.nan)],
            "wx_mean_temp_t1": [js.get("mean_temp", np.nan)],
            "wx_mean_rh_t1": [js.get("mean_rh", np.nan)],
            "wx_mean_wind_t1": [js.get("mean_wind", np.nan)],
        }
    )

    return row, d_t1


def _predict_with_model(X_row: pd.DataFrame) -> Tuple[str, Dict[str, float]]:
    if MODEL_PATH.exists():
        bundle = load(MODEL_PATH)
        clf: RandomForestClassifier = bundle["model"]
        le: LabelEncoder = bundle["label_encoder"]
        feature_cols: List[str] = bundle["features"]

        for col in feature_cols:
            if col not in X_row.columns:
                X_row[col] = np.nan

        X = X_row[feature_cols].copy()
        for c in feature_cols:
            X[c] = pd.to_numeric(X[c], errors="coerce")
        X = X.fillna(X.median(numeric_only=True))

        proba = clf.predict_proba(X)[0]  #shape n_classes_in_model

        class_indices = getattr(clf, "classes_", None)
        prob_map = {CLASSES[i]: 0.0 for i in range(len(CLASSES))}
        if class_indices is not None:
            for cls_idx, p in zip(class_indices, proba):
                cls_name = le.inverse_transform([cls_idx])[0]
                prob_map[str(cls_name)] = float(p)
        else:
            maj = max(prob_map.items(), key=lambda kv: kv[1])[0]
            return maj, prob_map

        pred_class = max(prob_map.items(), key=lambda kv: kv[1])[0]

        s = sum(prob_map.values()) or 1.0
        prob_map = {k: float(v / s) for k, v in prob_map.items()}
        return pred_class, prob_map

    if BASELINE_PATH.exists():
        baseline = json.loads(BASELINE_PATH.read_text())
        maj = baseline.get("class", "Moderate")
    else:
        maj = "Moderate"
    prob_map = {c: 0.0 for c in CLASSES}
    prob_map[maj] = 1.0
    return maj, prob_map


# ---------- Public API ----------
def fit_and_save() -> Dict[str, object]:
    df = _load_features_df()
    return train_rf(df)


def predict_tomorrow(city_id: str = "DAL-TX") -> Dict[str, object]:
    _ensure_dirs()
    try:
        row, d_t1 = _build_single_feature_row(city_id)
    except Exception as e:
        print(f"[model] live feature build failed ({e}); falling back to last training row")
        df = _load_features_df()
        sub = df[df.get("city_id", "").astype(str) == city_id]
        row = (sub.tail(1) if not sub.empty else df.tail(1)).copy()
        d_t1 = (pd.to_datetime(row["date"].iloc[0]) + pd.Timedelta(days=1))
        
    pred_label, prob_map = _predict_with_model(row)

    out = {
        "date": pd.to_datetime(d_t1).date().isoformat(),
        "predicted_category": pred_label,
        "proba": {k: float(v) for k, v in prob_map.items()},
        "model_version": _today_str(),
        "city_id": city_id,
    }
    TOMORROW_PATH.write_text(json.dumps(out, indent=2))
    print(f"[model] wrote {TOMORROW_PATH}")
    return out


# ---------- CLI ----------
def _main():
    import argparse

    parser = argparse.ArgumentParser(description="AQI Predictor model operations")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("train", help="Train RF model from features_train")
    p_pred = sub.add_parser("predict_tomorrow", help="Predict tomorrow for a city")
    p_pred.add_argument("--city", default="DAL-TX")

    args = parser.parse_args()

    if args.cmd in (None, "train"):
        df = _load_features_df()
        train_rf(df)
    elif args.cmd == "predict_tomorrow":
        predict_tomorrow(city_id=args.city)
    else:
        parser.print_help()


if __name__ == "__main__":
    _main()
