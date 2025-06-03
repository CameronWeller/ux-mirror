# PowerShell script to compile Vulkan shaders
param(
    [string]$ShaderDir = "shaders",
    [string]$OutputDir = "build/shaders",
    [string]$GlslcPath = "glslc"
)

# Create output directory if it doesn't exist
if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
    Write-Host "Created output directory: $OutputDir"
}

# Get all shader files
$shaderFiles = Get-ChildItem -Path $ShaderDir -Filter "*.comp" -Recurse

foreach ($shader in $shaderFiles) {
    $outputFile = Join-Path $OutputDir ($shader.BaseName + ".spv")
    
    Write-Host "Compiling $($shader.Name) -> $outputFile"
    
    # Compile shader
    & $GlslcPath $shader.FullName -o $outputFile
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Successfully compiled $($shader.Name)" -ForegroundColor Green
    } else {
        Write-Host "Failed to compile $($shader.Name)" -ForegroundColor Red
        exit 1
    }
}

Write-Host "All shaders compiled successfully!" -ForegroundColor Green 