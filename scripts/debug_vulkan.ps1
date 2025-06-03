# Vulkan Debugging Script for 3D Game of Life
# Helps diagnose common Vulkan issues and run tests

param(
    [switch]$RunTests,
    [switch]$CheckShaders,
    [switch]$ValidateVulkan,
    [switch]$ProfileMemory,
    [switch]$All
)

Write-Host "=== Vulkan Debugging Tool ===" -ForegroundColor Cyan
Write-Host ""

# Check Vulkan SDK
if ($ValidateVulkan -or $All) {
    Write-Host "Checking Vulkan SDK..." -ForegroundColor Yellow
    
    if ($env:VULKAN_SDK) {
        Write-Host "✓ Vulkan SDK found: $env:VULKAN_SDK" -ForegroundColor Green
        
        # Check for key binaries
        $glslc = Join-Path $env:VULKAN_SDK "Bin\glslc.exe"
        $spirvVal = Join-Path $env:VULKAN_SDK "Bin\spirv-val.exe"
        $vulkanInfo = Join-Path $env:VULKAN_SDK "Bin\vulkaninfo.exe"
        
        if (Test-Path $glslc) {
            Write-Host "✓ glslc compiler found" -ForegroundColor Green
        } else {
            Write-Host "✗ glslc compiler NOT found" -ForegroundColor Red
        }
        
        if (Test-Path $spirvVal) {
            Write-Host "✓ spirv-val validator found" -ForegroundColor Green
        } else {
            Write-Host "✗ spirv-val validator NOT found" -ForegroundColor Red
        }
        
        if (Test-Path $vulkanInfo) {
            Write-Host "✓ vulkaninfo found" -ForegroundColor Green
            Write-Host ""
            Write-Host "GPU Information:" -ForegroundColor Cyan
            & $vulkanInfo --summary | Select-String -Pattern "GPU|deviceName|driverVersion" | ForEach-Object { Write-Host "  $_" }
        }
    } else {
        Write-Host "✗ Vulkan SDK not found in environment" -ForegroundColor Red
    }
    Write-Host ""
}

# Check and validate shaders
if ($CheckShaders -or $All) {
    Write-Host "Checking shaders..." -ForegroundColor Yellow
    
    $shaderDir = "shaders"
    if (Test-Path $shaderDir) {
        $shaderFiles = Get-ChildItem -Path $shaderDir -Filter "*.comp" | Select-Object -ExpandProperty Name
        Write-Host "Found compute shaders:" -ForegroundColor Cyan
        foreach ($shader in $shaderFiles) {
            Write-Host "  - $shader" -ForegroundColor Gray
            
            $spvFile = $shader + ".spv"
            $spvPath = Join-Path $shaderDir $spvFile
            
            if (Test-Path $spvPath) {
                Write-Host "    ✓ Compiled SPIR-V exists" -ForegroundColor Green
                
                # Validate SPIR-V
                if ($env:VULKAN_SDK) {
                    $spirvVal = Join-Path $env:VULKAN_SDK "Bin\spirv-val.exe"
                    if (Test-Path $spirvVal) {
                        $validation = & $spirvVal $spvPath 2>&1
                        if ($LASTEXITCODE -eq 0) {
                            Write-Host "    ✓ SPIR-V validation passed" -ForegroundColor Green
                        } else {
                            Write-Host "    ✗ SPIR-V validation failed:" -ForegroundColor Red
                            Write-Host "      $validation" -ForegroundColor Red
                        }
                    }
                }
            } else {
                Write-Host "    ✗ Compiled SPIR-V missing" -ForegroundColor Red
            }
        }
    }
    Write-Host ""
}

