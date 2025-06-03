#!/usr/bin/env python3
"""
Screenshot-Enabled 3D Game of Life Demo
======================================

This version automatically captures screenshots to provide visual feedback
of what's actually happening on screen. Perfect example of UX-Mirror functionality.

Features:
- Auto-screenshot every N generations
- Manual screenshot on keypress
- Screenshot analysis and feedback
- Visual debugging information

Author: UX-Mirror System
"""

import numpy as np
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import time
import os
from datetime import datetime
import PIL.Image

class ScreenshotGame3D:
    def __init__(self, size=10):
        self.size = size
        self.grid = np.random.choice([0, 1], size=(size, size, size), p=[0.7, 0.3])
        self.next_grid = np.zeros_like(self.grid)
        
        # Visualization parameters
        self.rotation_x = 20
        self.rotation_y = 45
        self.zoom = -25
        self.paused = False
        self.frame_count = 0
        
        # Timing
        self.last_update = time.time()
        self.update_interval = 1.0  # Slower for better screenshots
        
        # Screenshot settings
        self.screenshot_dir = "game_screenshots"
        self.auto_screenshot_interval = 5  # Every 5 generations
        self.last_screenshot_gen = 0
        
        # Display size for screenshots
        self.display_size = (800, 600)
        
        # Statistics
        self.living_cells = 0
        self.peak_population = 0
        
        # Ensure screenshot directory exists
        os.makedirs(self.screenshot_dir, exist_ok=True)
        
        print(f"Screenshots will be saved to: {os.path.abspath(self.screenshot_dir)}")
        
    def count_neighbors(self, x, y, z):
        """Count living neighbors in 3D"""
        count = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                for dz in [-1, 0, 1]:
                    if dx == 0 and dy == 0 and dz == 0:
                        continue
                    
                    nx, ny, nz = x + dx, y + dy, z + dz
                    nx = nx % self.size
                    ny = ny % self.size
                    nz = nz % self.size
                    
                    count += self.grid[nx, ny, nz]
        return count
    
    def update(self):
        """Update the game state"""
        if self.paused:
            return
            
        current_time = time.time()
        if current_time - self.last_update < self.update_interval:
            return
            
        self.last_update = current_time
        
        # Apply 3D Conway's rules
        for x in range(self.size):
            for y in range(self.size):
                for z in range(self.size):
                    neighbors = self.count_neighbors(x, y, z)
                    
                    if self.grid[x, y, z] == 1:  # Alive
                        if 4 <= neighbors <= 6:
                            self.next_grid[x, y, z] = 1
                        else:
                            self.next_grid[x, y, z] = 0
                    else:  # Dead
                        if neighbors == 5:
                            self.next_grid[x, y, z] = 1
                        else:
                            self.next_grid[x, y, z] = 0
        
        # Swap grids
        self.grid, self.next_grid = self.next_grid, self.grid
        self.frame_count += 1
        self.update_statistics()
    
    def update_statistics(self):
        """Update population statistics"""
        self.living_cells = np.sum(self.grid)
        if self.living_cells > self.peak_population:
            self.peak_population = self.living_cells
    
    def take_screenshot(self, filename=None):
        """Capture screenshot of the current frame"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"game_of_life_gen_{self.frame_count:03d}_{timestamp}.png"
        
        filepath = os.path.join(self.screenshot_dir, filename)
        
        try:
            # Read pixels from the framebuffer
            glPixelStorei(GL_PACK_ALIGNMENT, 1)
            data = glReadPixels(0, 0, self.display_size[0], self.display_size[1], 
                              GL_RGB, GL_UNSIGNED_BYTE)
            
            # Convert to PIL image and flip vertically (OpenGL is upside down)
            image = PIL.Image.frombytes("RGB", self.display_size, data)
            image = image.transpose(PIL.Image.FLIP_TOP_BOTTOM)
            
            # Save image
            image.save(filepath)
            
            print(f"Screenshot saved: {filename}")
            print(f"  Generation: {self.frame_count}")
            print(f"  Population: {self.living_cells}")
            print(f"  Peak: {self.peak_population}")
            
            return filepath
            
        except Exception as e:
            print(f"Failed to take screenshot: {e}")
            return None
    
    def should_auto_screenshot(self):
        """Check if we should take an automatic screenshot"""
        return (self.frame_count > 0 and 
                self.frame_count % self.auto_screenshot_interval == 0 and
                self.frame_count != self.last_screenshot_gen)
    
    def draw(self):
        """Render the 3D grid with enhanced visual feedback"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        # Set up camera
        glTranslatef(0, 0, self.zoom)
        glRotatef(self.rotation_x, 1, 0, 0)
        glRotatef(self.rotation_y, 0, 1, 0)
        
        # Center the grid
        offset = self.size / 2.0
        glTranslatef(-offset, -offset, -offset)
        
        # Draw living cells
        cube_size = 0.7
        for x in range(self.size):
            for y in range(self.size):
                for z in range(self.size):
                    if self.grid[x, y, z] == 1:
                        # Color based on position for visual variety
                        r = 0.3 + 0.7 * (x / self.size)
                        g = 0.3 + 0.7 * (y / self.size)
                        b = 0.3 + 0.7 * (z / self.size)
                        glColor3f(r, g, b)
                        
                        glPushMatrix()
                        glTranslatef(x, y, z)
                        self.draw_cube(cube_size)
                        glPopMatrix()
        
        # Draw coordinate axes for reference
        self.draw_axes()
        
        # Draw boundary wireframe
        self.draw_boundary()
        
        pygame.display.flip()
        
        # Auto-screenshot check
        if self.should_auto_screenshot():
            self.take_screenshot()
            self.last_screenshot_gen = self.frame_count
    
    def draw_cube(self, size):
        """Draw a cube"""
        s = size / 2
        glBegin(GL_QUADS)
        
        # All 6 faces of the cube
        faces = [
            # Front face
            [(-s, -s, s), (s, -s, s), (s, s, s), (-s, s, s)],
            # Back face  
            [(-s, -s, -s), (-s, s, -s), (s, s, -s), (s, -s, -s)],
            # Top face
            [(-s, s, -s), (-s, s, s), (s, s, s), (s, s, -s)],
            # Bottom face
            [(-s, -s, -s), (s, -s, -s), (s, -s, s), (-s, -s, s)],
            # Right face
            [(s, -s, -s), (s, s, -s), (s, s, s), (s, -s, s)],
            # Left face
            [(-s, -s, -s), (-s, -s, s), (-s, s, s), (-s, s, -s)]
        ]
        
        for face in faces:
            for vertex in face:
                glVertex3f(*vertex)
        
        glEnd()
    
    def draw_axes(self):
        """Draw coordinate axes"""
        glBegin(GL_LINES)
        
        # X-axis (red)
        glColor3f(1.0, 0.0, 0.0)
        glVertex3f(0, 0, 0)
        glVertex3f(self.size + 2, 0, 0)
        
        # Y-axis (green)
        glColor3f(0.0, 1.0, 0.0)
        glVertex3f(0, 0, 0)
        glVertex3f(0, self.size + 2, 0)
        
        # Z-axis (blue)
        glColor3f(0.0, 0.0, 1.0)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0, self.size + 2)
        
        glEnd()
    
    def draw_boundary(self):
        """Draw boundary wireframe"""
        glColor3f(0.5, 0.5, 0.5)
        glBegin(GL_LINES)
        
        size = self.size
        # Draw wireframe cube
        edges = [
            [(0, 0, 0), (size, 0, 0)], [(size, 0, 0), (size, size, 0)],
            [(size, size, 0), (0, size, 0)], [(0, size, 0), (0, 0, 0)],
            [(0, 0, size), (size, 0, size)], [(size, 0, size), (size, size, size)],
            [(size, size, size), (0, size, size)], [(0, size, size), (0, 0, size)],
            [(0, 0, 0), (0, 0, size)], [(size, 0, 0), (size, 0, size)],
            [(size, size, 0), (size, size, size)], [(0, size, 0), (0, size, size)]
        ]
        
        for edge in edges:
            glVertex3f(*edge[0])
            glVertex3f(*edge[1])
        
        glEnd()
    
    def reset_with_pattern(self, pattern_name="random"):
        """Reset with different patterns"""
        if pattern_name == "random":
            self.grid = np.random.choice([0, 1], size=(self.size, self.size, self.size), p=[0.7, 0.3])
        elif pattern_name == "cross":
            self.grid.fill(0)
            center = self.size // 2
            for i in range(self.size):
                self.grid[center, center, i] = 1
                self.grid[center, i, center] = 1
                self.grid[i, center, center] = 1
        elif pattern_name == "corner":
            self.grid.fill(0)
            # Create patterns in corners
            for i in range(3):
                for j in range(3):
                    for k in range(3):
                        self.grid[i, j, k] = 1
                        self.grid[self.size-1-i, self.size-1-j, self.size-1-k] = 1
        
        self.frame_count = 0
        self.update_statistics()
        self.take_screenshot(f"reset_{pattern_name}_{datetime.now().strftime('%H%M%S')}.png")

