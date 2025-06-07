@echo off
echo Building UX Test Game (C++ Edition)...

REM Check if g++ is available
g++ --version >nul 2>&1
if %errorlevel% neq 0 (
    echo g++ not found in PATH. Checking MSYS2 installation...
    
    REM Try MSYS2 MinGW64 path
    if exist "C:\msys64\mingw64\bin\g++.exe" (
        echo Found MSYS2 MinGW64. Adding to PATH for this session...
        set PATH=C:\msys64\mingw64\bin;%PATH%
        echo Please install MinGW GCC with: 
        echo   C:\msys64\msys2.exe
        echo   pacman -S mingw-w64-x86_64-gcc
        echo Then re-run this script.
        pause
        exit /b 1
    ) else (
        echo Error: g++ compiler not found. Installing with winget...
        echo MSYS2 is installed but MinGW GCC is not configured.
        echo.
        echo To install MinGW GCC:
        echo 1. Open MSYS2 terminal: C:\msys64\msys2.exe
        echo 2. Run: pacman -S mingw-w64-x86_64-gcc
        echo 3. Add C:\msys64\mingw64\bin to your PATH
        echo.
        pause
        exit /b 1
    )
)

REM Compile the game
echo Compiling...
g++ -std=c++17 -O2 -Wall -Wextra ^
    -I. ^
    test_cpp_game.cpp ^
    -o ux_test_game.exe ^
    -lgdi32 -luser32 -lopengl32 -lgdiplus -lShlwapi -ldwmapi -lstdc++fs

if %errorlevel% equ 0 (
    echo.
    echo ✓ Build successful! 
    echo ✓ Executable created: ux_test_game.exe
    echo.
    echo Checking Anthropic API key...
    if "%ANTHROPIC_API_KEY%"=="" (
        echo ⚠ Warning: ANTHROPIC_API_KEY environment variable not set!
        echo Please set it with: set ANTHROPIC_API_KEY=your_key_here
    ) else (
        echo ✓ Anthropic API key found in environment
    )
    echo.
    echo To run the game: ux_test_game.exe
    echo To test with UX-MIRROR: python ux_mirror_launcher.py
    echo.
) else (
    echo.
    echo ✗ Build failed! Check the error messages above.
    echo.
)

pause 