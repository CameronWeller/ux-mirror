@echo off
echo Setting up MinGW GCC through MSYS2...

REM Check if MSYS2 is installed
if not exist "C:\msys64\msys2.exe" (
    echo MSYS2 not found. Installing via winget...
    winget install MSYS2.MSYS2
    if %errorlevel% neq 0 (
        echo Failed to install MSYS2
        pause
        exit /b 1
    )
)

echo MSYS2 found. Installing MinGW GCC...

REM Update MSYS2 and install MinGW GCC
echo Running MSYS2 package installation...
C:\msys64\usr\bin\bash.exe -l -c "pacman -Syu --noconfirm"
C:\msys64\usr\bin\bash.exe -l -c "pacman -S --noconfirm mingw-w64-x86_64-gcc mingw-w64-x86_64-make"

REM Check if installation was successful
if exist "C:\msys64\mingw64\bin\g++.exe" (
    echo ✓ MinGW GCC installed successfully!
    echo.
    echo Adding MinGW to PATH for this session...
    set PATH=C:\msys64\mingw64\bin;%PATH%
    
    echo Testing compiler...
    C:\msys64\mingw64\bin\g++.exe --version
    
    echo.
    echo ✓ Setup complete! You can now build C++ programs.
    echo.
    echo To permanently add MinGW to your PATH:
    echo 1. Open Environment Variables in Windows Settings
    echo 2. Add C:\msys64\mingw64\bin to your PATH variable
    echo.
    echo Or run this in PowerShell as Administrator:
    echo [Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\msys64\mingw64\bin", "Machine")
    echo.
) else (
    echo ✗ MinGW GCC installation failed
    echo Please try manual installation:
    echo 1. Open: C:\msys64\msys2.exe
    echo 2. Run: pacman -S mingw-w64-x86_64-gcc
    pause
    exit /b 1
)

pause 