#!/bin/bash
# CLAP System Startup Script

echo "=========================================="
echo "CLAP - Air Quality Prediction System"
echo "=========================================="
echo ""

# Anchor to script directory
SCRIPT_DIR="$(cd -- "$(dirname "$0")" >/dev/null 2>&1 && pwd)"
cd "$SCRIPT_DIR" || exit 1
ROOT="$SCRIPT_DIR"
BACKEND="$ROOT/backend"
FRONTEND=""
if [ -d "$ROOT/frontend" ]; then
  FRONTEND="$ROOT/frontend"
elif [ -d "$ROOT/dashboard" ]; then
  FRONTEND="$ROOT/dashboard"
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3.12 or 3.13."
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
source venv/bin/activate # shellcheck disable=SC1091

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

# Build React/Vite frontend
if [ -n "$FRONTEND" ]; then
  if command -v node >/dev/null 2>&1 && command -v npm >/dev/null 2>&1; then
    echo "Checking Node.js..."
    node --version
    npm --version
    
    cd "$FRONTEND"
    echo "Installing frontend dependencies..."
    npm install
    echo "Starting React (Vite) dev server..."
    npm run dev &         
    cd "$ROOT"
  else
    echo "ERROR: Node.js/npm not found."
  fi
else
  echo "ERROR: No frontend/ or dashboard/ folder found."
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
cd "$BACKEND"
python3 app.py
