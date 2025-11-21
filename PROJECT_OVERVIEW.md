# CLAP V1.2+ - Complete Project Overview

## 📋 Project Summary

**CLAP (County-level Air Quality Prediction System)** is a machine learning-powered web application that predicts Air Quality Index (AQI) for counties across the United States. It provides multi-day forecasting capabilities (1, 3, 7, or 14 days ahead) using trained LightGBM models.

**Repository**: https://github.com/cchung7/rtx_team1  
**Course**: SE 4485.001 at University of Texas at Dallas

---

## 🏗️ Architecture

### System Components

1. **Backend (Flask REST API)**
   - Python Flask server running on port 5001
   - Serves both API endpoints and static frontend files
   - Modular route structure using Flask Blueprints
   - Structured JSON logging

2. **Frontend (React + Vite)**
   - React 19.1.1 with modern hooks
   - Vite for fast development and building
   - TailwindCSS for styling
   - Chart.js for data visualization
   - Built as static files served by Flask

3. **Machine Learning Models**
   - LightGBM gradient boosting models
   - Two model variants: Balanced (R²=0.72) and Prototype (R²=0.46)
   - Trained on EPA AQI datasets from 2024

4. **Data Source**
   - CSV-based data storage (no database required)
   - EPA daily AQI data by county
   - 773 counties across the United States

---

## 🛠️ Technology Stack

### Backend
- **Python 3.13+** (compatible with 3.11, 3.12, 3.13)
- **Flask 3.0.0** - Web framework
- **Flask-CORS 4.0.0** - Cross-origin resource sharing
- **LightGBM 4.5.0** - Machine learning library
- **scikit-learn 1.5.2** - ML utilities
- **pandas 2.2.3** - Data manipulation
- **numpy 2.1.0** - Numerical computing
- **SQLAlchemy 2.0.35** - Database ORM (configured but using CSV)

### Frontend
- **React 19.1.1** - UI framework
- **Vite 7.1.7** - Build tool and dev server
- **Chart.js 4.5.1** - Data visualization
- **react-chartjs-2 5.3.0** - React wrapper for Chart.js
- **TailwindCSS 3.4.18** - Utility-first CSS framework

### Data & Models
- **EPA AQI Datasets** - 2024 daily AQI by county
- **LightGBM Models** - Pre-trained prediction models
- **CSV Storage** - Historical data in CSV format

---

## 📁 Project Structure

```
RayethonProject1.3/
├── backend/                    # Flask API server
│   ├── app.py                  # Main Flask application
│   ├── config.py               # Configuration settings
│   ├── ml_model.py             # ML model wrapper (AQIPredictor)
│   ├── data_source.py          # CSV data source handler
│   ├── routes/                 # API route blueprints
│   │   ├── health.py           # Health check endpoint
│   │   ├── counties.py         # County listing
│   │   ├── categories.py       # AQI categories
│   │   ├── historical.py       # Historical AQI data
│   │   ├── predict.py          # Prediction endpoint
│   │   ├── model_metrics.py    # Model performance metrics
│   │   ├── refresh.py          # Data refresh endpoint
│   │   └── index.py            # Root route
│   └── logs/                   # Application logs
│
├── frontend/                    # React web application
│   ├── src/
│   │   ├── App.jsx             # Main React component
│   │   ├── components/         # React components
│   │   │   ├── AqiChart.jsx    # Historical AQI chart
│   │   │   ├── MultiDayChart.jsx # Multi-day forecast chart
│   │   │   ├── PredictionCard.jsx # Prediction display
│   │   │   ├── ProbabilitiesList.jsx # Category probabilities
│   │   │   ├── Select.jsx      # Dropdown components
│   │   │   ├── Spinner.jsx     # Loading indicator
│   │   │   ├── ErrorAlert.jsx  # Error messages
│   │   │   ├── AqiLegend.jsx   # EPA color legend
│   │   │   └── StatsStrip.jsx  # Statistics display
│   │   ├── lib/
│   │   │   └── api.js          # API client functions
│   │   └── utils/
│   │       └── aqi.js          # AQI utility functions
│   ├── package.json            # Node.js dependencies
│   ├── vite.config.js          # Vite configuration
│   └── dist/                   # Built static files (generated)
│
├── data/                        # Data files
│   ├── daily_aqi_by_county_2024.csv  # Main AQI dataset
│   ├── encoded_dataset.csv      # Processed dataset
│   └── AQI_Time_series.py      # Data processing utilities
│
├── models/                      # Trained ML models
│   ├── balanced_lightgbm_model.pkl    # Balanced model (R²=0.72)
│   ├── balanced_pipeline.pkl          # Balanced preprocessing pipeline
│   ├── prototype_lightgbm_model.pkl  # Prototype model (R²=0.46)
│   └── prototype_pipeline.pkl        # Prototype preprocessing pipeline
│
├── train_balanced_model.py      # Script to train balanced model
├── train_prototype_model.py     # Script to train prototype model
│
├── run.sh                       # Mac/Linux startup script (EXECUTABLE)
├── run.bat                      # Windows startup script
├── install_simple.sh            # Simple installation script
├── requirements.txt             # Python dependencies
├── README.md                    # Project documentation
├── INSTALL.md                   # Installation guide
└── REQUIREMENTS.md              # Functional requirements
```

