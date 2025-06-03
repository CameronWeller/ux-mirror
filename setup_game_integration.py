#!/usr/bin/env python3
"""
UX Mirror - Game Integration Setup Script
Prepares the environment for Vulkan game UI analysis
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def run_command(cmd, cwd=None):
    """Run a command and return success status"""
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
        if result.returncode != 0:
            logger.error(f"Command failed: {cmd}")
            logger.error(f"Error: {result.stderr}")
            return False
        return True
    except Exception as e:
        logger.error(f"Failed to run command: {e}")
        return False

def setup_game_integration():
    """Setup the game integration environment"""
    
    logger.info("Setting up UX Mirror Game Integration...")
    
    # 1. Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or python_version.minor < 11:
        logger.error("Python 3.11+ is required")
        return False
    
    # 2. Create necessary directories
    directories = ['game-target', 'logs', 'screenshots', 'analysis-results']
    for dir_name in directories:
        Path(dir_name).mkdir(exist_ok=True)
        logger.info(f"Created directory: {dir_name}")
    
    # 3. Clone the 3DGameOfLife project
    game_path = Path("game-target/3DGameOfLife")
    if not game_path.exists():
        logger.info("Cloning 3DGameOfLife-Vulkan-Edition...")
        if not run_command(
            "git clone https://github.com/CameronWeller/3DGameOfLife-Vulkan-Edition.git 3DGameOfLife",
            cwd="game-target"
        ):
            logger.error("Failed to clone game repository")
            return False
        logger.info("Successfully cloned 3DGameOfLife")
    else:
        logger.info("3DGameOfLife already exists, skipping clone")
    
    # 4. Create .env file if it doesn't exist
    env_file = Path(".env")
    if not env_file.exists():
        logger.info("Creating .env configuration file...")
        env_content = """# UX Mirror Configuration

# OpenAI API Configuration
OPENAI_API_KEY=your-openai-api-key-here

# Vulkan Capture Settings
VULKAN_CAPTURE_WIDTH=1920
VULKAN_CAPTURE_HEIGHT=1080
VULKAN_SHARED_MEMORY_NAME=UXMirrorVulkanCapture

# Analysis Settings
ANALYSIS_INTERVAL_SECONDS=3.0
SCREENSHOT_QUALITY=high
LOG_LEVEL=INFO

# Game Integration
GAME_EXECUTABLE_PATH=game-target/3DGameOfLife/build/3DGameOfLife.exe
AUTO_START_GAME=False
"""
        with open(env_file, 'w') as f:
            f.write(env_content)
        logger.info("Created .env file - please update with your API key")
    
    # 5. Install Python dependencies
    logger.info("Installing Python dependencies...")
    
    # Create virtual environment if it doesn't exist
    venv_path = Path("venv")
    if not venv_path.exists():
        logger.info("Creating virtual environment...")
        if not run_command(f"{sys.executable} -m venv venv"):
            logger.error("Failed to create virtual environment")
            return False
    
    # Determine pip path based on OS
    if sys.platform == "win32":
        pip_path = "venv\\Scripts\\pip.exe"
        activate_cmd = "venv\\Scripts\\activate.bat"
    else:
        pip_path = "venv/bin/pip"
        activate_cmd = "source venv/bin/activate"
    
    # Install requirements
    if Path("requirements.txt").exists():
        logger.info("Installing base requirements...")
        if not run_command(f"{pip_path} install -r requirements.txt"):
            logger.warning("Some base requirements failed to install")
    
    if Path("requirements-vm.txt").exists():
        logger.info("Installing VM requirements...")
        if not run_command(f"{pip_path} install -r requirements-vm.txt"):
            logger.warning("Some VM requirements failed to install")
    
    # Install game integration specific packages
    logger.info("Installing game integration packages...")
    game_packages = [
        "pynput",
        "pillow",
        "numpy",
        "aiohttp",
        "python-dotenv",
        "opencv-python"
    ]
    
    for package in game_packages:
        if not run_command(f"{pip_path} install {package}"):
            logger.warning(f"Failed to install {package}")
    
    # 6. Create Vulkan capture configuration
    vulkan_config_dir = Path.home() / ".ux-mirror"
    vulkan_config_dir.mkdir(exist_ok=True)
    
    vulkan_config = {
        "capture_layer": {
            "name": "VK_LAYER_UX_MIRROR_CAPTURE",
            "enabled": True,
            "shared_memory_name": "UXMirrorVulkanCapture",
            "capture_fps": 1
        }
    }
    
    import json
    vulkan_config_file = vulkan_config_dir / "vulkan_capture_config.json"
    with open(vulkan_config_file, 'w') as f:
        json.dump(vulkan_config, f, indent=2)
    logger.info(f"Created Vulkan configuration at {vulkan_config_file}")
    
    # 7. Create example scripts
    create_example_scripts()
    
    logger.info("\n" + "="*60)
    logger.info("Setup Complete!")
    logger.info("="*60)
    logger.info("\nNext steps:")
    logger.info("1. Update the .env file with your OpenAI API key")
    logger.info("2. Build the 3DGameOfLife project (see game-target/3DGameOfLife/README.md)")
    logger.info("3. Run: python run_game_analysis.py")
    logger.info(f"\nActivate virtual environment with: {activate_cmd}")
    
    return True

def create_example_scripts():
    """Create example scripts for running the analysis"""
    
    # Create a simple run script
    run_script = """#!/usr/bin/env python3
\"\"\"
Quick script to run game UI analysis
\"\"\"

import asyncio
import os
from dotenv import load_dotenv
from game_integration_example import GameUIAnalyzer

# Load environment variables
load_dotenv()

async def main():
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key == 'your-openai-api-key-here':
        print("ERROR: Please update your OpenAI API key in .env file")
        return
    
    analyzer = GameUIAnalyzer(openai_api_key=api_key)
    
    print("Starting UX Mirror Game Analysis...")
    print("Make sure 3DGameOfLife is running!")
    
    if await analyzer.start():
        try:
            await analyzer.continuous_analysis(interval_seconds=3.0)
        except KeyboardInterrupt:
            print("\\nStopping analysis...")
        finally:
            analyzer.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
"""
    
    with open("run_game_analysis.py", 'w') as f:
        f.write(run_script)
    
    # Create a test script
    test_script = """#!/usr/bin/env python3
\"\"\"
Test script to verify setup
\"\"\"

import sys
from pathlib import Path

def test_setup():
    errors = []
    
    # Check Python version
    if sys.version_info < (3, 11):
        errors.append("Python 3.11+ required")
    
    # Check directories
    for dir_name in ['game-target', 'logs', 'screenshots']:
        if not Path(dir_name).exists():
            errors.append(f"Missing directory: {dir_name}")
    
    # Check game clone
    if not Path("game-target/3DGameOfLife").exists():
        errors.append("3DGameOfLife not cloned")
    
    # Check .env file
    if not Path(".env").exists():
        errors.append(".env file not found")
    
    # Check imports
    try:
        import pynput
        import PIL
        import numpy
        import cv2
    except ImportError as e:
        errors.append(f"Missing package: {e.name}")
    
    if errors:
        print("Setup issues found:")
        for error in errors:
            print(f"  - {error}")
        return False
    else:
        print("✓ Setup verified successfully!")
        return True

if __name__ == "__main__":
    test_setup()
"""
    
    with open("test_setup.py", 'w') as f:
        f.write(test_script)
    
    logger.info("Created example scripts: run_game_analysis.py, test_setup.py")

if __name__ == "__main__":
    setup_game_integration() 