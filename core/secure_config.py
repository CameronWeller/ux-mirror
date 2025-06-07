#!/usr/bin/env python3
"""
Secure Configuration Manager for UX-MIRROR

Handles secure storage of API keys and other sensitive settings using:
1. OS credential store (keyring) - primary method
2. Encrypted config file - fallback method
3. Machine-specific encryption keys
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path
import hashlib
import base64

logger = logging.getLogger(__name__)

class SecureConfigManager:
    """Secure configuration management with encrypted storage"""
    
    def __init__(self, app_name: str = "UX-MIRROR"):
        self.app_name = app_name
        self.config_dir = Path.home() / ".ux_mirror"
        self.config_file = self.config_dir / "config.json"
        self.config_dir.mkdir(exist_ok=True)
        
        # Try to import security libraries
        self.keyring_available = self._check_keyring()
        self.crypto_available = self._check_cryptography()
        
        # Load existing config
        self.config = self._load_config()
        
        logger.info(f"Secure config initialized (keyring: {self.keyring_available}, crypto: {self.crypto_available})")
    
    def _check_keyring(self) -> bool:
        """Check if keyring library is available"""
        try:
            import keyring
            # Test if keyring is functional
            keyring.get_keyring()
            return True
        except (ImportError, Exception) as e:
            logger.warning(f"Keyring not available: {e}")
            return False
    
    def _check_cryptography(self) -> bool:
        """Check if cryptography library is available"""
        try:
            from cryptography.fernet import Fernet
            return True
        except ImportError as e:
            logger.warning(f"Cryptography library not available: {e}")
            return False
    
    def _get_machine_key(self) -> bytes:
        """Generate a machine-specific encryption key"""
        try:
            import platform
            import getpass
            
            # Create a machine-specific identifier
            machine_id = f"{platform.node()}-{platform.machine()}-{getpass.getuser()}"
            
            # Hash it to create a consistent key
            key_material = hashlib.pbkdf2_hmac(
                'sha256',
                machine_id.encode('utf-8'),
                b'ux-mirror-salt-2024',  # Static salt
                100000  # iterations
            )
            
            # Encode for Fernet (32 bytes, base64 encoded)
            from cryptography.fernet import Fernet
            return base64.urlsafe_b64encode(key_material[:32])
            
        except Exception as e:
            logger.error(f"Failed to generate machine key: {e}")
            # Fallback to a default (less secure)
            return base64.urlsafe_b64encode(b'fallback_key_not_secure_123456789')
    
    def _encrypt_data(self, data: str) -> str:
        """Encrypt data using machine-specific key"""
        if not self.crypto_available:
            logger.warning("Encryption not available, storing as base64")
            return base64.b64encode(data.encode()).decode()
        
        try:
            from cryptography.fernet import Fernet
            key = self._get_machine_key()
            cipher = Fernet(key)
            encrypted = cipher.encrypt(data.encode())
            return base64.b64encode(encrypted).decode()
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            return base64.b64encode(data.encode()).decode()  # Fallback to base64
    
    def _decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt data using machine-specific key"""
        if not self.crypto_available:
            try:
                return base64.b64decode(encrypted_data.encode()).decode()
            except:
                return encrypted_data  # Return as-is if decoding fails
        
        try:
            from cryptography.fernet import Fernet
            key = self._get_machine_key()
            cipher = Fernet(key)
            encrypted_bytes = base64.b64decode(encrypted_data.encode())
            decrypted = cipher.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            logger.warning(f"Decryption failed, trying base64: {e}")
            try:
                return base64.b64decode(encrypted_data.encode()).decode()
            except:
                return encrypted_data  # Return as-is if all fails
    
    def set_api_key(self, provider: str, api_key: str) -> bool:
        """Securely store an API key"""
        if not api_key.strip():
            return self.remove_api_key(provider)
        
        key_name = f"{self.app_name}-{provider}-api-key"
        
        # Try keyring first (most secure)
        if self.keyring_available:
            try:
                import keyring
                keyring.set_password(self.app_name, key_name, api_key)
                logger.info(f"API key for {provider} stored in OS credential store")
                
                # Remove from config file if it exists there
                if f"{provider}_api_key_encrypted" in self.config:
                    del self.config[f"{provider}_api_key_encrypted"]
                    self._save_config()
                
                return True
            except Exception as e:
                logger.warning(f"Failed to store in keyring: {e}")
        
        # Fallback to encrypted config file
        try:
            encrypted_key = self._encrypt_data(api_key)
            self.config[f"{provider}_api_key_encrypted"] = encrypted_key
            self._save_config()
            logger.info(f"API key for {provider} stored in encrypted config")
            return True
        except Exception as e:
            logger.error(f"Failed to store API key: {e}")
            return False
    
    def get_api_key(self, provider: str) -> Optional[str]:
        """Retrieve an API key securely"""
        key_name = f"{self.app_name}-{provider}-api-key"
        
        # Try keyring first
        if self.keyring_available:
            try:
                import keyring
                api_key = keyring.get_password(self.app_name, key_name)
                if api_key:
                    return api_key
            except Exception as e:
                logger.warning(f"Failed to retrieve from keyring: {e}")
        
        # Try encrypted config file
        encrypted_key = self.config.get(f"{provider}_api_key_encrypted")
        if encrypted_key:
            try:
                return self._decrypt_data(encrypted_key)
            except Exception as e:
                logger.error(f"Failed to decrypt API key: {e}")
        
        # Try environment variable as final fallback
        env_var = f"{provider.upper()}_API_KEY"
        return os.getenv(env_var)
    
    def remove_api_key(self, provider: str) -> bool:
        """Remove an API key from storage"""
        key_name = f"{self.app_name}-{provider}-api-key"
        success = True
        
        # Remove from keyring
        if self.keyring_available:
            try:
                import keyring
                keyring.delete_password(self.app_name, key_name)
            except Exception as e:
                logger.warning(f"Failed to remove from keyring: {e}")
                success = False
        
        # Remove from config file
        config_key = f"{provider}_api_key_encrypted"
        if config_key in self.config:
            del self.config[config_key]
            self._save_config()
        
        return success
    
    def set_setting(self, key: str, value: Any) -> bool:
        """Store a non-sensitive setting"""
        try:
            self.config[key] = value
            self._save_config()
            return True
        except Exception as e:
            logger.error(f"Failed to save setting {key}: {e}")
            return False
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Retrieve a setting"""
        return self.config.get(key, default)
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if not self.config_file.exists():
            return {}
        
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return {}
    
    def _save_config(self) -> bool:
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            return False
    
    def get_security_status(self) -> Dict[str, Any]:
        """Get information about security capabilities"""
        return {
            'keyring_available': self.keyring_available,
            'encryption_available': self.crypto_available,
            'config_file_exists': self.config_file.exists(),
            'storage_method': 'OS Credential Store' if self.keyring_available else 'Encrypted File',
            'security_level': 'High' if self.keyring_available else 'Medium' if self.crypto_available else 'Low'
        }
    
    def list_stored_keys(self) -> list:
        """List API providers that have stored keys"""
        providers = []
        
        # Check config file for encrypted keys
        for key in self.config.keys():
            if key.endswith('_api_key_encrypted'):
                provider = key.replace('_api_key_encrypted', '')
                providers.append(provider)
        
        # Check keyring (harder to enumerate, so we'll check common providers)
        if self.keyring_available:
            common_providers = ['anthropic', 'openai', 'google']
            import keyring
            for provider in common_providers:
                try:
                    key_name = f"{self.app_name}-{provider}-api-key"
                    if keyring.get_password(self.app_name, key_name):
                        if provider not in providers:
                            providers.append(provider)
                except:
                    pass
        
        return providers

# Global instance
_config_manager = None

def get_config_manager() -> SecureConfigManager:
    """Get the global config manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = SecureConfigManager()
    return _config_manager 