---

## 🚀 Running the Application

### Prerequisites
- **Python 3.13+** (3.11, 3.12, or 3.13)
- **Node.js v22.21.0+** (for frontend)
- **npm** (comes with Node.js)
- **8GB+ RAM** recommended

### Quick Start (Mac/Linux)

1. **Make script executable** (if not already):
   ```bash
   chmod +x run.sh
   ```

2. **Run the startup script**:
   ```bash
   ./run.sh
   ```

   This script will:
   - Check for Python 3
   - Create/activate virtual environment
   - Install Python dependencies
   - Install Node.js dependencies
   - Build the React frontend
   - Start the Flask server on port 5001

3. **Access the application**:
   - Open browser to: `http://localhost:5001`
   - Select a county and model
   - Generate forecasts!

### Manual Setup

If you prefer manual setup:

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
# venv\Scripts\activate   # Windows

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Install frontend dependencies
cd frontend
npm install
npm run build  # Build for production
cd ..

# 4. Start the server
cd backend
python app.py
```

---

## 🎯 Key Features

### 1. Multi-Day Forecasting
- Predict AQI for **1, 3, 7, or 14 days** ahead
- Uses historical patterns and lag features

### 2. Two ML Models
- **Balanced Model** (R² = 0.72, MSE = 93.47)
  - Recommended for best performance
  - Better accuracy and generalization
- **Prototype Model** (R² = 0.46, MSE = 177.72)
  - Baseline comparison model
  - Original implementation

### 3. Interactive Dashboard
- Beautiful web interface with EPA-compliant color coding
- Real-time predictions
- Historical data visualization
- Multi-day forecast charts
- Category probability distributions

### 4. County Coverage
- **773 counties** across the United States
- Searchable by state and county name
- Historical data for each county

### 5. EPA Compliance
- Standard EPA AQI categories:
  - Good (0-50) - Green
  - Moderate (51-100) - Yellow
  - Unhealthy for Sensitive Groups (101-150) - Orange
  - Unhealthy (151-200) - Red
  - Very Unhealthy (201-300) - Purple
  - Hazardous (301-500) - Maroon
- WCAG 2.1 Level AA accessibility compliance

---

## 🔌 API Endpoints

### Health & Status
- `GET /api/health` - Health check endpoint
  - Returns: `{"status": "healthy", "timestamp": "..."}`

### Data Endpoints
- `GET /api/counties` - List all available counties
  - Returns: Array of county objects with state and county name
- `GET /api/categories` - List AQI categories
  - Returns: EPA AQI categories with ranges and colors
- `GET /api/aqi/historical?county={county}&state={state}` - Historical AQI data
  - Returns: Last 30 days of AQI data for selected county

### Prediction Endpoints
- `POST /api/aqi/predict` - Generate AQI predictions
  - Request body:
    ```json
    {
      "county": "Dallas",
      "state": "Texas",
      "model": "balanced",  // or "prototype"
      "days": 1  // 1, 3, 7, or 14
    }
    ```
  - Returns: Prediction with AQI value, category, and probabilities

### Model Information
- `GET /api/model/metrics` - Model performance metrics
  - Returns: R² scores, MSE, and other metrics for both models

---

## 📊 Model Details

### Balanced Model
- **Algorithm**: LightGBM Gradient Boosting
- **Performance**: R² = 0.72, MSE = 93.47
- **Features**: 
  - Historical AQI values (lag features)
  - County location data
  - Temporal features (day of year, etc.)
- **Use Case**: Production predictions

### Prototype Model
- **Algorithm**: LightGBM Gradient Boosting
- **Performance**: R² = 0.46, MSE = 177.72
- **Features**: Similar to balanced model
- **Use Case**: Baseline comparison

### Training Scripts
- `train_balanced_model.py` - Trains the balanced model
- `train_prototype_model.py` - Trains the prototype model

To retrain models:
```bash
python train_prototype_model.py
python train_balanced_model.py
```

---

## 👥 Team Members

- **David Santos** - Project Lead
- **Amelia Quinn** - Testing & QA
- **Kevin Melo** - Performance Optimization
- **AJ Kimbrough** - Deployment & Infrastructure
- **Andrew Enright** - UI/UX Development
- **Jay Chung** - Model Research & Enhancement

---

## 📝 Functional Requirements

### Data Ingestion
- FR-1.1: Utilizes daily AQI data from EPA

### Data Processing
- FR-2.1: Stores historical AQI data in CSV
- FR-2.2: Generates lag features for prediction

### Predictive Analytics
- FR-3.1: Trains and runs predictive model using historical AQI and county location data
- FR-3.2: Outputs next-day AQI category for selected county
- FR-3.3: Provides prediction with associated probability score for each AQI category

### Dashboard
- FR-4.1: Provides graphical user interface (GUI) for visualizing AQI data and predictions
- FR-4.2: Displays chart of most recent 30 days of AQI and next-day predicted category with probabilities
- FR-4.3: Provides Refresh control that updates dashboard from locally stored dataset

---

## 🔧 Configuration

### Environment Variables (Optional)
The system can use a `.env` file for configuration:
- `SECRET_KEY` - Flask secret key
- `FLASK_ENV` - Environment (development/production)
- `FLASK_DEBUG` - Debug mode (True/False)
- `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` - Database config (not currently used, CSV-based)

### Default Configuration
- **Port**: 5001
- **Host**: 0.0.0.0 (all interfaces)
- **Debug Mode**: True (development)
- **Data Source**: CSV files in `data/` directory
- **Model Path**: `models/` directory

---

## 🐛 Troubleshooting

### Port 5001 Already in Use
```bash
# Find and kill the process
lsof -ti:5001 | xargs kill -9

