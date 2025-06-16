# UX Mirror GitHub Repository Setup Script for Windows
# This script helps you set up both public and private repositories

Write-Host "===================================" -ForegroundColor Cyan
Write-Host "UX Mirror Repository Setup" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan
Write-Host ""

# Check if gh CLI is installed
try {
    $null = gh --version
} catch {
    Write-Host "GitHub CLI (gh) is not installed." -ForegroundColor Red
    Write-Host "Please install it from: https://cli.github.com/" -ForegroundColor Yellow
    Write-Host "Or run: winget install GitHub.cli" -ForegroundColor Yellow
    exit 1
}

# Check if user is authenticated
try {
    $null = gh auth status
} catch {
    Write-Host "Please authenticate with GitHub first:" -ForegroundColor Red
    Write-Host "Run: gh auth login" -ForegroundColor Yellow
    exit 1
}

# Get GitHub username
$GITHUB_USER = gh api user -q .login
Write-Host "GitHub User: $GITHUB_USER" -ForegroundColor Green
Write-Host ""

# Function to create repository
function Create-Repository {
    param(
        [string]$RepoName,
        [string]$Description,
        [string]$Visibility
    )
    
    Write-Host "Creating $Visibility repository: $RepoName" -ForegroundColor Yellow
    
    try {
        $null = gh repo view "$GITHUB_USER/$RepoName" 2>$null
        Write-Host "Repository $RepoName already exists. Skipping..." -ForegroundColor Gray
        return
    } catch {
        # Repository doesn't exist, create it
    }
    
    gh repo create $RepoName `
        --description $Description `
        --$Visibility `
        --clone=false `
        --confirm
    
    Write-Host "✓ Repository created successfully" -ForegroundColor Green
}

# Create public repository
Write-Host "Step 1: Creating public repository" -ForegroundColor Cyan
Write-Host "---------------------------------" -ForegroundColor Cyan
Create-Repository -RepoName "ux-mirror" `
    -Description "GPU-accelerated UX intelligence system for real-time interface optimization" `
    -Visibility "public"

Write-Host ""

# Create private repository
Write-Host "Step 2: Creating private repository" -ForegroundColor Cyan
Write-Host "----------------------------------" -ForegroundColor Cyan
Create-Repository -RepoName "ux-mirror-experimental" `
    -Description "Experimental features and dramatic programming approaches for UX Mirror" `
    -Visibility "private"

Write-Host ""

# Set up public repository
Write-Host "Step 3: Setting up public repository" -ForegroundColor Cyan
Write-Host "-----------------------------------" -ForegroundColor Cyan

if (-not (Test-Path .git)) {
    git init
}

# Add all files
git add .
git commit -m "Initial commit: UX Mirror - GPU-accelerated UX intelligence system" 2>$null

# Add remote and push
git remote remove origin 2>$null
git remote add origin "https://github.com/$GITHUB_USER/ux-mirror.git"
git branch -M main
git push -u origin main

Write-Host "✓ Public repository set up and pushed" -ForegroundColor Green
Write-Host ""

# Create private repository directory
Write-Host "Step 4: Setting up private repository" -ForegroundColor Cyan
Write-Host "------------------------------------" -ForegroundColor Cyan

# Create experimental directory
New-Item -ItemType Directory -Force -Path "../ux-mirror-experimental" | Out-Null
Copy-Item -Path "." -Destination "../ux-mirror-experimental" -Recurse -Force
Set-Location "../ux-mirror-experimental"

# Initialize git
git init

# Create experimental README addition
@"

---

## 🚀 Experimental Features

This is the experimental branch of UX Mirror where we explore:

- **Dramatic Programming Paradigms**: Bold approaches to self-programming systems
- **Unsafe Optimizations**: Performance experiments that push boundaries
- **Wild Ideas**: Unconventional UX analysis techniques
- **Future Vision**: Features that might be 5-10 years ahead

### Current Experiments

1. **Neural Architecture Search for UI**: Self-evolving interface layouts
2. **Quantum-Inspired Optimization**: Superposition of UI states
3. **Consciousness Simulation**: UX that adapts to user mental states
4. **Time-Travel Debugging**: Replay and modify user sessions in real-time

### Warning

