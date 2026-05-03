#!/bin/bash

# AI Medical Diagnostic System - Streamlit Setup & Run Script
# This script sets up dependencies and runs the Streamlit application

echo ""
echo "========================================"
echo "AI Medical Diagnostic System"
echo "Streamlit Application Setup"
echo "========================================"
echo ""

# Activate virtual environment
echo "[1/4] Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "Error: Could not activate virtual environment"
    exit 1
fi
echo "✓ Virtual environment activated"

echo ""
echo "[2/4] Installing dependencies..."
pip install -r requirements.txt -q
if [ $? -ne 0 ]; then
    echo "Error: Could not install dependencies"
    exit 1
fi
echo "✓ Dependencies installed"

echo ""
echo "[3/4] Checking configuration..."
if [ ! -f ".env" ]; then
    echo "⚠ Warning: .env file not found"
    echo "Please create .env file with your API keys before running"
    echo ""
fi
echo "✓ Configuration checked"

echo ""
echo "[4/4] Starting Streamlit application..."
echo ""
echo "========================================"
echo "Opening http://localhost:8501"
echo "========================================"
echo ""

streamlit run streamlit_app.py --logger.level=info
