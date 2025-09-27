# Streamlit dash for AQI prediction 
# - 30 day AQI history (by city)
# - Tomorrow's prediction from data/tomorrow.json
# - Baseline vs Model metrics (macro-F1, accuracy, per-class F1)
# Run: streamlit run dashboard.py  

import json
from pathlib import Path
from datetime import timedelta

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Tomorrow's AQI — MVP", layout="wide")
st.title("Tomorrow’s AQI — MVP Dashboard")

DATA_DIR = Path("data")
MODELS_DIR = Path("models")

def load_json(path: Path, default=None):
    try:
        return json.loads(path.read_text())
    except Exception:
        return default

def as_df_top_features(meta: dict) -> pd.DataFrame:
    tf = (meta or {}).get("explanations", {}).get("top_features", [])
    # expected format: [["feature", score], ...]
    if not tf:
        return pd.DataFrame(columns=["feature", "importance"])
    return pd.DataFrame(tf, columns=["feature", "importance"]).sort_values("importance", ascending=False)

def metrics_cards(baseline: dict, model: dict):
    c1, c2, c3, c4 = st.columns(4)
    #Baseline Model
    with c1:
        st.caption("Baseline (Majority Class)")
        st.metric("Macro-F1 (baseline)", f"{baseline.get('macro_f1', 0):.3f}")
        st.metric("Accuracy (baseline)", f"{baseline.get('accuracy', 0):.3f}")
    #Prediction model
    with c2:
        st.caption("Model (Current)")
        st.metric("Macro-F1 (model)", f"{model.get('macro_f1', 0):.3f}")
        st.metric("Accuracy (model)", f"{model.get('accuracy', 0):.3f}")
    with c3:
        st.caption("Baseline Class / Version")
        st.metric("Majority Class", (baseline.get("majority_class") or "—"))
        st.metric("Model Version", (meta.get("version") or "—"))
    with c4:
        st.caption("Algorithm")
        algo = (meta.get("training") or {}).get("algorithm", "—")
        st.metric("Training Algorithm", algo)

#Time series
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("30-day AQI (per city)")
    fcsv = DATA_DIR / "features_train.csv"
    if fcsv.exists():
        df_all = pd.read_csv(fcsv, parse_dates=["date"])
        #City selector
        cities = sorted(df_all["city_id"].dropna().unique().tolist()) if "city_id" in df_all.columns else []
        city = st.selectbox("City", options=cities or ["(no city_id column)"], index=0)
        if cities:
            df = df_all[df_all["city_id"] == city].copy()
        else:
            df = df_all.copy()
        if not df.empty and "date" in df.columns:
            df = df.sort_values("date")
            last30 = df.tail(30)
            chart_df = last30.set_index("date")[["aqi_val_t"]].rename(columns={"aqi_val_t": "AQI (t)"})
            st.line_chart(chart_df)
            st.caption(f"Showing last {len(chart_df)} rows for {city if cities else 'dataset'}")
        else:
            st.info("No rows available to plot yet.")
    else:
        st.info("`data/features_train.csv` not found — run feature builder.")

#Prediction
with col2:
    st.subheader("Tomorrow")
    fjson = DATA_DIR / "tomorrow.json"
    if fjson.exists():
        pred = load_json(fjson, {})
        st.metric("Predicted Category", pred.get("predicted_category", "—"))
        proba = pred.get("proba") or {}
        if isinstance(proba, dict) and proba:
            p_df = pd.DataFrame([proba]).T.reset_index()
            p_df.columns = ["Category", "Probability"]
            p_df = p_df.sort_values("Probability", ascending=False)
            st.table(p_df)
        st.caption(f"Date: {pred.get('date','—')} • Model: {pred.get('model_version','—')}")
        with st.expander("Raw prediction JSON"):
            st.json(pred)
    else:
        st.info("`data/tomorrow.json` not found — run prediction step.")

#Metrics
st.subheader("Model vs Baseline")

meta = load_json(MODELS_DIR / "model_meta.json", {})
baseline_json = load_json(MODELS_DIR / "majority_baseline.json", meta.get("baseline") or {})

if meta:
    metrics_cards(
        baseline=baseline_json or {"macro_f1": 0, "accuracy": 0, "majority_class": "—"},
        model=(meta.get("metrics") or {"macro_f1": 0, "accuracy": 0})
    )

    # F1 per class F1 
    per_class = (meta.get("metrics") or {}).get("per_class_f1")
    if isinstance(per_class, dict) and per_class:
        st.markdown("**Per-class F1**")
        pc_df = pd.DataFrame(
            [{"Category": k, "F1": float(v)} for k, v in per_class.items()]
        ).sort_values("F1", ascending=False)
        st.bar_chart(pc_df.set_index("Category"))

    tf_df = as_df_top_features(meta)
    st.markdown("**Top Features (Permutation Importance)**")
    if not tf_df.empty:
        st.bar_chart(tf_df.set_index("feature"))
    else:
        st.caption("No feature importances available yet (train the RF first).")

    with st.expander("Raw model_meta.json"):
        st.json(meta)
else:
    st.info("`models/model_meta.json` not found — run training once to populate it.")
