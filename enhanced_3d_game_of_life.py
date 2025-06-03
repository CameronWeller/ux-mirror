#!/usr/bin/env python3
"""
Enhanced 3D Game of Life Demo
============================

An improved 3D Conway's Game of Life with better visualization and patterns.

New Features:
- Multiple color schemes
- Better initial patterns
- Generation statistics
- Performance monitoring
- Multiple rule sets

Author: UX-Mirror System
"""

import numpy as np
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import time
import random

class Enhanced3DGame:
    def __init__(self, size=12):
        self.size = size
        self.grid = np.zeros((size, size, size), dtype=np.int8)
        self.next_grid = np.zeros_like(self.grid)
        
        # Visualization parameters
        self.rotation_x = 20
        self.rotation_y = 45
        self.zoom = -30
        self.paused = False
        self.frame_count = 0
        
        # Timing and performance
        self.last_update = time.time()
        self.update_interval = 0.3  # Faster updates
        self.fps_history = []
        
        # Statistics
        self.living_cells = 0
        self.peak_population = 0
        
        # Color schemes
        self.color_schemes = {
            'blue': [(0.2, 0.8, 1.0), (0.1, 0.4, 0.8)],
            'fire': [(1.0, 0.4, 0.1), (1.0, 0.8, 0.2)],
            'green': [(0.2, 1.0, 0.3), (0.1, 0.7, 0.2)],
            'purple': [(0.8, 0.2, 1.0), (0.6, 0.1, 0.8)]
        }
        self.current_color_scheme = 'blue'
        
        # Initialize with interesting pattern
        self.set_glider_pattern()
    
    def set_glider_pattern(self):
        """Set up an interesting 3D glider-like pattern"""
        self.grid.fill(0)
        center = self.size // 2
        
        # Create a 3D glider pattern
        pattern = [
            (0, 0, 0), (1, 0, 0), (2, 0, 0),
            (0, 1, 0), (1, 1, 1), (2, 1, 0),
            (1, 0, 1), (1, 1, 2), (1, 2, 1)
        ]
        
        for dx, dy, dz in pattern:
            x, y, z = center + dx - 1, center + dy - 1, center + dz - 1
            if 0 <= x < self.size and 0 <= y < self.size and 0 <= z < self.size:
                self.grid[x, y, z] = 1
        
        self.frame_count = 0
        self.update_statistics()
    
    def set_random_pattern(self, density=0.3):
        """Set a random pattern with specified density"""
        self.grid = np.random.choice([0, 1], size=(self.size, self.size, self.size), 
                                   p=[1-density, density])
        self.frame_count = 0
        self.update_statistics()
    
    def set_cross_pattern(self):
        """Create a 3D cross pattern"""
        self.grid.fill(0)
        center = self.size // 2
        
        # Create 3D cross
        for i in range(self.size):
            self.grid[center, center, i] = 1  # Z-axis
            self.grid[center, i, center] = 1  # Y-axis
            self.grid[i, center, center] = 1  # X-axis
        
        self.frame_count = 0
        self.update_statistics()
    
    def count_neighbors(self, x, y, z):
        """Count living neighbors in 3D (26 neighbors)"""
        count = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                for dz in [-1, 0, 1]:
                    if dx == 0 and dy == 0 and dz == 0:
                        continue
                    
                    nx, ny, nz = x + dx, y + dy, z + dz
                    
                    # Periodic boundary conditions
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
                    
                    # 3D rules - adjusted for better dynamics
                    if self.grid[x, y, z] == 1:  # Alive
                        # Survival: 4-6 neighbors
                        if 4 <= neighbors <= 6:
                            self.next_grid[x, y, z] = 1
                        else:
                            self.next_grid[x, y, z] = 0
                    else:  # Dead
                        # Birth: exactly 5 neighbors
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
    
    def cycle_color_scheme(self):
        """Cycle through color schemes"""
        schemes = list(self.color_schemes.keys())
        current_index = schemes.index(self.current_color_scheme)
        self.current_color_scheme = schemes[(current_index + 1) % len(schemes)]
    
    def draw(self):
        """Enhanced rendering with colors and effects"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        # Set up camera
        glTranslatef(0, 0, self.zoom)
        glRotatef(self.rotation_x, 1, 0, 0)
        glRotatef(self.rotation_y, 0, 1, 0)
        
        # Center the grid
        offset = self.size / 2.0
        glTranslatef(-offset, -offset, -offset)
        
        # Draw living cells with current color scheme
        colors = self.color_schemes[self.current_color_scheme]
        
        cube_size = 0.8
        for x in range(self.size):
            for y in range(self.size):
                for z in range(self.size):
                    if self.grid[x, y, z] == 1:
                        # Color variation based on position
                        t = (x + y + z) / (3 * self.size)
                        color = [
                            colors[0][i] * (1 - t) + colors[1][i] * t
                            for i in range(3)
                        ]
                        glColor3f(*color)
                        
                        glPushMatrix()
                        glTranslatef(x, y, z)
                        self.draw_cube(cube_size)
                        glPopMatrix()
        
        # Draw wireframe boundary
        self.draw_boundary()
        
        pygame.display.flip()
    
    def draw_cube(self, size):
        """Draw a cube with slight transparency effect"""
        s = size / 2
        glBegin(GL_QUADS)
        
        # All 6 faces
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
    
    def draw_boundary(self):
        """Draw boundary wireframe"""
        glColor3f(0.5, 0.5, 0.5)
        glBegin(GL_LINES)
        
        # Draw cube edges
        size = self.size
        edges = [
            # Bottom face edges
            [(0, 0, 0), (size, 0, 0)],
            [(size, 0, 0), (size, size, 0)],
            [(size, size, 0), (0, size, 0)],
            [(0, size, 0), (0, 0, 0)],
            # Top face edges
            [(0, 0, size), (size, 0, size)],
            [(size, 0, size), (size, size, size)],
            [(size, size, size), (0, size, size)],
            [(0, size, size), (0, 0, size)],
            # Vertical edges
            [(0, 0, 0), (0, 0, size)],
            [(size, 0, 0), (size, 0, size)],
            [(size, size, 0), (size, size, size)],
            [(0, size, 0), (0, size, size)]
        ]
        
        for edge in edges:
            glVertex3f(*edge[0])
            glVertex3f(*edge[1])
        
        glEnd()

def main():
    """Enhanced main game loop"""
    pygame.init()
    display = (1000, 700)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Enhanced 3D Game of Life - UX-Mirror Demo")
    
    # OpenGL settings
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.05, 0.05, 0.15, 1.0)  # Dark blue background
    
    # Set up perspective
    gluPerspective(45, (display[0]/display[1]), 0.1, 100.0)
    
    # Create enhanced game instance
    game = Enhanced3DGame(size=10)
    
    # Mouse control variables
    mouse_down = False
    last_mouse_pos = (0, 0)
    
    clock = pygame.time.Clock()
    
    print("Enhanced 3D Game of Life Demo")
    print("Controls:")
    print("  Mouse drag: Rotate view")
    print("  Mouse wheel: Zoom")
    print("  SPACE: Pause/Resume")
    print("  R: Random pattern")
    print("  G: Glider pattern")
    print("  C: Cross pattern")
    print("  X: Change colors")
    print("  Q/ESC: Quit")
    print(f"Generation: {game.frame_count}, Population: {game.living_cells}")
    
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
                    game.set_random_pattern()
                    print("Random pattern loaded")
                elif event.key == pygame.K_g:
                    game.set_glider_pattern()
                    print("Glider pattern loaded")
                elif event.key == pygame.K_c:
                    game.set_cross_pattern()
                    print("Cross pattern loaded")
                elif event.key == pygame.K_x:
                    game.cycle_color_scheme()
                    print(f"Color scheme: {game.current_color_scheme}")
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
                game.zoom += event.y * 3
                game.zoom = max(-100, min(-5, game.zoom))
        
        # Update and draw
        old_frame_count = game.frame_count
        old_population = game.living_cells
        game.update()
        
        if game.frame_count != old_frame_count:
            print(f"Gen: {game.frame_count:3d}, Pop: {game.living_cells:3d}, Peak: {game.peak_population:3d}")
        
        game.draw()
        clock.tick(60)
    
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