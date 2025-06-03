#!/usr/bin/env python3
"""
Simple 3D Game of Life Demo
==========================

A working 3D Conway's Game of Life implementation using Python, NumPy, and OpenGL.
This creates a 3D grid where each cell follows Conway's rules extended to 3D space.

Requirements:
    pip install numpy pygame PyOpenGL PyOpenGL_accelerate

Controls:
    - Mouse: Rotate view
    - Scroll: Zoom in/out
    - SPACE: Pause/Resume
    - R: Reset with random pattern
    - Q/ESC: Quit

Author: UX-Mirror System
"""

import numpy as np
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import time
import random

class Game3D:
    def __init__(self, size=20):
        self.size = size
        self.grid = np.random.choice([0, 1], size=(size, size, size), p=[0.7, 0.3])
        self.next_grid = np.zeros_like(self.grid)
        
        # Visualization parameters
        self.rotation_x = 20
        self.rotation_y = 45
        self.zoom = -50
        self.paused = False
        self.frame_count = 0
        
        # Timing
        self.last_update = time.time()
        self.update_interval = 0.5  # Update every 500ms
        
    def count_neighbors(self, x, y, z):
        """Count living neighbors in 3D (26 neighbors in a 3x3x3 cube)"""
        count = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                for dz in [-1, 0, 1]:
                    if dx == 0 and dy == 0 and dz == 0:
                        continue
                    
                    nx, ny, nz = x + dx, y + dy, z + dz
                    
                    # Periodic boundary conditions (torus topology)
                    nx = nx % self.size
                    ny = ny % self.size
                    nz = nz % self.size
                    
                    count += self.grid[nx, ny, nz]
        return count
    
    def update(self):
        """Update the game state according to 3D Conway's rules"""
        if self.paused:
            return
            
        current_time = time.time()
        if current_time - self.last_update < self.update_interval:
            return
            
        self.last_update = current_time
        
        # Apply Conway's rules adapted for 3D
        for x in range(self.size):
            for y in range(self.size):
                for z in range(self.size):
                    neighbors = self.count_neighbors(x, y, z)
                    
                    # 3D Conway's rules (modified for 3D space)
                    if self.grid[x, y, z] == 1:  # Alive
                        # Survival: 4-7 neighbors (fewer than 2D due to more neighbors)
                        if 4 <= neighbors <= 7:
                            self.next_grid[x, y, z] = 1
                        else:
                            self.next_grid[x, y, z] = 0
                    else:  # Dead
                        # Birth: exactly 6 neighbors
                        if neighbors == 6:
                            self.next_grid[x, y, z] = 1
                        else:
                            self.next_grid[x, y, z] = 0
        
        # Swap grids
        self.grid, self.next_grid = self.next_grid, self.grid
        self.frame_count += 1
    
    def reset_random(self):
        """Reset with a random pattern"""
        self.grid = np.random.choice([0, 1], size=(self.size, self.size, self.size), p=[0.7, 0.3])
        self.frame_count = 0
    
    def draw(self):
        """Render the 3D grid"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        # Set up camera
        glTranslatef(0, 0, self.zoom)
        glRotatef(self.rotation_x, 1, 0, 0)
        glRotatef(self.rotation_y, 0, 1, 0)
        
        # Center the grid
        offset = self.size / 2.0
        glTranslatef(-offset, -offset, -offset)
        
        # Draw living cells as small cubes
        glColor3f(0.2, 0.8, 1.0)  # Light blue
        cube_size = 0.4
        
        for x in range(self.size):
            for y in range(self.size):
                for z in range(self.size):
                    if self.grid[x, y, z] == 1:
                        glPushMatrix()
                        glTranslatef(x, y, z)
                        self.draw_cube(cube_size)
                        glPopMatrix()
        
        # Draw grid lines for reference
        self.draw_grid_lines()
        
        pygame.display.flip()
    
    def draw_cube(self, size):
        """Draw a simple cube"""
        s = size / 2
        glBegin(GL_QUADS)
        
        # Front face
        glVertex3f(-s, -s, s)
        glVertex3f(s, -s, s)
        glVertex3f(s, s, s)
        glVertex3f(-s, s, s)
        
        # Back face
        glVertex3f(-s, -s, -s)
        glVertex3f(-s, s, -s)
        glVertex3f(s, s, -s)
        glVertex3f(s, -s, -s)
        
        # Top face
        glVertex3f(-s, s, -s)
        glVertex3f(-s, s, s)
        glVertex3f(s, s, s)
        glVertex3f(s, s, -s)
        
        # Bottom face
        glVertex3f(-s, -s, -s)
        glVertex3f(s, -s, -s)
        glVertex3f(s, -s, s)
        glVertex3f(-s, -s, s)
        
        # Right face
        glVertex3f(s, -s, -s)
        glVertex3f(s, s, -s)
        glVertex3f(s, s, s)
        glVertex3f(s, -s, s)
        
        # Left face
        glVertex3f(-s, -s, -s)
        glVertex3f(-s, -s, s)
        glVertex3f(-s, s, s)
        glVertex3f(-s, s, -s)
        
        glEnd()
    
    def draw_grid_lines(self):
        """Draw reference grid lines"""
        glColor3f(0.3, 0.3, 0.3)  # Dark gray
        glBegin(GL_LINES)
        
        # Draw some reference lines
        for i in range(0, self.size, 5):
            # X-axis lines
            glVertex3f(i, 0, 0)
            glVertex3f(i, self.size, 0)
            glVertex3f(i, 0, 0)
            glVertex3f(i, 0, self.size)
            
            # Y-axis lines
            glVertex3f(0, i, 0)
            glVertex3f(self.size, i, 0)
            glVertex3f(0, i, 0)
            glVertex3f(0, i, self.size)
            
            # Z-axis lines
            glVertex3f(0, 0, i)
            glVertex3f(self.size, 0, i)
            glVertex3f(0, 0, i)
            glVertex3f(0, self.size, i)
        
        glEnd()

def main():
    """Main game loop"""
    # Initialize Pygame and OpenGL
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("3D Game of Life - UX-Mirror Demo")
    
    # OpenGL settings
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.1, 0.1, 0.2, 1.0)  # Dark blue background
    
    # Set up perspective
    gluPerspective(45, (display[0]/display[1]), 0.1, 100.0)
    
    # Create game instance
    game = Game3D(size=15)  # Smaller size for better performance
    
    # Mouse control variables
    mouse_down = False
    last_mouse_pos = (0, 0)
    
    clock = pygame.time.Clock()
    
    print("3D Game of Life Demo")
    print("Controls:")
    print("  Mouse drag: Rotate view")
    print("  Mouse wheel: Zoom")
    print("  SPACE: Pause/Resume")
    print("  R: Reset with random pattern")
    print("  Q/ESC: Quit")
    print(f"Generation: {game.frame_count}")
    
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
                elif event.key == pygame.K_r:
                    game.reset_random()
                    print("Reset with random pattern")
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
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
                game.zoom = max(-100, min(-10, game.zoom))  # Clamp zoom
        
        # Update and draw
        old_frame_count = game.frame_count
        game.update()
        
        if game.frame_count != old_frame_count:
            print(f"Generation: {game.frame_count}")
        
        game.draw()
        clock.tick(60)  # 60 FPS
    
    pygame.quit()

if __name__ == "__main__":
    try:
        main()
    except ImportError as e:
        print("Missing required libraries. Please install with:")
        print("pip install numpy pygame PyOpenGL PyOpenGL_accelerate")
        print(f"Error: {e}")
    except Exception as e:
        print(f"Error running demo: {e}")
        import traceback
        traceback.print_exc() 