# Or change port in backend/app.py
app.run(host='0.0.0.0', port=5002, debug=True)
```

### Missing Models
If models are missing, train them:
```bash
python train_prototype_model.py
python train_balanced_model.py
```

### Frontend Not Building
```bash
cd frontend
rm -rf node_modules dist
npm install
npm run build
```

### Python Version Issues
Ensure Python 3.11+ is installed:
```bash
python3 --version
# Should show Python 3.11.x, 3.12.x, or 3.13.x
```

### Permission Issues (Mac/Linux)
```bash
chmod +x run.sh
chmod +x install_simple.sh
```

---

## 📈 Performance Metrics

### Model Performance
| Model | R² Score | MSE | Use Case |
|-------|----------|-----|----------|
| Balanced | 0.72 | 93.47 | **Recommended** - Best overall performance |
| Prototype | 0.46 | 177.72 | Baseline comparison |

### System Requirements
- **Ingestion Time**: ≤ 60 seconds per county (NFR-1.1)
- **Dashboard Render**: ≤ 5 seconds (p95) (NFR-1.2)
- **Reliability**: ≥ 90% success rate (NFR-4.1)
- **Availability**: ≥ 99% uptime over 30 days (NFR-5.1)

---

## 📚 Additional Documentation

- **README.md** - Project overview and quick start
- **INSTALL.md** - Detailed installation instructions
- **REQUIREMENTS.md** - Complete functional and non-functional requirements
- **SE 4485.001 - Documents/** - Course documentation (Architecture, Design, Test Plan, etc.)

---

## 🔐 Security & Best Practices

- Structured JSON logging with timestamps
- Error handling and validation
- CORS enabled for API access
- Environment-based configuration
- Virtual environment isolation
- Static file serving for frontend

---

## 🎓 License

This project is part of SE 4485.001 coursework at the University of Texas at Dallas.

---

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review INSTALL.md for detailed setup
3. Check console logs in `backend/logs/app.log`
4. Contact the development team

---

**Last Updated**: Based on repository state as of latest commit  
**Version**: CLAP V1.2+

