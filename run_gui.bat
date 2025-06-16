@echo off
echo ========================================
echo    UX-MIRROR GUI Launcher
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://www.python.org/
    pause
    exit /b 1
)

REM Run the GUI launcher
echo Starting UX-MIRROR GUI...
python run_gui.py

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to start UX-MIRROR GUI
    echo Please check the error messages above
    pause
)

exit /b %errorlevel% 