#!/usr/bin/env python3

import os
import subprocess
import sys

def find_glslc():
    # Try to find glslc in PATH
    if sys.platform == "win32":
        # On Windows, try to find glslc in the Vulkan SDK
        vulkan_sdk = os.environ.get("VULKAN_SDK")
        if vulkan_sdk:
            glslc_path = os.path.join(vulkan_sdk, "Bin", "glslc.exe")
            if os.path.exists(glslc_path):
                return glslc_path
    
    # Try to find glslc in PATH
    try:
        subprocess.run(["glslc", "--version"], capture_output=True, check=True)
        return "glslc"
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
    
    return None

def compile_shader(glslc_path, input_file, output_file):
    try:
        subprocess.run([glslc_path, input_file, "-o", output_file], check=True)
        print(f"Compiled {input_file} to {output_file}")
    except subprocess.SubprocessError as e:
        print(f"Error compiling {input_file}: {e}")
        sys.exit(1)

def main():
    glslc_path = find_glslc()
    if not glslc_path:
        print("Error: Could not find glslc. Make sure it's installed and in your PATH.")
        sys.exit(1)
    
    # Create shaders directory if it doesn't exist
    os.makedirs("shaders", exist_ok=True)
    
    # Compile compute shader
    compile_shader(
        glslc_path,
        "shaders/game_of_life_3d.comp",
        "shaders/game_of_life_3d.comp.spv"
    )

if __name__ == "__main__":
    main() 