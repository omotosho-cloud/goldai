#!/bin/bash

echo "========================================"
echo "   GOLD AI SIGNAL GENERATOR APP"
echo "========================================"
echo

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "ERROR: Python is not installed or not in PATH"
    echo "Please install Python 3.8+ and try again"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/Scripts/activate

# Install/upgrade requirements
echo "Installing requirements..."
pip install -r requirements.txt --quiet

# Check if model exists
if [ ! -f "gold_v1.joblib" ]; then
    echo
    echo "No trained model found. Training initial model..."
    echo "This may take a few minutes..."
    python -c "from model_trainer import ModelTrainer; trainer = ModelTrainer(); trainer.train_model()"
fi

echo
echo "========================================"
echo "Starting Gold AI Web Application..."
echo "Dashboard will be available at:"
echo "http://localhost:5000"
echo "========================================"
echo
echo "Press Ctrl+C to stop the application"
echo

# Start the Flask application
python app.py

echo
echo "Application stopped."