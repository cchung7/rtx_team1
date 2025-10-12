#!/bin/bash
# CLAP System Startup Script

echo "=========================================="
echo "CLAP - Air Quality Prediction System"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✓ Python 3 found"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo ""
echo "✓ Dependencies installed"
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "No .env file found. Creating from .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "Please edit .env file with your database credentials."
    fi
fi

echo "=========================================="
echo "Starting CLAP System..."
echo "=========================================="
echo ""
echo "📊 Dashboard will be available at:"
echo "   http://localhost:5001"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start Flask app
cd backend
python3 app.py

