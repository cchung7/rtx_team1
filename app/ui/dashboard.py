#Temp dash for testing of pipeline 
# Streamlit UI for the AQI prediction system
# - Shows the last 30 days of actual AQI history and displays tomorrow’s predicted AQI category from tomorrow.json
# - Explains the model via coefficients/feature importances from model_meta.json
# Notes:
# - Reads data/tomorrow.json and models/model_meta.json
# - Run: make run_ui


import json, pandas as pd, streamlit as st
from pathlib import Path

st.set_page_config(page_title="Tomorrow's AQI — MVP", layout="wide")

st.title("Tomorrow’s AQI — MVP Dashboard")

col1, col2 = st.columns([2,1])
with col1:
    st.subheader("30-day AQI (sample)")
    fcsv = Path("data/features_train.csv")
    if fcsv.exists():
        df = pd.read_csv(fcsv, parse_dates=["date"])
        st.line_chart(df.sort_values("date")[["date","aqi_val_t"]].set_index("date"))
    else:
        st.info("features_train.csv not found yet — run build_features.")
with col2:
    st.subheader("Tomorrow")
    fjson = Path("data/tomorrow.json")
    if fjson.exists():
        pred = json.loads(fjson.read_text())
        st.metric("Predicted Category", pred.get("predicted_category","—"))
        st.json(pred)
    else:
        st.info("tomorrow.json not found — run make predict.")

st.subheader("Why (top features)")
mmeta = Path("models/model_meta.json")
if mmeta.exists():
    st.json(json.loads(mmeta.read_text()))
else:
    st.info("model_meta.json not found — train not run yet.")
