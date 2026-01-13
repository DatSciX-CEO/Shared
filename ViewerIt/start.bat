@echo off
:: =============================================================================
:: ViewerIt Unified Launcher - Windows Batch File
:: =============================================================================
:: Double-click this file to start all ViewerIt services.
:: Requires Python 3.10+ installed and on PATH.
:: =============================================================================

title ViewerIt Unified Launcher

:: Enable delayed expansion for better variable handling
setlocal enabledelayedexpansion

:: Change to the script's directory
cd /d "%~dp0"

:: Check if Python is available
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Python is not installed or not on PATH.
    echo Please install Python 3.10+ from https://python.org
    echo.
    pause
    exit /b 1
)

:: Check Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYVER=%%i
echo Detected Python version: %PYVER%

:: Run the unified launcher
echo.
echo Starting ViewerIt...
echo =================================================
echo.

python run.py

:: If the script exits, pause to show any errors
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] ViewerIt exited with an error.
    pause
)

