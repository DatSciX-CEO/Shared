@echo off
echo Building Rust Extension (viewerit_core)...

REM Set environment variable for Python 3.14 forward compatibility
set PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1

cd backend\rust_core
maturin develop --release
if %errorlevel% neq 0 (
    echo Build failed! Make sure you have Rust installed and the virtual environment active.
    exit /b %errorlevel%
)
echo Build successful!
cd ..\..

echo.
echo The viewerit_core Rust extension is now installed.
echo You can verify it with: python -c "from viewerit_core import FastIntersector; print('OK')"
