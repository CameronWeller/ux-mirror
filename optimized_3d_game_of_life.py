#!/usr/bin/env python3
"""
Optimized 3D Game of Life - Conservative Screenshot Capture
=========================================================

Based on user feedback: reduced screenshot frequency to 1/second, max 10 per session.
This provides sufficient data for analysis without overwhelming the system.

Author: UX-Mirror System (Optimized based on user feedback)
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

class OptimizedGame3D:
    def __init__(self, size=6):
        self.size = size
        self.grid = np.random.choice([0, 1], size=(size, size, size), p=[0.7, 0.3])
        self.next_grid = np.zeros_like(self.grid)
        
        # Visualization parameters - ENHANCED FOR VISIBILITY
        self.rotation_x = 20
        self.rotation_y = 45
        self.zoom = -15  # Closer for better visibility
        self.paused = False
        self.frame_count = 0
        
        # Timing
        self.last_update = time.time()
        self.update_interval = 1.0
        
        # OPTIMIZED Screenshot settings
        self.screenshot_dir = "game_screenshots"
        self.screenshot_interval = 1.0  # 1 screenshot per second
        self.max_screenshots = 10       # Maximum 10 screenshots per session
        self.screenshot_count = 0
        self.last_screenshot_time = 0
        self.display_size = (800, 600)
        
        # Statistics
        self.living_cells = 0
        self.peak_population = 0
        self.session_start_time = time.time()
        
        # Ensure screenshot directory exists
        os.makedirs(self.screenshot_dir, exist_ok=True)
        
        print(f"🎯 OPTIMIZED VERSION - Conservative screenshot capture")
        print(f"📸 Screenshot settings: 1/second, max {self.max_screenshots} per session")
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
    
    def should_take_screenshot(self):
        """Conservative screenshot logic - 1/second, max 10 per session"""
        current_time = time.time()
        
        # Check if we've hit the screenshot limit
        if self.screenshot_count >= self.max_screenshots:
            return False
        
        # Check if enough time has passed (1 second minimum)
        if current_time - self.last_screenshot_time < self.screenshot_interval:
            return False
            
        return True
    
    def take_screenshot(self, filename=None, force=False):
        """Capture screenshot with conservative limits"""
        if not force and not self.should_take_screenshot():
            return None
            
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"opt_game_of_life_gen_{self.frame_count:03d}_{timestamp}.png"
        
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
            
            # Update screenshot tracking
            self.screenshot_count += 1
            self.last_screenshot_time = time.time()
            session_time = self.last_screenshot_time - self.session_start_time
            
            print(f"📸 Screenshot {self.screenshot_count}/{self.max_screenshots}: {filename}")
            print(f"   Gen: {self.frame_count}, Pop: {self.living_cells}, Session: {session_time:.1f}s")
            
            return filepath
            
        except Exception as e:
            print(f"Failed to take screenshot: {e}")
            return None
    
    def draw(self):
        """Render the 3D grid with ENHANCED VISIBILITY"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        # Set up camera
        glTranslatef(0, 0, self.zoom)
        glRotatef(self.rotation_x, 1, 0, 0)
        glRotatef(self.rotation_y, 0, 1, 0)
        
        # Center the grid
        offset = self.size / 2.0
        glTranslatef(-offset, -offset, -offset)
        
        # Draw living cells with BRIGHT, VISIBLE colors
        cube_size = 0.8  # Slightly larger
        for x in range(self.size):
            for y in range(self.size):
                for z in range(self.size):
                    if self.grid[x, y, z] == 1:
                        # BRIGHT, HIGH-CONTRAST COLORS
                        r = 0.8 + 0.2 * (x / self.size)  # Bright red component
                        g = 0.6 + 0.4 * (y / self.size)  # Bright green component  
                        b = 0.4 + 0.6 * (z / self.size)  # Bright blue component
                        
                        # Ensure minimum brightness
                        r = max(0.7, r)
                        g = max(0.5, g)
                        b = max(0.3, b)
                        
                        glColor3f(r, g, b)
                        
                        glPushMatrix()
                        glTranslatef(x, y, z)
                        
                        # Draw filled cube
                        self.draw_cube(cube_size)
                        
                        # Draw wireframe outline for extra visibility
                        glColor3f(1.0, 1.0, 1.0)  # White outline
                        self.draw_wireframe_cube(cube_size * 1.05)
                        
                        glPopMatrix()
        
        # Draw coordinate axes for reference (BRIGHT colors)
        self.draw_bright_axes()
        
        # Draw boundary wireframe (more visible)
        self.draw_bright_boundary()
        
        pygame.display.flip()
        
        # Conservative auto-screenshot check
        self.take_screenshot()
    
    def draw_cube(self, size):
        """Draw a filled cube"""
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
    
    def draw_wireframe_cube(self, size):
        """Draw wireframe outline of cube for visibility"""
        s = size / 2
        glBegin(GL_LINES)
        
        # All 12 edges of the cube
        edges = [
            # Bottom face edges
            [(-s, -s, -s), (s, -s, -s)], [(s, -s, -s), (s, -s, s)],
            [(s, -s, s), (-s, -s, s)], [(-s, -s, s), (-s, -s, -s)],
            # Top face edges
            [(-s, s, -s), (s, s, -s)], [(s, s, -s), (s, s, s)],
            [(s, s, s), (-s, s, s)], [(-s, s, s), (-s, s, -s)],
            # Vertical edges
            [(-s, -s, -s), (-s, s, -s)], [(s, -s, -s), (s, s, -s)],
            [(s, -s, s), (s, s, s)], [(-s, -s, s), (-s, s, s)]
        ]
        
        for edge in edges:
            glVertex3f(*edge[0])
            glVertex3f(*edge[1])
        
        glEnd()
    
    def draw_bright_axes(self):
        """Draw BRIGHT coordinate axes"""
        glBegin(GL_LINES)
        
        # X-axis (BRIGHT red)
        glColor3f(1.0, 0.2, 0.2)
        glVertex3f(0, 0, 0)
        glVertex3f(self.size + 2, 0, 0)
        
        # Y-axis (BRIGHT green)
        glColor3f(0.2, 1.0, 0.2)
        glVertex3f(0, 0, 0)
        glVertex3f(0, self.size + 2, 0)
        
        # Z-axis (BRIGHT blue)
        glColor3f(0.2, 0.2, 1.0)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0, self.size + 2)
        
        glEnd()
    
    def draw_bright_boundary(self):
        """Draw BRIGHT boundary wireframe"""
        glColor3f(0.8, 0.8, 0.8)  # Bright gray
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
            # Create bright patterns in corners
            for i in range(3):
                for j in range(3):
                    for k in range(3):
                        self.grid[i, j, k] = 1
                        self.grid[self.size-1-i, self.size-1-j, self.size-1-k] = 1
        
        self.frame_count = 0
        self.update_statistics()
        self.take_screenshot(f"opt_reset_{pattern_name}_{datetime.now().strftime('%H%M%S')}.png", force=True)

