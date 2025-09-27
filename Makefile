#Local set up
PY ?= python -m

.PHONY: setup refresh run_ui clean

#Install dependencies
setup:
	$(PY) pip install -r requirements.txt || true
	mkdir -p data models

#Pipeline: init DB, build features, train, predict
refresh:
	$(PY) app.db init
	$(PY) app.features
	$(PY) app.model train
	$(PY) app.model predict

#Dashboard
run_ui:
	streamlit run app/ui/dashboard.py

#Clean
clean:
	rm -f data/*.sqlite data/*.csv data/*.json
	rm -rf models/*
