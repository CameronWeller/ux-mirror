#!/bin/bash

# UX Mirror GitHub Repository Setup Script
# This script helps you set up both public and private repositories

set -e  # Exit on error

echo "==================================="
echo "UX Mirror Repository Setup"
echo "==================================="
echo ""

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "GitHub CLI (gh) is not installed."
    echo "Please install it from: https://cli.github.com/"
    echo "Or run: brew install gh (macOS) / sudo apt install gh (Linux)"
    exit 1
fi

# Check if user is authenticated
if ! gh auth status &> /dev/null; then
    echo "Please authenticate with GitHub first:"
    echo "Run: gh auth login"
    exit 1
fi

# Get GitHub username
GITHUB_USER=$(gh api user -q .login)
echo "GitHub User: $GITHUB_USER"
echo ""

# Function to create repository
create_repo() {
    local repo_name=$1
    local description=$2
    local visibility=$3
    
    echo "Creating $visibility repository: $repo_name"
    
    if gh repo view "$GITHUB_USER/$repo_name" &> /dev/null; then
        echo "Repository $repo_name already exists. Skipping..."
        return
    fi
    
    gh repo create "$repo_name" \
        --description "$description" \
        --$visibility \
        --clone=false \
        --confirm
    
    echo "✓ Repository created successfully"
}

# Create public repository
echo "Step 1: Creating public repository"
echo "---------------------------------"
create_repo "ux-mirror" \
    "GPU-accelerated UX intelligence system for real-time interface optimization" \
    "public"

echo ""

# Create private repository
echo "Step 2: Creating private repository"
echo "----------------------------------"
create_repo "ux-mirror-experimental" \
    "Experimental features and dramatic programming approaches for UX Mirror" \
    "private"

echo ""

# Set up public repository
echo "Step 3: Setting up public repository"
echo "-----------------------------------"

if [ ! -d ".git" ]; then
    git init
fi

# Add all files
git add .
git commit -m "Initial commit: UX Mirror - GPU-accelerated UX intelligence system" || true

# Add remote and push
git remote remove origin 2>/dev/null || true
git remote add origin "https://github.com/$GITHUB_USER/ux-mirror.git"
git branch -M main
git push -u origin main

echo "✓ Public repository set up and pushed"
echo ""

# Create private repository directory
echo "Step 4: Setting up private repository"
echo "------------------------------------"

# Create experimental directory
mkdir -p ../ux-mirror-experimental
cp -r . ../ux-mirror-experimental/
cd ../ux-mirror-experimental

# Initialize git
git init

# Create experimental README addition
cat >> README.md << 'EOF'

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
EOF

# Commit and push
git add .
git commit -m "Initial commit: Experimental UX Mirror with dramatic features"
git remote add origin "https://github.com/$GITHUB_USER/ux-mirror-experimental.git"
git branch -M main
git push -u origin main

# Add public as upstream
git remote add public "https://github.com/$GITHUB_USER/ux-mirror.git"

echo "✓ Private repository set up and pushed"
echo ""

# Create sync script
cat > sync-from-public.sh << 'EOF'
#!/bin/bash
# Sync stable features from public to private

echo "Syncing from public repository..."
git fetch public
git merge public/main --no-ff -m "Sync: Merge stable features from public"
echo "Sync complete!"
EOF

chmod +x sync-from-public.sh

echo "✓ Sync script created"
echo ""

# Return to public directory
cd ../ux-mirror

# Set up branch protection for public repo
echo "Step 5: Configuring repository settings"
echo "--------------------------------------"

# Enable issues, projects, wiki, discussions for public repo
gh repo edit "$GITHUB_USER/ux-mirror" \
    --enable-issues \
    --enable-projects \
    --enable-wiki \
    --enable-discussions || true

echo "✓ Public repository features enabled"

# Create initial issues
echo ""
echo "Step 6: Creating initial issues"
echo "------------------------------"

# Create welcome issue
gh issue create \
    --repo "$GITHUB_USER/ux-mirror" \
    --title "Welcome to UX Mirror! 👋" \
    --body "Welcome to the UX Mirror project! This issue is a place to introduce yourself and learn about the project.

## About UX Mirror
UX Mirror is a GPU-accelerated UX intelligence system that provides real-time interface optimization through continuous monitoring and analysis.

## How to Get Started
1. Read our [Contributing Guide](CONTRIBUTING.md)
2. Check out the [Roadmap](ROADMAP.md)
3. Join our [Discord server](https://discord.gg/YOUR_INVITE)
4. Pick an issue labeled \`good first issue\`

## Introduce Yourself
Feel free to comment below and tell us:
- Your background and interests
- What brought you to this project
- How you'd like to contribute

Looking forward to working with you!" \
    --label "welcome,community" || true

# Create first good first issue
gh issue create \
    --repo "$GITHUB_USER/ux-mirror" \
    --title "Add unit tests for CircularBuffer class" \
    --body "## Description
We need unit tests for the CircularBuffer class that will be used in our metrics collection system.

## Requirements
- Use Google Test framework
- Test edge cases (empty buffer, full buffer, wraparound)
- Ensure thread safety tests
- Add performance benchmarks

## Files to create
- \`tests/core/circular_buffer_test.cpp\`
- Update \`tests/CMakeLists.txt\`

## Getting Started
1. Fork the repository
2. Set up your development environment (see CONTRIBUTING.md)
3. Create the test file
4. Run tests with \`ctest\`

This is a great first issue for getting familiar with our codebase!" \
    --label "good first issue,testing" || true

echo "✓ Initial issues created"
echo ""

echo "==================================="
echo "Setup Complete! 🎉"
echo "==================================="
echo ""
echo "Public Repository: https://github.com/$GITHUB_USER/ux-mirror"
echo "Private Repository: https://github.com/$GITHUB_USER/ux-mirror-experimental"
echo ""
echo "Next Steps:"
echo "1. Update the Discord invite link in README.md"
echo "2. Configure branch protection rules manually"
echo "3. Set up GitHub Secrets for CI/CD"
echo "4. Create a Discord server"
echo "5. Start reaching out to potential contributors"
echo ""
echo "Happy coding! 🚀" 