def main():
    """Main game loop with optimized screenshot capture"""
    try:
        import PIL.Image
    except ImportError:
        print("PIL (Pillow) is required for screenshots. Installing...")
        os.system("pip install Pillow")
        import PIL.Image
    
    pygame.init()
    display = (800, 600)
    screen = pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("OPTIMIZED 3D Game of Life - Conservative Screenshots")
    
    # OpenGL settings for better visibility
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.05, 0.05, 0.15, 1.0)  # Very dark background for contrast
    
    # Enable lighting for better 3D appearance
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_POSITION, [1, 1, 1, 0])
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.8, 1])
    glEnable(GL_COLOR_MATERIAL)
    
    # Set up perspective
    gluPerspective(45, (display[0]/display[1]), 0.1, 100.0)
    
    # Create OPTIMIZED game instance
    game = OptimizedGame3D(size=6)
    
    # Mouse control
    mouse_down = False
    last_mouse_pos = (0, 0)
    
    clock = pygame.time.Clock()
    
    print("\n" + "="*80)
    print("🎯 OPTIMIZED 3D Game of Life - Conservative Screenshot Capture")
    print("="*80)
    print("✅ OPTIMIZED: 1 screenshot per second maximum")
    print("✅ OPTIMIZED: 10 screenshot limit per session")
    print("✅ ENHANCED: Bright, high-contrast cell colors")
    print("✅ ENHANCED: Wireframe outlines for better visibility")
    print("\nControls:")
    print("  Mouse drag: Rotate view")
    print("  Mouse wheel: Zoom")
    print("  SPACE: Pause/Resume")
    print("  S: Manual screenshot (if under limit)")
    print("  R: Reset with random pattern")
    print("  C: Reset with cross pattern")  
    print("  N: Reset with corner pattern")
    print("  Q/ESC: Quit")
    print(f"\nScreenshot budget: {game.max_screenshots} max, 1/second rate")
    print(f"Generation: {game.frame_count}, Population: {game.living_cells}")
    print("="*80)
    
    # Take initial screenshot
    game.take_screenshot("opt_initial_state.png", force=True)
    
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
                    result = game.take_screenshot(force=True)
                    if result:
                        print("Manual screenshot taken")
                    else:
                        print(f"Screenshot limit reached ({game.screenshot_count}/{game.max_screenshots})")
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
            remaining_shots = game.max_screenshots - game.screenshot_count
            print(f"Gen: {game.frame_count:3d}, Pop: {game.living_cells:3d}, Peak: {game.peak_population:3d}, Screenshots: {remaining_shots} left")
        
        game.draw()
        clock.tick(60)
        
        # Stop if we've hit screenshot limit and some time has passed
        if game.screenshot_count >= game.max_screenshots and game.frame_count > 20:
            print(f"\n🎯 Reached screenshot limit ({game.max_screenshots}). Stopping session.")
            break
    
    # Take final screenshot if we have budget
    if game.screenshot_count < game.max_screenshots:
        game.take_screenshot("opt_final_state.png", force=True)
        
    session_time = time.time() - game.session_start_time
    print(f"\n🎯 Optimized session completed!")
    print(f"   Screenshots captured: {game.screenshot_count}/{game.max_screenshots}")
    print(f"   Session duration: {session_time:.1f} seconds")
    print(f"   Check {os.path.abspath(game.screenshot_dir)} for results.")
    pygame.quit()

if __name__ == "__main__":
    try:
        main()
    except ImportError as e:
        print("Missing required libraries. Please install with:")
        print("pip install numpy pygame PyOpenGL PyOpenGL_accelerate Pillow")
        print(f"Error: {e}")
    except Exception as e:
        print(f"Error running optimized demo: {e}")
        import traceback
        traceback.print_exc() 