@echo off
setlocal enabledelayedexpansion

echo Setting up Vulkan SDK environment...

:: Check multiple possible installation paths
set "VULKAN_PATHS=C:\VulkanSDK;C:\Program Files\VulkanSDK;C:\Program Files (x86)\VulkanSDK;%LOCALAPPDATA%\VulkanSDK"

for %%p in ("%VULKAN_PATHS:;=" "%") do (
    if exist "%%~p" (
        set "VULKAN_SDK_PATH=%%~p"
        goto :found_sdk
    )
)

:not_found
echo Vulkan SDK not found in common locations.
echo Please download and install Vulkan SDK from: https://vulkan.lunarg.com/sdk/home
echo After installation, run this script again.
echo.
echo Installation instructions:
echo 1. Download the latest Vulkan SDK from https://vulkan.lunarg.com/sdk/home
echo 2. Run the installer
echo 3. Make sure to select "Add to PATH" during installation
echo 4. Restart your terminal after installation
exit /b 1

:found_sdk
echo Found Vulkan SDK at: !VULKAN_SDK_PATH!

:: Find the latest version
set "LATEST_VERSION="
for /f "tokens=*" %%i in ('dir /b /ad "!VULKAN_SDK_PATH!"') do (
    set "LATEST_VERSION=%%i"
)

if not defined LATEST_VERSION (
    echo Error: No version found in !VULKAN_SDK_PATH!
    goto :not_found
)

:: Set up environment variables
set "VULKAN_SDK=!VULKAN_SDK_PATH!\!LATEST_VERSION!"
set "PATH=!VULKAN_SDK!\Bin;!PATH!"

echo.
echo Vulkan SDK version: !LATEST_VERSION!
echo VULKAN_SDK path: !VULKAN_SDK!

:: Verify glslc is available
where glslc >nul 2>nul
if !ERRORLEVEL! neq 0 (
    echo.
    echo Error: glslc not found in PATH
    echo Current PATH: !PATH!
    echo.
    echo Please try these steps:
    echo 1. Make sure Vulkan SDK is properly installed
    echo 2. Try restarting your terminal
    echo 3. If the issue persists, manually add to PATH:
    echo    !VULKAN_SDK!\Bin
    exit /b 1
)

:: Verify glslc works
glslc --version >nul 2>nul
if !ERRORLEVEL! neq 0 (
    echo.
    echo Error: glslc found but failed to run
    echo Please check your Vulkan SDK installation
    exit /b 1
)

echo.
echo Vulkan SDK environment set up successfully!
echo glslc is now available in PATH

:: Run the environment check again
call check_env.bat

endlocal 