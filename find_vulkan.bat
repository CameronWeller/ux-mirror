@echo off
echo Searching for Vulkan SDK...

dir /s /b "C:\VulkanSDK\*glslc.exe" 2>nul
dir /s /b "C:\Program Files\VulkanSDK\*glslc.exe" 2>nul
dir /s /b "C:\Program Files (x86)\VulkanSDK\*glslc.exe" 2>nul
dir /s /b "%LOCALAPPDATA%\VulkanSDK\*glslc.exe" 2>nul

echo.
echo If you see any paths above, that's where your Vulkan SDK is installed.
echo If you don't see any paths, please install the Vulkan SDK from:
echo https://vulkan.lunarg.com/sdk/home 