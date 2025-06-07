#!/bin/bash

echo "Building UX Test Game (C++ Edition)..."

# Check if g++ is available
if ! command -v g++ &> /dev/null; then
    echo "Error: g++ compiler not found. Please install g++."
    echo "Ubuntu/Debian: sudo apt install g++"
    echo "macOS: xcode-select --install"
    exit 1
fi

# Compile the game
echo "Compiling..."
g++ -std=c++17 -O2 -Wall -Wextra \
    -I. \
    test_cpp_game.cpp \
    -o ux_test_game \
    -lX11 -lGL -lpthread -lpng -lstdc++fs

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Build successful!"
    echo "✓ Executable created: ux_test_game"
    echo ""
    echo "Checking Anthropic API key..."
    if [ -z "$ANTHROPIC_API_KEY" ]; then
        echo "⚠ Warning: ANTHROPIC_API_KEY environment variable not set!"
        echo "Please set it with: export ANTHROPIC_API_KEY=your_key_here"
    else
        echo "✓ Anthropic API key found in environment"
    fi
    echo ""
    echo "To run the game: ./ux_test_game"
    echo "To test with UX-MIRROR: python ux_mirror_launcher.py"
    echo ""
else
    echo ""
    echo "✗ Build failed! Check the error messages above."
    echo ""
fi 