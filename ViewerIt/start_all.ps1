# ViewerIt - Unified Launcher (PowerShell)
# =========================================
# This script provides flexible UI modes:
#   - All (default): Backend + React + Streamlit
#   - React: Backend + React UI only
#   - Streamlit: Backend + Streamlit UI only
#
# Usage:
#   .\start_all.ps1              # Start all services
#   .\start_all.ps1 -UI react    # React UI only
#   .\start_all.ps1 -UI streamlit # Streamlit UI only
#   .\start_all.ps1 -MultiWindow # Legacy multi-window mode
#   .\start_all.ps1 -CheckOnly   # Check prerequisites only
#   .\start_all.ps1 -InstallOnly # Install dependencies only

param(
    [ValidateSet("all", "react", "streamlit")]
    [string]$UI = "all",
    [switch]$MultiWindow,
    [switch]$CheckOnly,
    [switch]$InstallOnly,
    [switch]$SkipChecks,
    [switch]$Open
)

# Banner
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

# Check if Python is available
function Test-Python {
    try {
        $version = python --version 2>&1
        Write-Host "  [OK] $version" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "  [ERROR] Python not found. Install from https://python.org" -ForegroundColor Red
        return $false
    }
}

# Check if run.py exists
function Test-Launcher {
    $launcherPath = Join-Path $ProjectRoot "run.py"
    if (Test-Path $launcherPath) {
        Write-Host "  [OK] Unified launcher found" -ForegroundColor Green
        return $true
    } else {
        Write-Host "  [ERROR] run.py not found in $ProjectRoot" -ForegroundColor Red
        return $false
    }
}

# Unified Mode - Use Python launcher
function Start-UnifiedMode {
    param(
        [string]$UIMode = "all",
        [string]$AdditionalArgs = "",
        [switch]$OpenBrowser
    )
    
    $launcherPath = Join-Path $ProjectRoot "run.py"
    
    Write-Host "Starting unified launcher (UI: $UIMode)..." -ForegroundColor Cyan
    Write-Host ""
    
    Push-Location $ProjectRoot
    try {
        $cmdArgs = @("--ui", $UIMode)
        if ($OpenBrowser) {
            $cmdArgs += "--open"
        }
        if ($AdditionalArgs) {
            $cmdArgs += $AdditionalArgs.Split(" ")
        }
        python $launcherPath @cmdArgs
    } finally {
        Pop-Location
    }
}

# Multi-Window Mode (Legacy) - Open each service in separate window
function Start-MultiWindowMode {
    Write-Host "Starting in Multi-Window mode (legacy)..." -ForegroundColor Yellow
    Write-Host ""
    
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
    Write-Host "  All services starting in separate windows!" -ForegroundColor Green
    Write-Host "===============================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "  Frontend:   http://localhost:5173" -ForegroundColor White
    Write-Host "  Backend:    http://localhost:8000" -ForegroundColor White
    Write-Host "  Streamlit:  http://localhost:8501" -ForegroundColor White
    Write-Host "  API Docs:   http://localhost:8000/docs" -ForegroundColor White
    Write-Host ""
    Write-Host "  Close each window individually to stop services." -ForegroundColor DarkGray
    Write-Host ""
    Write-Host "  Press any key to exit this launcher..." -ForegroundColor DarkGray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

# Main execution
Write-Host "Checking prerequisites..." -ForegroundColor Cyan

if (-not (Test-Python)) {
    Write-Host ""
    Write-Host "Please install Python 3.10+ and try again." -ForegroundColor Red
    exit 1
}

if (-not (Test-Launcher)) {
    Write-Host ""
    Write-Host "Launcher not found. Falling back to multi-window mode." -ForegroundColor Yellow
    Start-MultiWindowMode
    exit 0
}

Write-Host ""

# Handle different modes
if ($CheckOnly) {
    Start-UnifiedMode -UIMode $UI -AdditionalArgs "--check"
} elseif ($InstallOnly) {
    Start-UnifiedMode -UIMode $UI -AdditionalArgs "--install"
} elseif ($MultiWindow) {
    Start-MultiWindowMode
} else {
    # Default: Unified mode with selected UI
    $additionalArgs = ""
    if ($SkipChecks) {
        $additionalArgs = "--skip-checks"
    }
    Start-UnifiedMode -UIMode $UI -AdditionalArgs $additionalArgs -OpenBrowser:$Open
}
