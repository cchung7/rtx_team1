@echo off
REM CLAP System Startup Script for Windows

echo ==========================================
echo CLAP - Air Quality Prediction System
echo ==========================================
echo.

REM Anchor to script’s folder
cd /d "%~dp0"
set "ROOT=%CD%"
set "VENV=%ROOT%\venv"
set "FRONTEND=%ROOT%\frontend"
set "BACKEND=%ROOT%\backend"

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo X Python is not installed. Please install Python 3.8 or higher.
    exit /b 1
)

echo OK Python found
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    echo.
    py -3.12 -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo.
echo Installing dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo.
echo OK Dependencies installed
echo.

REM Check if .env exists
if not exist ".env" (
    echo Warning: No .env file found. Creating from .env.example...
    if exist ".env.example" (
        copy .env.example .env
        echo Please edit .env file with your database credentials.
    )
)

REM Build React/Vite frontend
cd frontend
call npm install
call npm run build
cd ..

echo ==========================================
echo Starting CLAP System...
echo ==========================================
echo.
echo Dashboard will be available at:
echo    http://localhost:5001
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start Flask app
cd backend
python app.py
