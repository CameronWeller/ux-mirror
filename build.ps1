# Find Visual Studio installation
$vswhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"
$vsPath = & $vswhere -latest -property installationPath

if (-not $vsPath) {
    Write-Error "Visual Studio not found. Please install Visual Studio 2022 with C++ development tools."
    exit 1
}

# Set up Visual Studio environment
$devCmd = Join-Path $vsPath "Common7\Tools\Launch-VsDevShell.ps1"
if (Test-Path $devCmd) {
    & $devCmd -Arch amd64 -HostArch amd64
} else {
    Write-Error "Could not find Visual Studio developer command prompt script."
    exit 1
}

# Create build directory if it doesn't exist
if (-not (Test-Path "build")) {
    New-Item -ItemType Directory -Path "build"
}

# Enter build directory
Set-Location build

try {
    # Configure with CMake
    Write-Host "Configuring project with CMake..."
    cmake -G "Visual Studio 17 2022" -A x64 ..

    if ($LASTEXITCODE -ne 0) {
        throw "CMake configuration failed with exit code $LASTEXITCODE"
    }

    # Build the project
    Write-Host "Building project..."
    cmake --build . --config Debug

    if ($LASTEXITCODE -ne 0) {
        throw "Build failed with exit code $LASTEXITCODE"
    }

    Write-Host "Build completed successfully!"
    Write-Host "Executable location: $((Get-Location).Path)\bin\Debug\vulkan_3d_game_of_life.exe"
}
catch {
    Write-Error "Error: $_"
    exit 1
}
finally {
    # Return to original directory
    Set-Location ..
} 