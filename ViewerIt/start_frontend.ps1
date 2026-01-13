# ViewerIt Frontend Startup Script (PowerShell)
Write-Host "===============================================" -ForegroundColor Magenta
Write-Host "   VIEWERIT - Frontend Server Starting...      " -ForegroundColor Magenta
Write-Host "===============================================" -ForegroundColor Magenta

Set-Location $PSScriptRoot\frontend

# Check for node_modules
if (-Not (Test-Path "node_modules")) {
    Write-Host "Installing npm dependencies..." -ForegroundColor Yellow
    npm install
}

# Start the dev server
Write-Host ""
Write-Host "Starting Vite dev server on http://localhost:5173" -ForegroundColor Green
Write-Host ""
npm run dev