This repository contains experimental code that may:
- Break unexpectedly
- Use excessive resources
- Implement unconventional patterns
- Challenge traditional programming paradigms

**Use at your own risk!**
"@ | Add-Content -Path "README.md"

# Commit and push
git add .
git commit -m "Initial commit: Experimental UX Mirror with dramatic features"
git remote add origin "https://github.com/$GITHUB_USER/ux-mirror-experimental.git"
git branch -M main
git push -u origin main

# Add public as upstream
git remote add public "https://github.com/$GITHUB_USER/ux-mirror.git"

Write-Host "✓ Private repository set up and pushed" -ForegroundColor Green
Write-Host ""

# Create sync script
@'
#!/bin/bash
# Sync stable features from public to private

echo "Syncing from public repository..."
git fetch public
git merge public/main --no-ff -m "Sync: Merge stable features from public"
echo "Sync complete!"
'@ | Out-File -FilePath "sync-from-public.sh" -Encoding UTF8

Write-Host "✓ Sync script created" -ForegroundColor Green
Write-Host ""

# Return to public directory
Set-Location "../ux-mirror"

# Set up branch protection for public repo
Write-Host "Step 5: Configuring repository settings" -ForegroundColor Cyan
Write-Host "--------------------------------------" -ForegroundColor Cyan

# Enable issues, projects, wiki, discussions for public repo
gh repo edit "$GITHUB_USER/ux-mirror" `
    --enable-issues `
    --enable-projects `
    --enable-wiki `
    --enable-discussions 2>$null

Write-Host "✓ Public repository features enabled" -ForegroundColor Green

# Create initial issues
Write-Host ""
Write-Host "Step 6: Creating initial issues" -ForegroundColor Cyan
Write-Host "------------------------------" -ForegroundColor Cyan

# Create welcome issue
$welcomeBody = @"
Welcome to the UX Mirror project! This issue is a place to introduce yourself and learn about the project.

## About UX Mirror
UX Mirror is a GPU-accelerated UX intelligence system that provides real-time interface optimization through continuous monitoring and analysis.

## How to Get Started
1. Read our [Contributing Guide](CONTRIBUTING.md)
2. Check out the [Roadmap](ROADMAP.md)
3. Join our [Discord server](https://discord.gg/YOUR_INVITE)
4. Pick an issue labeled ``good first issue``

## Introduce Yourself
Feel free to comment below and tell us:
- Your background and interests
- What brought you to this project
- How you'd like to contribute

Looking forward to working with you!
"@

gh issue create `
    --repo "$GITHUB_USER/ux-mirror" `
    --title "Welcome to UX Mirror! 👋" `
    --body $welcomeBody `
    --label "welcome,community" 2>$null

# Create first good first issue
$issueBody = @"
## Description
We need unit tests for the CircularBuffer class that will be used in our metrics collection system.

## Requirements
- Use Google Test framework
- Test edge cases (empty buffer, full buffer, wraparound)
- Ensure thread safety tests
- Add performance benchmarks

## Files to create
- ``tests/core/circular_buffer_test.cpp``
- Update ``tests/CMakeLists.txt``

## Getting Started
1. Fork the repository
2. Set up your development environment (see CONTRIBUTING.md)
3. Create the test file
4. Run tests with ``ctest``

This is a great first issue for getting familiar with our codebase!
"@

gh issue create `
    --repo "$GITHUB_USER/ux-mirror" `
    --title "Add unit tests for CircularBuffer class" `
    --body $issueBody `
    --label "good first issue,testing" 2>$null

Write-Host "✓ Initial issues created" -ForegroundColor Green
Write-Host ""

Write-Host "===================================" -ForegroundColor Cyan
Write-Host "Setup Complete! 🎉" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Public Repository: https://github.com/$GITHUB_USER/ux-mirror" -ForegroundColor Green
Write-Host "Private Repository: https://github.com/$GITHUB_USER/ux-mirror-experimental" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Update the Discord invite link in README.md"
Write-Host "2. Configure branch protection rules manually"
Write-Host "3. Set up GitHub Secrets for CI/CD"
Write-Host "4. Create a Discord server"
Write-Host "5. Start reaching out to potential contributors"
Write-Host ""
Write-Host "Happy coding! 🚀" -ForegroundColor Cyan 