# SSZ StarMaps - Automated Setup and Run Script
# © 2025 Carmen Wrede, Lino Casu
#
# This script automatically:
# 1. Creates virtual environment
# 2. Installs dependencies
# 3. Runs the demo
#
# Usage: .\setup_and_run.ps1

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "SSZ StarMaps - Automated Setup" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[1/6] Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python not found! Please install Python 3.8+" -ForegroundColor Red
    exit 1
}

# Create virtual environment if it doesn't exist
if (-not (Test-Path ".venv")) {
    Write-Host "[2/6] Creating virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
    Write-Host "      Virtual environment created." -ForegroundColor Green
} else {
    Write-Host "[2/6] Virtual environment already exists." -ForegroundColor Green
}

# Activate virtual environment
Write-Host "[3/6] Activating virtual environment..." -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1

# Upgrade pip
Write-Host "[4/6] Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet

# Install dependencies
Write-Host "[5/6] Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet
Write-Host "      Dependencies installed: numpy, matplotlib, astropy, astroquery" -ForegroundColor Green

# Run the demo
Write-Host "[6/6] Running SSZ StarMaps demo..." -ForegroundColor Yellow
Write-Host ""
python -m ssz_starmaps.demo_starmap

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "Setup complete! Virtual environment is now active." -ForegroundColor Green
Write-Host ""
Write-Host "To run again (without setup):" -ForegroundColor Cyan
Write-Host "  .\.venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "  python -m ssz_starmaps.demo_starmap" -ForegroundColor White
Write-Host ""
Write-Host "To deactivate virtual environment:" -ForegroundColor Cyan
Write-Host "  deactivate" -ForegroundColor White
Write-Host "================================================================================" -ForegroundColor Cyan
