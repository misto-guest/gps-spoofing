@echo off
REM GPS Spoofing Campaign Manager - Quick Start Script for Windows

echo ========================================
echo GPS Spoofing Campaign Manager
echo ========================================
echo.

REM Check if virtual environment exists
if not exist ".venv\Scripts\activate.bat" (
    echo Virtual environment not found!
    echo Please run: python setup_venv.py
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Check if .env file exists
if not exist ".env" (
    echo .env file not found!
    echo Please run: python setup_venv.py
    pause
    exit /b 1
)

echo Starting GPS Campaign Manager...
echo.
echo Dashboard will be available at: http://localhost:5002
echo Press Ctrl+C to stop the server
echo.

REM Start the application
cd gps_campaign_manager
python run.py
