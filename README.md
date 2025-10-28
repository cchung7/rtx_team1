# CLAP_V1.1 - County-level Air Quality Prediction System

A machine learning-powered web application that predicts Air Quality Index (AQI) for counties across the United States with multi-day forecasting capabilities.

## Features

- **Multi-Day Forecasting**: Predict AQI for 1, 3, 7, or 14 days ahead
- **Two ML Models**: 
  - **Balanced Model** (R² = 0.72) - Recommended for best performance
  - **Prototype Model** (R² = 0.46) - Original baseline model
- **Interactive Dashboard**: Beautiful web interface with EPA-compliant color coding
- **County Coverage**: 773 counties across the United States
- **Real-time Predictions**: RESTful API with instant results

## Model Performance

| Model | R² Score | MSE | Use Case |
|-------|----------|-----|----------|
| Balanced | 0.72 | 93.47 | **Recommended** - Best overall performance |
| Prototype | 0.46 | 177.72 | Baseline comparison |

## Quick Start

### Prerequisites
- Python 3.13+
- Node.js v22.21.0+

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd clap-project
   ```

2. **Run the setup script**
   ```bash
   # Mac/Linux
   ./run.sh
   
   # Windows
   run.bat
   ```

3. **Access the application**
   - Open your browser to `http://localhost:5001`
   - Select a county and model
   - Generate forecasts!

## Project Structure

```
clap-project/
├── backend/           # Flask API server
├── frontend/          # Web dashboard
├── data/             # AQI datasets
├── models/           # Trained ML models
└── requirements.txt  # Python dependencies
```

## API Endpoints

- `GET /api/health` - Health check
- `GET /api/counties` - List available counties
- `GET /api/categories` - List AQI categories
- `GET /api/aqi/historical` - Historical AQI data
- `POST /api/aqi/predict` - Generate predictions
- `GET /api/model/metrics` - Model performance metrics

## Usage Examples

### Single-Day Prediction
```bash
curl -X POST http://localhost:5001/api/aqi/predict \
  -H "Content-Type: application/json" \
  -d '{"county": "Dallas", "state": "Texas", "model": "balanced", "days": 1}'
```

### Multi-Day Forecast (Optional)
```bash
curl -X POST http://localhost:5001/api/aqi/predict \
  -H "Content-Type: application/json" \
  -d '{"county": "Dallas", "state": "Texas", "model": "balanced", "days": 7}'
```

## Team Members

- **David Santos** - Project Lead
- **Amelia Quinn** - Testing & QA
- **Kevin Melo** - Performance Optimization
- **AJ Kimbrough** - Deployment & Infrastructure
- **Andrew Enright** - UI/UX Development
- **Jay Chung** - Model Research & Enhancement

## License

This project is part of SE 4485.001 coursework at the University of Texas at Dallas.

## Technical Details

- **Framework**: Flask (Python)
- **ML Library**: LightGBM
- **Frontend**: React, HTML5, CSS3, JavaScript, Chart.js
- **Data Source**: EPA AQI datasets (2024)
- **Deployment**: Local development server (port 5001)

---

For detailed installation instructions, see [INSTALL.md](INSTALL.md)

---

For requirements information, see [REQUIREMENTS.md](REQUIREMENTS.md)
