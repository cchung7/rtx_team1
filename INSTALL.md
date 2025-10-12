# CLAP Installation Guide

## Prerequisites

- **Python 3.13+** (recommended: Python 3.13.7)
- **Git** (for cloning the repository)
- **8GB+ RAM** (for model training and data processing)

## Installation Methods

### Method 1: Automated Setup (Recommended)

**Mac/Linux:**
```bash
git clone <repository-url>
cd clap-project
chmod +x run.sh
./run.sh
```

**Windows:**
```bash
git clone <repository-url>
cd clap-project
run.bat
```

### Method 2: Manual Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd clap-project
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Mac/Linux
   source venv/bin/activate
   
   # Windows
   venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Train the models** (if not already trained)
   ```bash
   python train_prototype_model.py
   python train_balanced_model.py
   ```

5. **Start the server**
   ```bash
   cd backend
   python app.py
   ```

6. **Access the application**
   - Open browser to `http://localhost:5001`

## Troubleshooting

### Port 5001 Already in Use
If you get "Address already in use" error:
```bash
# Find and kill the process
lsof -ti:5001 | xargs kill -9

# Or use a different port by editing backend/app.py
app.run(host='0.0.0.0', port=5002, debug=True)
```

### Python Version Issues
Make sure you're using Python 3.13+:
```bash
python --version
# Should show Python 3.13.x
```

### Missing Models
If models are missing, train them:
```bash
python train_prototype_model.py
python train_balanced_model.py
```

### Permission Issues (Mac/Linux)
```bash
chmod +x run.sh
chmod +x install_simple.sh
```

## Verification

After installation, verify everything works:

1. **Check server is running**
   ```bash
   curl http://localhost:5001/api/health
   ```

2. **Test prediction API**
   ```bash
   curl -X POST http://localhost:5001/api/aqi/predict \
     -H "Content-Type: application/json" \
     -d '{"county": "Dallas", "state": "Texas", "model": "balanced", "days": 1}'
   ```

3. **Open web interface**
   - Go to `http://localhost:5001`
   - Select a county and generate a forecast

## System Requirements

- **OS**: Windows 10+, macOS 10.15+, or Linux
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 2GB free space
- **Network**: Internet connection for initial setup

## Support

If you encounter issues:
1. Check this troubleshooting guide
2. Verify all prerequisites are installed
3. Check the console output for error messages
4. Contact the development team