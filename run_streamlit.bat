@echo off
REM AI Medical Diagnostic System - Streamlit Setup & Run Script
REM This script sets up dependencies and runs the Streamlit application

echo.
echo ========================================
echo AI Medical Diagnostic System
echo Streamlit Application Setup
echo ========================================
echo.

REM Activate virtual environment
echo [1/4] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo Error: Could not activate virtual environment
    pause
    exit /b 1
)
echo ✓ Virtual environment activated

echo.
echo [2/4] Installing dependencies...
pip install -r requirements.txt -q
if errorlevel 1 (
    echo Error: Could not install dependencies
    pause
    exit /b 1
)
echo ✓ Dependencies installed

echo.
echo [3/4] Checking configuration...
if not exist ".env" (
    echo ⚠ Warning: .env file not found
    echo Please create .env file with your API keys before running
    echo.
)
echo ✓ Configuration checked

echo.
echo [4/4] Starting Streamlit application...
echo.
echo ========================================
echo Opening http://localhost:8501
echo ========================================
echo.

streamlit run streamlit_app.py --logger.level=info

pause
