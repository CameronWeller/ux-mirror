@echo off
title UX-MIRROR + 3D Game of Life Launcher
color 0A
echo.
echo  ██    ██ ██   ██       ███    ███ ██ ██████  ██████   ██████  ██████  
echo  ██    ██  ██ ██        ████  ████ ██ ██   ██ ██   ██ ██    ██ ██   ██ 
echo  ██    ██   ███   █████ ██ ████ ██ ██ ██████  ██████  ██    ██ ██████  
echo  ██    ██  ██ ██        ██  ██  ██ ██ ██   ██ ██   ██ ██    ██ ██   ██ 
echo   ██████  ██   ██       ██      ██ ██ ██   ██ ██   ██  ██████  ██   ██ 
echo.
echo  🎯 Intelligent UX Analysis + 3D Game of Life
echo  ═══════════════════════════════════════════════════════════════════════
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Check if the UX-MIRROR launcher exists
if not exist "ux_mirror_launcher.py" (
    echo ❌ ERROR: UX-MIRROR launcher not found
    echo Please ensure you're running this from the UX-MIRROR project directory
    pause
    exit /b 1
)

REM Check if requirements are installed
echo 🔍 Checking Python dependencies...
python -c "import tkinter, psutil, asyncio" >nul 2>&1
if errorlevel 1 (
    echo 📦 Installing required dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Check and build the target game if needed
echo 🎮 Checking target game (3D Game of Life - Vulkan Edition)...
if exist "game-target" (
    cd game-target
    
    REM Check if the game executable exists
    if not exist "build_minimal\x64\Release\minimal_vulkan_app.exe" (
        echo 🔨 Building target game...
        if exist "scripts\build_windows.bat" (
            call scripts\build_windows.bat
        ) else (
            echo 📝 Building minimal Vulkan application...
            if not exist "build_minimal" mkdir build_minimal
            cd build_minimal
            cmake -S .. -B . -DCMAKE_BUILD_TYPE=Release -DCMAKE_TOOLCHAIN_FILE=../vcpkg/scripts/buildsystems/vcpkg.cmake
            cmake --build . --config Release
            cd ..
        )
    )
    
    cd ..
) else (
    echo ⚠️  Warning: Target game directory not found
    echo UX-MIRROR will launch in application detection mode
    echo.
)

REM Set environment variables
set GAME_TARGET_PATH=%CD%\game-target\build_minimal\x64\Release\minimal_vulkan_app.exe
set UX_MIRROR_CONFIG=%CD%\game_ux_config.json

echo 🚀 Starting UX-MIRROR System...
echo.
echo Target Game: 3D Game of Life (Vulkan Edition)
echo Config: %UX_MIRROR_CONFIG%
echo.
echo Instructions:
echo ┌─────────────────────────────────────────────────────────────┐
echo │ 1. The UX-MIRROR launcher window will open                 │
echo │ 2. Select "3D Game of Life" or launch it manually          │
echo │ 3. Configure analysis settings as needed                   │
echo │ 4. Click "Start Analysis" to begin UX monitoring          │
echo │ 5. Play the game naturally while analysis runs            │
echo │ 6. Review UX insights and recommendations                  │
echo └─────────────────────────────────────────────────────────────┘
echo.
echo Press any key to launch...
pause >nul

REM Start the UX-MIRROR launcher
python ux_mirror_launcher.py

echo.
echo 📊 UX-MIRROR session completed.
echo Check the reports/ directory for analysis results.
echo.
pause 