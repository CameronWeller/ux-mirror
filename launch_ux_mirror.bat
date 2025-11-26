@echo off
REM UX-MIRROR v0.1.0 Launcher
REM Quick launch script for GUI

cd /d "%~dp0"
python ux_mirror_launcher.py

if errorlevel 1 (
    echo.
    echo [ERROR] Failed to launch UX-MIRROR
    echo.
    echo Make sure Python is installed and dependencies are available:
    echo   pip install -r requirements_v0.1.0.txt
    echo.
    pause
)


