#!/usr/bin/env python3
"""
Script to remove legacy directories.
Run this when file locks are released.
"""

import os
import shutil
import time
from pathlib import Path

def remove_directory(path: str, max_attempts: int = 5):
    """Attempt to remove a directory with retries."""
    if not os.path.exists(path):
        print(f"[OK] {path} does not exist")
        return True
    
    for attempt in range(max_attempts):
        try:
            # Try to remove
            shutil.rmtree(path, ignore_errors=False)
            if not os.path.exists(path):
                print(f"[OK] Successfully removed {path}")
                return True
        except PermissionError as e:
            print(f"[!] Attempt {attempt + 1}/{max_attempts}: Permission denied for {path}")
            if attempt < max_attempts - 1:
                time.sleep(2)
        except Exception as e:
            print(f"[ERROR] Error removing {path}: {e}")
            return False
    
    print(f"[FAILED] Failed to remove {path} after {max_attempts} attempts")
    print(f"  Please close any processes using files in {path} and try again")
    return False

if __name__ == '__main__':
    print("Cleaning up legacy directories...\n")
    
    directories = ['legacy', 'agents']
    
    for directory in directories:
        remove_directory(directory)
        print()
    
    print("Cleanup complete!")
