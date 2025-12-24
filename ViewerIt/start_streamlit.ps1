# ViewerIt Streamlit Startup Script (PowerShell)
Write-Host "===============================================" -ForegroundColor Yellow
Write-Host "   VIEWERIT - Streamlit Dashboard Starting...  " -ForegroundColor Yellow
Write-Host "===============================================" -ForegroundColor Yellow

Set-Location $PSScriptRoot

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

# Start Streamlit
Write-Host ""
Write-Host "Starting Streamlit on http://localhost:8501" -ForegroundColor Green
Write-Host ""
streamlit run streamlit_app/viz_report.py --server.port 8501 --server.headless true

