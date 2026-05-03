@echo off
REM AI Medical Diagnostic System Setup Script for Windows

echo.
echo ========================================
echo AI Medical Diagnostic System Setup
echo ========================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.9+ from https://www.python.org/
    pause
    exit /b 1
)

echo [1/5] Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo Error: Failed to create virtual environment
    pause
    exit /b 1
)

echo [2/5] Activating virtual environment...
call venv\Scripts\activate.bat

echo [3/5] Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)

echo [4/5] Setting up environment file...
if not exist .env (
    copy .env.example .env
    echo Created .env file. Please edit it with your API keys.
) else (
    echo .env file already exists
)

echo [5/5] Creating required directories...
if not exist uploads mkdir uploads
if not exist reports mkdir reports
if not exist logs mkdir logs
if not exist cache mkdir cache
if not exist memory mkdir memory

echo.
echo ========================================
echo ✅ Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Edit .env file with your API keys
echo    - ANTHROPIC_API_KEY (from Anthropic)
echo    - SERPER_API_KEY (optional, for doctor search)
echo.
echo 2. Run the application:
echo    - Backend: python main.py
echo    - Frontend: Open index.html in browser
echo.
echo 3. The API will be available at: http://localhost:8000
echo.
echo For more information, see README.md
echo.
pause
