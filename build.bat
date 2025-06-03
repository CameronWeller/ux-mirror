@echo off
setlocal enabledelayedexpansion

:: Set up Vulkan SDK environment
set "VULKAN_SDK=C:\VulkanSDK\1.4.313.0"
set "PATH=%VULKAN_SDK%\Bin;%PATH%"

echo Building project...

:: Clean and recreate build directory
if exist "build" (
    echo Cleaning build directory...
    rmdir /s /q build
)
mkdir build
cd build

:: Configure with CMake
cmake .. -G "Visual Studio 17 2022" ^
    -A x64 ^
    -DCMAKE_BUILD_TYPE=Debug ^
    -DVULKAN_SDK="%VULKAN_SDK%" ^
    -DCMAKE_PREFIX_PATH="%VULKAN_SDK%"

if !ERRORLEVEL! neq 0 (
    echo Error: CMake configuration failed
    exit /b 1
)

:: Build the project
cmake --build . --config Debug

if !ERRORLEVEL! neq 0 (
    echo Error: Build failed
    exit /b 1
)

echo.
echo Build completed successfully!
cd ..

endlocal 