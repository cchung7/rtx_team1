#!/bin/bash
# Simple installation script for CLAP system

echo "=========================================="
echo "CLAP Installation Script"
echo "=========================================="
echo ""

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $PYTHON_VERSION"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip --quiet

# Install packages one by one for better reliability
echo ""
echo "Installing packages (this may take a few minutes)..."
echo ""

echo "[1/9] Installing Flask..."
pip install flask==3.0.0 --quiet

echo "[2/9] Installing Flask-CORS..."
pip install flask-cors==4.0.0 --quiet

echo "[3/9] Installing pandas..."
pip install pandas==2.2.3 --quiet

echo "[4/9] Installing numpy..."
pip install numpy==2.1.0 --quiet

echo "[5/9] Installing scipy..."
pip install scipy==1.14.1 --quiet

echo "[6/9] Installing scikit-learn..."
pip install scikit-learn==1.5.2 --quiet

echo "[7/9] Installing LightGBM..."
pip install lightgbm==4.5.0 --quiet

echo "[8/9] Installing SQLAlchemy..."
pip install sqlalchemy==2.0.35 --quiet

echo "[9/9] Installing python-dotenv..."
pip install python-dotenv==1.0.1 --quiet

echo ""
echo "=========================================="
echo "✓ Installation complete!"
echo "=========================================="
echo ""
echo "To start the application:"
echo "  1. source venv/bin/activate"
echo "  2. cd backend"
echo "  3. python app.py"
echo ""
echo "Then open: http://localhost:5000"
echo ""

