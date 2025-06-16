#!/usr/bin/env python3
"""
Launch script for testing 3D Game of Life with UX Mirror
This script configures the UX mirror system to test the 3D Game of Life application
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def main():
    # Set up the configuration for 3D Game of Life testing
    config = {
        "session_name": "3D_Game_of_Life_Testing",
        "target_executable": "rotating_cube.exe",  # Will use this once compiled
        "fallback_executable": "ux_test_game.exe",  # Use this for now
        "session_duration": 300,  # 5 minutes for testing
        "capture_interval": 5,
        "analysis_config": {
            "focus_areas": [
                "3D rendering performance",
                "User interaction responsiveness",
                "Visual clarity and aesthetics",
                "UI element accessibility"
            ],
            "metrics": {
                "fps_target": 60,
                "response_time_max_ms": 100,
                "visual_quality_min": 0.8
            }
        }
    }
    
    # Check if the rotating cube executable exists
    target_exe = Path(config["target_executable"])
    if not target_exe.exists():
        print(f"Target executable '{config['target_executable']}' not found.")
        print(f"Using fallback: '{config['fallback_executable']}'")
        config["target_executable"] = config["fallback_executable"]
    
    # Check if the fallback exists
    exe_path = Path(config["target_executable"])
    if not exe_path.exists():
        print(f"Error: No executable found at '{exe_path}'")
        print("Please ensure you have a test application available.")
        return 1
    
    # Set environment variable for the autonomous launcher
    os.environ['UX_MIRROR_TARGET_GAME'] = str(exe_path.absolute())
    
    # Load the Vulkan Game of Life configuration
    vulkan_config_path = Path("vulkan_gameoflife_ux_config.json")
    if vulkan_config_path.exists():
        with open(vulkan_config_path, 'r') as f:
            vulkan_config = json.load(f)
            print("Loaded Vulkan Game of Life UX configuration")
            config.update(vulkan_config.get("vulkan_3d_gameoflife_testing", {}))
    
    # Write the combined configuration
    config_path = Path("current_test_config.json")
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"Configuration saved to: {config_path}")
    print(f"Target executable: {exe_path.absolute()}")
    print(f"Session duration: {config.get('session_config', {}).get('session_duration', 300)} seconds")
    
    # Launch the autonomous testing system
    launcher_script = Path("autonomous_launcher.py")
    if launcher_script.exists():
        print("\nLaunching UX Mirror autonomous testing system...")
        try:
            # Use the existing autonomous launcher with our configuration
            result = subprocess.run(
                [sys.executable, str(launcher_script)],
                env=os.environ.copy()
            )
            return result.returncode
        except Exception as e:
            print(f"Error launching autonomous system: {e}")
            return 1
    else:
        print(f"Error: Autonomous launcher not found at '{launcher_script}'")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 