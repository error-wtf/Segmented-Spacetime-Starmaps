#!/bin/bash
# SSZ StarMaps - Automated Setup and Run Script
# © 2025 Carmen Wrede, Lino Casu
#
# This script automatically:
# 1. Creates virtual environment
# 2. Installs dependencies
# 3. Runs the demo
#
# Usage: ./setup_and_run.sh

echo "================================================================================"
echo "SSZ StarMaps - Automated Setup"
echo "================================================================================"
echo ""

# Check if Python is available
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "[1/6] Python found: $PYTHON_VERSION"
else
    echo "[ERROR] Python 3 not found! Please install Python 3.8+"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "[2/6] Creating virtual environment..."
    python3 -m venv .venv
    echo "      Virtual environment created."
else
    echo "[2/6] Virtual environment already exists."
fi

# Activate virtual environment
echo "[3/6] Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "[4/6] Upgrading pip..."
python -m pip install --upgrade pip --quiet

# Install dependencies
echo "[5/6] Installing dependencies..."
pip install -r requirements.txt --quiet
echo "      Dependencies installed: numpy, matplotlib, astropy, astroquery"

# Run the demo
echo "[6/6] Running SSZ StarMaps demo..."
echo ""
python -m ssz_starmaps.demo_starmap

echo ""
echo "================================================================================"
echo "Setup complete! Virtual environment is now active."
echo ""
echo "To run again (without setup):"
echo "  source .venv/bin/activate"
echo "  python -m ssz_starmaps.demo_starmap"
echo ""
echo "To deactivate virtual environment:"
echo "  deactivate"
echo "================================================================================"