def main():
    """Main game loop with screenshot functionality"""
    try:
        import PIL.Image
    except ImportError:
        print("PIL (Pillow) is required for screenshots. Installing...")
        os.system("pip install Pillow")
        import PIL.Image
    
    pygame.init()
    display = (800, 600)
    screen = pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Screenshot 3D Game of Life - UX-Mirror Demo")
    
    # OpenGL settings
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.1, 0.1, 0.2, 1.0)  # Dark background for better contrast
    
    # Set up perspective
    gluPerspective(45, (display[0]/display[1]), 0.1, 100.0)
    
    # Create game instance
    game = ScreenshotGame3D(size=8)  # Smaller for clearer screenshots
    
    # Mouse control
    mouse_down = False
    last_mouse_pos = (0, 0)
    
    clock = pygame.time.Clock()
    
    print("\n" + "="*60)
    print("Screenshot-Enabled 3D Game of Life Demo")
    print("="*60)
    print("This version provides visual feedback through screenshots!")
    print("\nControls:")
    print("  Mouse drag: Rotate view")
    print("  Mouse wheel: Zoom")
    print("  SPACE: Pause/Resume")
    print("  S: Manual screenshot")
    print("  R: Reset with random pattern")
    print("  C: Reset with cross pattern")  
    print("  N: Reset with corner pattern")
    print("  Q/ESC: Quit")
    print(f"\nAuto-screenshots every {game.auto_screenshot_interval} generations")
    print(f"Generation: {game.frame_count}, Population: {game.living_cells}")
    print("="*60)
    
    # Take initial screenshot
    game.take_screenshot("initial_state.png")
    
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                    running = False
                elif event.key == pygame.K_SPACE:
                    game.paused = not game.paused
                    print(f"{'Paused' if game.paused else 'Resumed'}")
                elif event.key == pygame.K_s:
                    game.take_screenshot()
                elif event.key == pygame.K_r:
                    game.reset_with_pattern("random")
                    print("Reset with random pattern")
                elif event.key == pygame.K_c:
                    game.reset_with_pattern("cross")
                    print("Reset with cross pattern")
                elif event.key == pygame.K_n:
                    game.reset_with_pattern("corner")
                    print("Reset with corner pattern")
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_down = True
                    last_mouse_pos = pygame.mouse.get_pos()
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    mouse_down = False
            elif event.type == pygame.MOUSEMOTION:
                if mouse_down:
                    x, y = pygame.mouse.get_pos()
                    dx = x - last_mouse_pos[0]
                    dy = y - last_mouse_pos[1]
                    game.rotation_y += dx * 0.5
                    game.rotation_x += dy * 0.5
                    last_mouse_pos = (x, y)
            elif event.type == pygame.MOUSEWHEEL:
                game.zoom += event.y * 2
                game.zoom = max(-80, min(-5, game.zoom))
        
        # Update and draw
        old_frame_count = game.frame_count
        game.update()
        
        if game.frame_count != old_frame_count:
            print(f"Gen: {game.frame_count:3d}, Pop: {game.living_cells:3d}, Peak: {game.peak_population:3d}")
        
        game.draw()
        clock.tick(60)
    
    # Take final screenshot
    game.take_screenshot("final_state.png")
    print(f"\nDemo completed! Check {os.path.abspath(game.screenshot_dir)} for screenshots.")
    pygame.quit()

if __name__ == "__main__":
    try:
        main()
    except ImportError as e:
        print("Missing required libraries. Please install with:")
        print("pip install numpy pygame PyOpenGL PyOpenGL_accelerate Pillow")
        print(f"Error: {e}")
    except Exception as e:
        print(f"Error running demo: {e}")
        import traceback
        traceback.print_exc() 