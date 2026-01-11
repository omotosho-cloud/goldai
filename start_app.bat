@echo off
title Gold AI Signal Generator App
color 0A

echo ========================================
echo    GOLD AI SIGNAL GENERATOR APP
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/upgrade requirements using python -m pip
echo Installing requirements...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt --quiet

REM Check if model exists
if not exist "gold_v1.joblib" (
    echo.
    echo No trained model found. Training initial model...
    echo This may take a few minutes...
    python -c "from model_trainer import ModelTrainer; trainer = ModelTrainer(); trainer.train_model()"
)

echo.
echo ========================================
echo Starting Gold AI Web Application...
echo Dashboard will be available at:
echo http://localhost:5000
echo ========================================
echo.
echo Press Ctrl+C to stop the application
echo.

REM Start the Flask application
python app.py

echo.
echo Application stopped.
pause