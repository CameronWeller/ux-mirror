# UX Mirror Repository Setup Guide

## Dual Repository Strategy

### Overview
We'll maintain two repositories:
1. **Public Repository** (`ux-mirror`) - Professional, community-facing
2. **Private Repository** (`ux-mirror-experimental`) - Bold experiments, dramatic features

## Step 1: Create the Public Repository

### 1.1 Initialize Public Repo
```bash
# Create a new directory for the public version
mkdir ux-mirror-public
cd ux-mirror-public

# Initialize git
git init

# Copy the professional files we created
cp -r ../ux-mirror/* .

# Create initial commit
git add .
git commit -m "Initial commit: UX Mirror - GPU-accelerated UX intelligence system"
```

### 1.2 Create GitHub Repository
1. Go to https://github.com/new
2. Repository name: `ux-mirror`
3. Description: "GPU-accelerated UX intelligence system for real-time interface optimization"
4. Public repository
5. Add README: No (we have one)
6. Add .gitignore: No (we'll create one)
7. Choose license: MIT

### 1.3 Push to GitHub
```bash
# Add remote
git remote add origin https://github.com/YOUR_USERNAME/ux-mirror.git

# Push to main branch
git branch -M main
git push -u origin main
```

## Step 2: Create the Private Repository

### 2.1 Initialize Private Repo
```bash
# Create directory for experimental version
mkdir ../ux-mirror-experimental
cd ../ux-mirror-experimental

# Initialize git
git init

# Copy all files including experimental features
cp -r ../ux-mirror/* .
```

### 2.2 Create Private GitHub Repository
1. Go to https://github.com/new
2. Repository name: `ux-mirror-experimental`
3. Description: "Experimental features and dramatic programming approaches for UX Mirror"
4. **Private repository** ✓
5. Create repository

### 2.3 Push to Private Repo
```bash
git remote add origin https://github.com/YOUR_USERNAME/ux-mirror-experimental.git
git add .
git commit -m "Initial commit: Experimental UX Mirror with dramatic features"
git push -u origin main
```

## Step 3: Set Up Synchronization

### 3.1 Add Public as Upstream to Private
```bash
# In the private repository
cd ../ux-mirror-experimental
git remote add public https://github.com/YOUR_USERNAME/ux-mirror.git
```

### 3.2 Create Sync Script
Create `sync-from-public.sh`:
```bash
#!/bin/bash
# Sync stable features from public to private

echo "Syncing from public repository..."
git fetch public
git merge public/main --no-ff -m "Sync: Merge stable features from public"
echo "Sync complete!"
```

## Step 4: Configure Repository Settings

### Public Repository Settings
1. Go to Settings → General
2. Features:
   - ✓ Issues
   - ✓ Projects
   - ✓ Wiki
   - ✓ Discussions
3. Pull Requests:
   - ✓ Allow merge commits
   - ✓ Allow squash merging
   - ✓ Allow rebase merging

### Private Repository Settings
1. Go to Settings → General
2. Features:
   - ✓ Issues
   - ✓ Projects
   - ✗ Wiki (keep internal docs private)
   - ✗ Discussions (use Discord)
3. Add collaborators as needed

## Step 5: Create .gitignore Files

### Public Repository .gitignore
```gitignore
# Build directories
build/
out/
cmake-build-*/

# IDE files
.idea/
.vscode/
*.swp
*.swo
*~

# OS files
.DS_Store
Thumbs.db

# Compiled files
*.o
*.so
*.dll
*.exe
*.pdb

# Dependencies
vcpkg_installed/
conan/

# Logs
*.log

# Private keys
*.pem
*.key
```

### Private Repository .gitignore
```gitignore
# Same as public, plus:

# Experimental features
experimental/
dramatic/
unsafe/

# Personal notes
notes/
ideas/

# Sensitive configs
config.private.json
secrets/
```

## Step 6: Branch Protection Rules

### Public Repository
1. Go to Settings → Branches
2. Add rule for `main`:
   - ✓ Require pull request reviews (1)
   - ✓ Dismiss stale reviews
   - ✓ Require status checks
   - ✓ Require branches up to date
   - ✓ Include administrators

### Private Repository
- More relaxed rules
- Direct push to main allowed
- Experimental branches encouraged

## Step 7: Documentation Differences

### Public Repository Docs
- Professional tone
- Clear technical documentation
- Community-focused language
- Conservative promises

### Private Repository Docs
- Experimental ideas
- Bold vision statements
- Dramatic feature descriptions
- Unconstrained creativity

## Step 8: Feature Migration Workflow

### Moving Features from Private to Public
```bash
# In private repo
git checkout -b feature/prepare-for-public

# Clean up experimental code
# Remove dramatic comments
# Add proper documentation
# Ensure tests pass

git commit -m "Prepare feature X for public release"

# Create patch
git format-patch -1 HEAD

# In public repo
git apply ../ux-mirror-experimental/0001-*.patch
git add .
git commit -m "feat: Add feature X"
```

## Security Considerations

### Public Repository
- No API keys or secrets
- No internal URLs
- No proprietary algorithms
- Sanitized example configs

### Private Repository
- Use GitHub Secrets for sensitive data
- Enable 2FA for all collaborators
- Regular security audits
- Encrypted backups

## Communication Strategy

### Public Channels
- GitHub Issues/Discussions
- Discord (public channels)
- Twitter/Blog posts
- Conference talks

### Private Channels
- Private Discord channels
- Internal documentation
- Direct collaborator chat
- Experimental feature demos

## Next Steps

1. **Create both repositories** following this guide
2. **Set up branch protection** on public repo
3. **Configure CI/CD** for both repos
4. **Create initial issues** for community
5. **Write blog post** announcing the project
6. **Start outreach** to potential contributors

Remember: The public repo is your professional face, while the private repo is your creative playground! 