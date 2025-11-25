@echo off
setlocal enabledelayedexpansion

echo 🤖 UX-MIRROR Autonomous Testing Setup - Phase 1 (Windows)
echo ═══════════════════════════════════════════════════════════

REM Create directory structure
echo Creating autonomous testing directories...
if not exist "ux_mirror_autonomous" mkdir "ux_mirror_autonomous"
if not exist "ux_mirror_autonomous\core" mkdir "ux_mirror_autonomous\core"
if not exist "ux_mirror_autonomous\scenarios" mkdir "ux_mirror_autonomous\scenarios"
if not exist "ux_mirror_autonomous\config" mkdir "ux_mirror_autonomous\config"
if not exist "ux_mirror_autonomous\utils" mkdir "ux_mirror_autonomous\utils"
if not exist "ux_mirror_autonomous\test_results" mkdir "ux_mirror_autonomous\test_results"
if not exist "ux_mirror_autonomous\downloads" mkdir "ux_mirror_autonomous\downloads"

echo ✅ Directory structure created

REM Check Python
python --version >nul 2>&1
if %errorlevel% == 0 (
    echo ✅ Python found
) else (
    echo ❌ Python not found - please install Python 3.8+
    pause
    exit /b 1
)

REM Install Python dependencies
echo Installing Python dependencies...
pip install pyyaml requests psutil

echo ✅ Phase 1 setup completed!
echo 📁 Files created in: ux_mirror_autonomous\
echo 🚀 Next: Manual VM setup with VirtualBox/VMware

pause 