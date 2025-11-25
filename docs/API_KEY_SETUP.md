# API Key Setup Guide

This guide explains how to set up API keys for UX-MIRROR v0.1.0.

## Overview

UX-MIRROR supports two AI vision providers:
- **Anthropic Claude** (recommended, required for full functionality)
- **OpenAI GPT-4 Vision** (optional)

## Step 1: Get Your API Keys

### Anthropic API Key (Required)
1. Visit https://console.anthropic.com/
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key (starts with `sk-ant-`)

### OpenAI API Key (Optional)
1. Visit https://platform.openai.com/api-keys
2. Sign up or log in
3. Create a new API key
4. Copy the key (starts with `sk-`)

## Step 2: Set Environment Variables

### Windows PowerShell
```powershell
# Anthropic (required)
$env:ANTHROPIC_API_KEY = "sk-ant-your-key-here"

# OpenAI (optional)
$env:OPENAI_API_KEY = "sk-your-key-here"
```

### Windows Command Prompt (CMD)
```cmd
set ANTHROPIC_API_KEY=sk-ant-your-key-here
set OPENAI_API_KEY=sk-your-key-here
```

### Linux/Mac (Bash/Zsh)
```bash
# Anthropic (required)
export ANTHROPIC_API_KEY="sk-ant-your-key-here"

# OpenAI (optional)
export OPENAI_API_KEY="sk-your-key-here"
```

### Make Environment Variables Persistent

#### Windows (PowerShell)
Add to your PowerShell profile:
```powershell
# Edit profile: notepad $PROFILE
$env:ANTHROPIC_API_KEY = "sk-ant-your-key-here"
$env:OPENAI_API_KEY = "sk-your-key-here"
```

#### Linux/Mac
Add to `~/.bashrc` or `~/.zshrc`:
```bash
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
export OPENAI_API_KEY="sk-your-key-here"
```

## Step 3: Verify Setup

### Option 1: Use the Validation Script
```bash
python tests/test_api_key_validation.py
```

### Option 2: Quick Python Test
```python
import os

# Check Anthropic key
anth_key = os.getenv('ANTHROPIC_API_KEY')
if anth_key:
    print(f"[OK] Anthropic key found: {anth_key[:15]}...")
else:
    print("[MISSING] ANTHROPIC_API_KEY not set")

# Check OpenAI key
openai_key = os.getenv('OPENAI_API_KEY')
if openai_key:
    print(f"[OK] OpenAI key found: {openai_key[:15]}...")
else:
    print("[INFO] OPENAI_API_KEY not set (optional)")
```

## Step 4: Alternative - Use config.env File

You can also set API keys in the `config.env` file:

```env
# Anthropic API Configuration (required)
ANTHROPIC_API_KEY=sk-ant-your-key-here
ANTHROPIC_MODEL=claude-3-opus-20240229

# OpenAI API Configuration (optional)
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4-vision-preview
```

**Note:** Environment variables take priority over config file values.

## Key Format Validation

### Anthropic Keys
- Must start with `sk-ant-`
- Typically 40-60 characters long
- Format: `sk-ant-api03-...`

### OpenAI Keys
- Must start with `sk-`
- Typically 50+ characters long
- Format: `sk-...`

## Troubleshooting

### Key Not Found
- Verify the environment variable is set: `echo $env:ANTHROPIC_API_KEY` (PowerShell)
- Check if you're in the correct terminal session
- Restart your terminal/IDE after setting variables

### Invalid Key Format
- Ensure the key starts with the correct prefix
- Check for extra spaces or quotes
- Verify you copied the entire key

### Key Not Working
- Verify the key is active in the provider's dashboard
- Check your API usage limits
- Ensure you have sufficient credits/quota

## Security Best Practices

1. **Never commit API keys to git**
   - Add `config.env` to `.gitignore`
   - Use environment variables in production

2. **Use different keys for development/production**
   - Keep production keys secure
   - Rotate keys regularly

3. **Limit key permissions**
   - Use read-only keys when possible
   - Set usage limits in provider dashboard

## Next Steps

After setting up API keys:
1. Run `python tests/test_api_key_validation.py` to verify
2. Test with: `python test_mvp.py`
3. Start using UX-MIRROR: `python ux_mirror_launcher.py`

## Support

For issues with:
- **Anthropic API**: https://docs.anthropic.com/
- **OpenAI API**: https://platform.openai.com/docs/
- **UX-MIRROR**: Check `docs/USAGE_GUIDE_v0.1.0.md`

