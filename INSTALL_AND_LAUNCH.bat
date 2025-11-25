@echo off
REM UX-MIRROR v0.1.0 - Install and Launch
REM Installs dependencies and launches the GUI

echo ========================================
echo UX-MIRROR v0.1.0 - Install and Launch
echo ========================================
echo.

cd /d "%~dp0"

echo [1/2] Installing dependencies...
python -m pip install -r requirements_v0.1.0.txt --quiet
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

echo [2/2] Launching UX-MIRROR...
echo.
python ux_mirror_launcher.py

if errorlevel 1 (
    echo.
    echo [ERROR] Failed to launch UX-MIRROR
    echo.
    echo Troubleshooting:
    echo   1. Check Python is installed: python --version
    echo   2. Check API key is set: python tests/test_api_key_validation.py
    echo   3. See QUICK_START_v0.1.0.md for help
    echo.
    pause
)

