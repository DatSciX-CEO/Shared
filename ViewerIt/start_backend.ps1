# ViewerIt Backend Startup Script (PowerShell)
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "   VIEWERIT - Backend Server Starting...       " -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan

Set-Location $PSScriptRoot\backend

# Check for virtual environment
if (-Not (Test-Path "..\venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv ..\venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
..\venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r ..\requirements.txt

# Start the server
Write-Host ""
Write-Host "Starting FastAPI server on http://localhost:8000" -ForegroundColor Green
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Green
Write-Host ""
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

