# ViewerIt - Start All Services
Write-Host ""
Write-Host "  ██╗   ██╗██╗███████╗██╗    ██╗███████╗██████╗ ██╗████████╗" -ForegroundColor Cyan
Write-Host "  ██║   ██║██║██╔════╝██║    ██║██╔════╝██╔══██╗██║╚══██╔══╝" -ForegroundColor Cyan
Write-Host "  ██║   ██║██║█████╗  ██║ █╗ ██║█████╗  ██████╔╝██║   ██║   " -ForegroundColor Magenta
Write-Host "  ╚██╗ ██╔╝██║██╔══╝  ██║███╗██║██╔══╝  ██╔══██╗██║   ██║   " -ForegroundColor Magenta
Write-Host "   ╚████╔╝ ██║███████╗╚███╔███╔╝███████╗██║  ██║██║   ██║   " -ForegroundColor Yellow
Write-Host "    ╚═══╝  ╚═╝╚══════╝ ╚══╝╚══╝ ╚══════╝╚═╝  ╚═╝╚═╝   ╚═╝   " -ForegroundColor Yellow
Write-Host ""
Write-Host "  Cyberpunk eDiscovery Data Comparator" -ForegroundColor DarkGray
Write-Host ""

$ProjectRoot = $PSScriptRoot

# Start Backend in new window
Write-Host "[1/3] Starting Backend Server..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-File", "$ProjectRoot\start_backend.ps1"

Start-Sleep -Seconds 3

# Start Streamlit in new window
Write-Host "[2/3] Starting Streamlit Dashboard..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-File", "$ProjectRoot\start_streamlit.ps1"

Start-Sleep -Seconds 2

# Start Frontend in new window
Write-Host "[3/3] Starting Frontend..." -ForegroundColor Magenta
Start-Process powershell -ArgumentList "-NoExit", "-File", "$ProjectRoot\start_frontend.ps1"

Write-Host ""
Write-Host "===============================================" -ForegroundColor Green
Write-Host "  All services starting!" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Frontend:   http://localhost:5173" -ForegroundColor White
Write-Host "  Backend:    http://localhost:8000" -ForegroundColor White
Write-Host "  Streamlit:  http://localhost:8501" -ForegroundColor White
Write-Host "  API Docs:   http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "  Press any key to exit this launcher..." -ForegroundColor DarkGray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

