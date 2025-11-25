#!/usr/bin/env python3
"""
Test script for secure configuration system
Tests API key storage, encryption, and OS credential store integration
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from core.secure_config import get_config_manager

def test_secure_config():
    """Test the secure configuration system"""
    print("🔒 Testing UX-MIRROR Secure Configuration System")
    print("=" * 60)
    
    # Get config manager
    config_manager = get_config_manager()
    
    # Test security status
    print("\n1. Security Status:")
    status = config_manager.get_security_status()
    for key, value in status.items():
        print(f"   {key}: {value}")
    
    # Test settings storage
    print("\n2. Testing Settings Storage:")
    test_settings = {
        'max_iterations': 10,
        'screenshot_interval': 2.5,
        'detailed_logging': True,
        'test_string': 'hello world'
    }
    
    for key, value in test_settings.items():
        success = config_manager.set_setting(key, value)
        retrieved = config_manager.get_setting(key)
        print(f"   {key}: Set={success}, Retrieved={retrieved}, Matches={retrieved == value}")
    
    # Test API key storage (with fake key)
    print("\n3. Testing API Key Storage:")
    fake_key = "sk-ant-test-key-1234567890abcdef"
    
    # Store key
    success = config_manager.set_api_key('anthropic', fake_key)
    print(f"   Store API key: {success}")
    
    # Retrieve key
    retrieved_key = config_manager.get_api_key('anthropic')
    print(f"   Retrieved key: {'✅ Match' if retrieved_key == fake_key else '❌ Mismatch'}")
    print(f"   Key preview: {retrieved_key[:20] if retrieved_key else 'None'}...")
    
    # Test key removal
    removed = config_manager.remove_api_key('anthropic')
    after_removal = config_manager.get_api_key('anthropic')
    print(f"   Remove key: {removed}")
    print(f"   After removal: {'✅ None' if not after_removal else '❌ Still exists'}")
    
    # Test environment variable fallback
    print("\n4. Testing Environment Variable Fallback:")
    os.environ['ANTHROPIC_API_KEY'] = 'env-test-key-123'
    env_key = config_manager.get_api_key('anthropic')
    print(f"   Environment fallback: {'✅ Working' if env_key == 'env-test-key-123' else '❌ Not working'}")
    del os.environ['ANTHROPIC_API_KEY']
    
    # Test stored providers list
    print("\n5. Testing Stored Providers:")
    config_manager.set_api_key('anthropic', 'test-key-1')
    config_manager.set_api_key('openai', 'test-key-2')
    providers = config_manager.list_stored_keys()
    print(f"   Stored providers: {providers}")
    
    # Cleanup
    config_manager.remove_api_key('anthropic')
    config_manager.remove_api_key('openai')
    
    print("\n✅ Secure configuration system test complete!")
    print(f"📁 Config location: {config_manager.config_file}")

if __name__ == "__main__":
    test_secure_config() 