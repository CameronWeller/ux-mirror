# 🔒 UX-MIRROR Secure Configuration Guide

## Overview
UX-MIRROR now includes a comprehensive secure configuration system that safely stores API keys and settings using industry-standard security practices.

## 🛡️ Security Features

### **Multi-Layer Security Approach**
1. **Primary**: OS Credential Store (Windows Credential Manager)
2. **Fallback**: Encrypted configuration file with machine-specific keys
3. **Never**: Plain text storage

### **Security Levels**
- **High**: Using OS credential store (keyring available)
- **Medium**: Using encrypted config file (cryptography available)  
- **Low**: Basic encoding only (if no security libraries available)

## 🔑 API Key Management

### **Accessing Settings**
1. Launch UX-MIRROR: `python ux_mirror_launcher.py`
2. Click **⚙️ Settings** button in the top-right
3. Navigate to **🔑 API Keys** tab

### **Adding Anthropic API Key**
1. Get your API key from [Anthropic Console](https://console.anthropic.com/)
2. In the settings dialog, paste your key in the "API Key" field
3. Click **Save Key** button
4. Key is automatically stored securely (masked display shows last 8 characters)

### **Security Status Display**
The settings show your current security configuration:
- **Storage Method**: Where keys are stored
- **Security Level**: High/Medium/Low based on available security features
- **Current Key**: Shows masked version of stored key

## 🔧 Configuration Options

### **Analysis Settings**
- **Maximum Iterations**: Limit analysis rounds per session (default: 15)
- **Screenshot Interval**: Seconds between captures (default: 3)
- **Detailed Logging**: Enable verbose output (default: true)
- **Auto-Save Screenshots**: Keep screenshots for review (default: false)

### **Applying Settings**
- Click **Save Settings** in the Analysis tab
- Settings are immediately applied to new analysis sessions
- No restart required

## 🔐 Technical Security Details

### **Encryption Method**
```python
# Machine-specific key generation
machine_id = f"{platform.node()}-{platform.machine()}-{getpass.getuser()}"
key_material = hashlib.pbkdf2_hmac('sha256', machine_id.encode(), 
                                   b'ux-mirror-salt-2024', 100000)
```

### **Storage Hierarchy**
1. **Windows Credential Manager** (if available)
   - Most secure option
   - Integrated with Windows security
   - Requires user authentication to access

2. **Encrypted Config File** (fallback)
   - Machine-specific encryption
   - PBKDF2 key derivation (100,000 iterations)
   - Fernet symmetric encryption

3. **Environment Variables** (final fallback)
   - `ANTHROPIC_API_KEY` environment variable
   - Only used if no stored key found

### **File Locations**
- **Config Directory**: `~/.ux_mirror/`
- **Config File**: `~/.ux_mirror/config.json`
- **Keyring**: System credential store

## 🚀 Quick Start

### **1. Install Security Dependencies**
```bash
pip install -r requirements_security.txt
```

### **2. Configure API Key**
```bash
# Launch UX-MIRROR
python ux_mirror_launcher.py

# Click Settings → API Keys tab
# Paste your Anthropic API key
# Click "Save Key"
```

### **3. Verify Configuration**
```bash
# Test configuration
python test_secure_config.py
```

## 🔧 Advanced Usage

### **Programmatic Access**
```python
from core.secure_config import get_config_manager

config = get_config_manager()

# Store API key
config.set_api_key('anthropic', 'your-api-key-here')

# Retrieve API key
api_key = config.get_api_key('anthropic')

# Store settings
config.set_setting('max_iterations', 20)

# Get settings
max_iter = config.get_setting('max_iterations', 15)
```

### **Security Status Check**
```python
status = config.get_security_status()
print(f"Security Level: {status['security_level']}")
print(f"Storage Method: {status['storage_method']}")
```

## 🛠️ Troubleshooting

### **Common Issues**

#### **"Keyring not available"**
- **Cause**: Missing or non-functional keyring library
- **Solution**: System will use encrypted file storage
- **Impact**: Medium security instead of high

#### **"Encryption failed"**
- **Cause**: Missing cryptography library
- **Solution**: Install with `pip install cryptography`
- **Fallback**: Basic base64 encoding (not secure)

#### **"Failed to save API key"**
- **Cause**: Permissions or disk space issues
- **Solution**: Check file permissions in `~/.ux_mirror/`

### **Security Validation**
```bash
# Check what's stored
python -c "from core.secure_config import get_config_manager; print(get_config_manager().list_stored_keys())"

# Verify encryption
python -c "from core.secure_config import get_config_manager; print(get_config_manager().get_security_status())"
```

## 📋 Security Best Practices

1. **Use Strong API Keys**: Never share or hardcode API keys
2. **Regular Rotation**: Rotate API keys periodically
3. **Monitor Usage**: Check API usage in provider consoles
4. **Secure Environment**: Keep your system updated and secure
5. **Backup Considerations**: API keys in credential store are tied to your user account

## 🔄 Migration from Environment Variables

If you previously used environment variables:
1. Open Settings → API Keys
2. Paste your existing `ANTHROPIC_API_KEY` value
3. Click "Save Key"
4. Remove the environment variable
5. UX-MIRROR will now use the secure storage

## 🆘 Support

For issues with secure configuration:
1. Run `python test_secure_config.py` for diagnostics
2. Check the Security tab in Settings for status
3. Verify required dependencies are installed
4. Check file permissions in `~/.ux_mirror/`

---

**⚡ The secure configuration system ensures your API keys are never stored in plain text while providing a seamless user experience for managing UX-MIRROR settings.** 