# Check VMA integration
if ($ProfileMemory -or $All) {
    Write-Host "Checking VMA integration..." -ForegroundColor Yellow
    
    # Check if VMA header exists
    $vmaHeader = "include\vk_mem_alloc.h"
    if (-not (Test-Path $vmaHeader)) {
        # Try vcpkg location
        $vcpkgVMA = Join-Path $env:VCPKG_ROOT "installed\x64-windows\include\vk_mem_alloc.h"
        if (Test-Path $vcpkgVMA) {
            Write-Host "✓ VMA header found in vcpkg" -ForegroundColor Green
        } else {
            Write-Host "✗ VMA header not found" -ForegroundColor Red
        }
    } else {
        Write-Host "✓ VMA header found locally" -ForegroundColor Green
    }
    
    # Check for VMA usage in code
    Write-Host "Checking VMA usage in code:" -ForegroundColor Cyan
    $vmaUsage = Get-ChildItem -Path "src" -Filter "*.cpp" | Select-String -Pattern "vmaCreate|VmaAllocator" | Select-Object -Property Filename, LineNumber -First 5
    foreach ($usage in $vmaUsage) {
        Write-Host "  - $($usage.Filename):$($usage.LineNumber)" -ForegroundColor Gray
    }
    Write-Host ""
}

# Run tests
if ($RunTests -or $All) {
    Write-Host "Running tests..." -ForegroundColor Yellow
    
    $testExe = "build\Debug\tests.exe"
    if (-not (Test-Path $testExe)) {
        $testExe = "build\tests.exe"
    }
    
    if (Test-Path $testExe) {
        Write-Host "Running test executable: $testExe" -ForegroundColor Cyan
        
        # Run specific test suites
        $testSuites = @(
            "*ComputeShaderTest*",
            "*VMAIntegrationTest*",
            "*VulkanMemoryManagerTest*"
        )
        
        foreach ($suite in $testSuites) {
            Write-Host ""
            Write-Host "Running test suite: $suite" -ForegroundColor Yellow
            & $testExe --gtest_filter=$suite --gtest_color=yes
            
            if ($LASTEXITCODE -ne 0) {
                Write-Host "✗ Test suite failed with code: $LASTEXITCODE" -ForegroundColor Red
            } else {
                Write-Host "✓ Test suite passed" -ForegroundColor Green
            }
        }
    } else {
        Write-Host "✗ Test executable not found at: $testExe" -ForegroundColor Red
        Write-Host "  Please build the tests target first" -ForegroundColor Yellow
    }
    Write-Host ""
}

# Environment diagnostics
Write-Host "Environment Diagnostics:" -ForegroundColor Cyan
Write-Host "  Vulkan SDK: $env:VULKAN_SDK" -ForegroundColor Gray
Write-Host "  VCPKG Root: $env:VCPKG_ROOT" -ForegroundColor Gray
Write-Host "  Current Directory: $(Get-Location)" -ForegroundColor Gray

# Check for common issues
Write-Host ""
Write-Host "Common Issue Checks:" -ForegroundColor Cyan

# Check for validation layers
$validationDll = Join-Path $env:VULKAN_SDK "Bin\VkLayer_khronos_validation.dll"
if (Test-Path $validationDll) {
    Write-Host "✓ Validation layers available" -ForegroundColor Green
} else {
    Write-Host "✗ Validation layers not found" -ForegroundColor Red
}

# Check for debug symbols
$pdbFiles = Get-ChildItem -Path "build" -Filter "*.pdb" -Recurse | Select-Object -First 3
if ($pdbFiles) {
    Write-Host "✓ Debug symbols found" -ForegroundColor Green
} else {
    Write-Host "⚠ No debug symbols found (build in Debug mode for better debugging)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Debugging Tips:" -ForegroundColor Cyan
Write-Host "  1. Enable validation layers by setting VK_INSTANCE_LAYERS=VK_LAYER_KHRONOS_validation" -ForegroundColor Gray
Write-Host "  2. Use RenderDoc for GPU debugging: https://renderdoc.org/" -ForegroundColor Gray
Write-Host "  3. Set VK_LOADER_DEBUG=all for loader debugging" -ForegroundColor Gray
Write-Host "  4. Use vkconfig.exe from Vulkan SDK to configure layers" -ForegroundColor Gray 