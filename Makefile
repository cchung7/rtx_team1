PY      ?= python -m      
PYEXE   ?= python         
COMPOSE ?= docker compose
ENVFILE ?= .env

.PHONY: setup build_features train predict run_ui refresh sanity test clean distclean \
        db_up db_down db_logs db_init print_db env_example export_features


#Setup
setup:
	$(PY) pip install -r requirements.txt
	mkdir -p data models sql app/ui
	@echo ">> Setup complete. Create .env from .env.example if needed."


#SQLite/MySQL
env_example:
	@test -f .env || cp .env.example .env; true

print_db:
	@echo "DB_URL=$${DB_URL:-sqlite:///data/aqi.sqlite}"

db_up: env_example
	$(COMPOSE) --env-file $(ENVFILE) up -d mysql
	@echo ">> MySQL container starting..."

db_logs:
	$(COMPOSE) logs -f mysql

db_down:
	$(COMPOSE) down

db_init:
	$(PY) app.db init   # auto-detects engine from DB_URL and applies schema


#Temp pipeline
build_features:
	@echo "build_features stub (will use DB via app.db)"

train:
	@echo "train stub (LogReg baseline later)"

predict:
	@echo "predict stub -> writes data/tomorrow.json" && \
	echo '{"date":"YYYY-MM-DD","predicted_category":"Moderate","proba":{"Good":0.25,"Moderate":0.50,"USG":0.15,"Unhealthy+":0.10},"model_version":"YYYY-MM-DD"}' > data/tomorrow.json

run_ui:
	$(PY) streamlit run app/ui/dashboard.py

refresh: build_features predict export_features
	@echo ">> Refresh complete"


#Util
export_features:
	$(PY) scripts.export_features
	import sqlite3, pandas as pd, os
	os.makedirs("data", exist_ok=True)
	con = sqlite3.connect("data/aqi.sqlite")
	df = pd.read_sql("SELECT * FROM features_train ORDER BY date", con)
	df.to_csv("data/features_train.csv", index=False)
	print("exported", len(df), "rows to data/features_train.csv")
	PY


sanity:
	$(PY) scripts.sanity_check_prediction

test:
	pytest -q || true

clean:
	rm -f data/features_train.csv data/tomorrow.json

distclean: clean
	rm -f data/aqi.sqlite
	rm -rf models/*
