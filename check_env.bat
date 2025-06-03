@echo off
echo Checking build environment...

:: Check Visual Studio
if not exist "%ProgramFiles(x86)%\Microsoft Visual Studio\Installer\vswhere.exe" (
    echo Error: Visual Studio not found
    exit /b 1
)

:: Check Vulkan SDK
where glslc >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: Vulkan SDK not found or glslc not in PATH
    echo Please install Vulkan SDK and add it to your PATH
    exit /b 1
)

:: Check CMake
where cmake >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: CMake not found
    echo Please install CMake and add it to your PATH
    exit /b 1
)

:: Check Ninja
where ninja >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: Ninja not found
    echo Please install Ninja and add it to your PATH
    exit /b 1
)

echo Environment check passed!
exit /b 0 