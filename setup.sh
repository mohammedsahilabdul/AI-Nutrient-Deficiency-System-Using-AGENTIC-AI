#!/bin/bash

# AI Medical Diagnostic System Setup Script for Mac/Linux

echo ""
echo "========================================"
echo "AI Medical Diagnostic System Setup"
echo "========================================"
echo ""

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    echo "Please install Python 3.9+ from https://www.python.org/"
    exit 1
fi

python3 --version

echo "[1/5] Creating virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "Error: Failed to create virtual environment"
    exit 1
fi

echo "[2/5] Activating virtual environment..."
source venv/bin/activate

echo "[3/5] Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies"
    exit 1
fi

echo "[4/5] Setting up environment file..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env file. Please edit it with your API keys."
else
    echo ".env file already exists"
fi

echo "[5/5] Creating required directories..."
mkdir -p uploads reports logs cache memory

echo ""
echo "========================================"
echo "✅ Setup Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys"
echo "   - ANTHROPIC_API_KEY (from Anthropic)"
echo "   - SERPER_API_KEY (optional, for doctor search)"
echo ""
echo "2. Run the application:"
echo "   - Backend: python main.py"
echo "   - Frontend: Open index.html in browser"
echo ""
echo "3. The API will be available at: http://localhost:8000"
echo ""
echo "For more information, see README.md"
echo ""
