@echo off
title UX-MIRROR Setup & Launcher Creator
color 0B
echo.
echo  ███████ ███████ ████████ ██    ██ ██████  
echo  ██      ██         ██    ██    ██ ██   ██ 
echo  ███████ █████      ██    ██    ██ ██████  
echo  ██      ██         ██    ██    ██ ██   ██ 
echo  ███████ ███████    ██     ██████  ██   ██ 
echo.
echo  🎯 UX-MIRROR + 3D Game of Life Setup
echo  ═══════════════════════════════════════════════════════════════════════
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8+ from https://python.org
    echo After installation, run this setup again.
    echo.
    pause
    exit /b 1
)

echo ✅ Python found
python --version

echo.
echo 📦 Installing/Updating Python dependencies...
echo.

REM Install core requirements
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ ERROR: Failed to install core requirements
    pause
    exit /b 1
)

REM Install Windows-specific packages for shortcuts
pip install pywin32 winshell
if errorlevel 1 (
    echo ⚠️  Warning: Could not install shortcut creation packages
    echo You can still use the batch file launcher
)

echo.
echo 🔨 Setting up target game build environment...
echo.

REM Check if vcpkg is set up in game-target
if exist "game-target\vcpkg" (
    echo ✅ vcpkg found in game-target
) else (
    echo ⚠️  vcpkg not found - game building may require manual setup
)

REM Check if CMake is available
cmake --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  CMake not found - you may need to install it for game building
    echo Download from: https://cmake.org/download/
) else (
    echo ✅ CMake found
    cmake --version | findstr /C:"cmake version"
)

echo.
echo 🖥️  Creating desktop shortcuts...
echo.

REM Try to create shortcuts using Python
python create_desktop_shortcut.py
if errorlevel 1 (
    echo ⚠️  Could not create automatic shortcuts
    echo You can manually run launch_ux_mirror.bat
)

echo.
echo 🎉 Setup Complete!
echo.
echo You now have several ways to start UX-MIRROR + 3D Game of Life:
echo.
echo 1. 📍 Desktop Shortcut: "UX-MIRROR + 3D Game of Life"
echo 2. 📍 Start Menu: Programs → "UX-MIRROR + 3D Game of Life"  
echo 3. 📁 Batch File: Double-click "launch_ux_mirror.bat"
echo 4. 🐍 Python GUI: Run "python launch_ux_mirror.py"
echo 5. 🖥️  Original: Run "python ux_mirror_launcher.py"
echo.
echo Recommended: Use the desktop shortcut for easiest access!
echo.
echo 📚 What you can do:
echo   • Analyze UX of the 3D Game of Life
echo   • Monitor any running application's UX
echo   • Get AI-powered UX insights and recommendations
echo   • Track user engagement and interaction patterns
echo.
pause 