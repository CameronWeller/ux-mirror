@echo off
setlocal enabledelayedexpansion

echo Checking Vulkan SDK installation...

:: Set the Vulkan SDK path
set "VULKAN_SDK=C:\VulkanSDK\1.4.313.0"
set "PATH=%VULKAN_SDK%\Bin;%PATH%"

:: Verify glslc exists
if exist "%VULKAN_SDK%\Bin\glslc.exe" (
    echo Found glslc.exe at: %VULKAN_SDK%\Bin\glslc.exe
) else (
    echo Error: glslc.exe not found at %VULKAN_SDK%\Bin\glslc.exe
    exit /b 1
)

:: Try to run glslc
glslc --version
if !ERRORLEVEL! neq 0 (
    echo Error: Failed to run glslc
    exit /b 1
)

echo.
echo Vulkan SDK environment is set up correctly!
echo VULKAN_SDK=%VULKAN_SDK%
echo PATH has been updated to include Vulkan SDK binaries

endlocal 