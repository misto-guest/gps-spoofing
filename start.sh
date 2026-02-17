#!/bin/bash
# GPS Spoofing Campaign Manager - Quick Start Script for Linux/Mac

echo "========================================"
echo "GPS Spoofing Campaign Manager"
echo "========================================"
echo

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Virtual environment not found!"
    echo "Please run: python setup_venv.py"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo ".env file not found!"
    echo "Please run: python setup_venv.py"
    exit 1
fi

echo "Starting GPS Campaign Manager..."
echo
echo "Dashboard will be available at: http://localhost:5002"
echo "Press Ctrl+C to stop the server"
echo

# Start the application
cd gps_campaign_manager
python run.py >> log.txt 2>&1
