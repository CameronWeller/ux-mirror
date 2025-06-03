#!/usr/bin/env python3
"""Create a test screenshot for 3D Game of Life implementation"""

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import math

def create_3d_grid_screenshot(width=800, height=600):
    """Create a screenshot of a 3D Game of Life grid"""
    # Create base image with dark background
    img = Image.new('RGB', (width, height), color='#1a1a1a')
    draw = ImageDraw.Draw(img)
    
    # Draw grid parameters
    grid_size = 6  # Increased size for better visibility
    grid_width = 12  # Increased grid size
    grid_height = 12
    grid_depth = 6
    
    # Calculate perspective parameters
    center_x = width // 2
    center_y = height // 2
    perspective_factor = 0.25  # Reduced for better depth perception
    
    # Define complex cell patterns
    live_cells = [
        # Glider pattern
        (2, 2, 2), (3, 2, 2), (4, 2, 2),
        (4, 3, 2), (3, 4, 2),
        
        # Block pattern
        (6, 6, 3), (7, 6, 3),
        (6, 7, 3), (7, 7, 3),
        
        # Blinker pattern
        (2, 8, 4), (3, 8, 4), (4, 8, 4),
        
        # Random 3D structure
        (8, 2, 5), (9, 2, 5), (10, 2, 5),
        (9, 3, 5), (9, 4, 5),
        (8, 4, 5), (10, 4, 5),
    ]
    
    # Draw grid lines with depth effect
    for z in range(grid_depth + 1):
        alpha = 1.0 - (z / grid_depth) * 0.7  # Fade out with depth
        color = f'#{int(51 * alpha):02x}{int(51 * alpha):02x}{int(51 * alpha):02x}'
        
        for x in range(grid_width + 1):
            for y in range(grid_height + 1):
                # Calculate 3D to 2D projection
                screen_x = center_x + (x - grid_width/2) * grid_size
                screen_y = center_y + (y - grid_height/2) * grid_size
                
                # Add perspective effect
                if z > 0:
                    perspective = 1 + (z * perspective_factor)
                    screen_x = center_x + (screen_x - center_x) * perspective
                    screen_y = center_y + (screen_y - center_y) * perspective
                
                # Draw grid point
                draw.ellipse([screen_x-2, screen_y-2, screen_x+2, screen_y+2], 
                           fill=color)
    
    # Draw live cells with depth effect
    for x, y, z in live_cells:
        # Calculate 3D to 2D projection
        screen_x = center_x + (x - grid_width/2) * grid_size
        screen_y = center_y + (y - grid_height/2) * grid_size
        
        # Add perspective effect
        perspective = 1 + (z * perspective_factor)
        screen_x = center_x + (screen_x - center_x) * perspective
        screen_y = center_y + (screen_y - center_y) * perspective
        
        # Calculate cell color based on depth
        alpha = 1.0 - (z / grid_depth) * 0.3  # Subtle depth effect
        color = f'#{int(0 * alpha):02x}{int(255 * alpha):02x}{int(0 * alpha):02x}'
        
        # Draw live cell with glow effect
        cell_size = grid_size * 0.8
        # Glow
        draw.ellipse([
            screen_x - cell_size,
            screen_y - cell_size,
            screen_x + cell_size,
            screen_y + cell_size
        ], fill=f'#{int(0 * alpha):02x}{int(255 * alpha):02x}{int(0 * alpha):02x}20')
        # Cell
        draw.ellipse([
            screen_x - cell_size/2,
            screen_y - cell_size/2,
            screen_x + cell_size/2,
            screen_y + cell_size/2
        ], fill=color)
    
    # Add UI elements with proper spacing and contrast
    # Draw title with background
    title_bg = draw.rectangle([width//2 - 120, 10, width//2 + 120, 50], 
                            fill='#2a2a2a', outline='#404040')
    draw.text((width//2 - 100, 15), "3D Game of Life", fill='#ffffff')
    
    # Draw stats panel
    stats_bg = draw.rectangle([20, 20, 200, 120], fill='#2a2a2a', outline='#404040')
    draw.text((30, 30), "Generation: 42", fill='#ffffff')
    draw.text((30, 50), "Live Cells: 15", fill='#ffffff')
    draw.text((30, 70), "FPS: 60", fill='#ffffff')
    draw.text((30, 90), "Speed: 1x", fill='#ffffff')
    
    # Draw control panel with better contrast
    controls_bg = draw.rectangle([20, height - 160, 200, height - 20], 
                               fill='#2a2a2a', outline='#404040')
    controls = [
        ("Space", "Pause/Resume"),
        ("R", "Reset"),
        ("F", "Faster"),
        ("S", "Slower"),
        ("Mouse", "Rotate View"),
        ("Scroll", "Zoom")
    ]
    y_pos = height - 150
    for key, action in controls:
        draw.text((30, y_pos), f"{key}:", fill='#00ff00')
        draw.text((100, y_pos), action, fill='#ffffff')
        y_pos += 20
    
    # Draw pattern info
    pattern_bg = draw.rectangle([width - 220, 20, width - 20, 120], 
                              fill='#2a2a2a', outline='#404040')
    draw.text((width - 210, 30), "Active Patterns:", fill='#ffffff')
    patterns = ["Glider", "Block", "Blinker", "3D Structure"]
    y_pos = 50
    for pattern in patterns:
        draw.text((width - 200, y_pos), f"• {pattern}", fill='#00ff00')
        y_pos += 20
    
    return img

def main():
    """Generate and save the test screenshot"""
    img = create_3d_grid_screenshot()
    img.save('test_game_of_life_screenshot.png')
    print("Created test_game_of_life_screenshot.png")

if __name__ == "__main__":
    main() 