---

### FUNCTIONAL REQUIREMENTS:
1.	Data Ingestion:
- FR-1.1: The system shall utilize daily AQI data from the Environmental Protection Agency (EPA), ingested manually from provided datasets.

2.	Data Processing:
- FR-2.1: The system shall store historical AQI data in a CSV.
- FR-2.2: The system shall generate lag features for use in prediction.

3.	Predictive Analytics: 
- FR-3.1: The system shall train and run a predictive model using historical AQI and county location data.
- FR-3.2: The system shall output a next-day AQI category for a selected county.
- FR-3.3: The system shall provide the prediction with an associated probability score for each AQI category.

4.	Dashboard: 
- FR-4.1: The system shall provide an graphical user interface (GUI) for visualizing AQI data and predictions.
- FR-4.2: The system shall display a chart or graph of the most recent 30 days of AQI for the selected county and the next-day predicted category with probabilities.
- FR-4.3: The system shall provide a Refresh control that updates the dashboard from locally stored dataset and regenerates the forecast for the selected county.

---

### NON-FUNCTIONAL REQUIREMENTS:
1.	Performance: 
- NFR-1.1: The system shall complete ingestion, validation, and feature generation for one county in ≤ 60 seconds.
- NFR-1.2: The system shall render the dashboard in ≤ 5 seconds (p95) after end user clicks Refresh.

2.	Usability: 
- NFR-2.1: The dashboard shall present AQI categories using standard EPA labels (e.g. Good, Moderate, Unhealthy for Sensitive Groups, Unhealthy, Very Unhealthy, Hazardous).
- NFR-2.2: The dashboard shall present each EPA category with a unique, distinguishable color code consistent with EPA/AirNow guidance (e.g. green, yellow, orange, red, purple, maroon).

3.	Accessibility:
- NFR-3.1: The system shall conform to WCAG 2.1 Level AA accessibility requirements for visual content (e.g. SC 1.4.1 “Use of Color”, SC 1.4.3 “Contract (Minimum)”, SC 1.4.11 “Non-text Contrast”).

4.	Reliability: 
- NFR-4.1: Daily ingest shall succeed on ≥ 90% of runs.

5.	Availability: 
- NFR-5.1: The CLAP dashboard shall be available for use by end users at least 99% of the time over any rolling 30-day period once deployed.

6.	Maintainability:
- NFR-6.1: The system shall implement structured logging for key operations (ingestion, validation, feature generation, and prediction).
- NFR-6.2: Log entries shall include timestamps and error details.
