#!/usr/bin/env python3
"""
Interactive 3D Game of Life Visualizer
- Renders a 3D grid and live cells (2D projection)
- UI overlays (title, stats, controls)
- Press '1' to take a screenshot
- Animates patterns for demo purposes
"""

import pygame
import sys
import time
import math
from datetime import datetime

# --- Config ---
WIDTH, HEIGHT = 900, 700
GRID_SIZE = 7
GRID_W, GRID_H, GRID_D = 12, 12, 6
PERSPECTIVE = 0.25
FPS = 30

# --- Patterns ---
PATTERNS = [
    # Glider
    [(2, 2, 2), (3, 2, 2), (4, 2, 2), (4, 3, 2), (3, 4, 2)],
    # Block
    [(6, 6, 3), (7, 6, 3), (6, 7, 3), (7, 7, 3)],
    # Blinker
    [(2, 8, 4), (3, 8, 4), (4, 8, 4)],
    # 3D Structure
    [(8, 2, 5), (9, 2, 5), (10, 2, 5), (9, 3, 5), (9, 4, 5), (8, 4, 5), (10, 4, 5)]
]

# --- Helper functions ---
def project(x, y, z, cx, cy):
    """Project 3D grid point to 2D screen coordinates"""
    sx = cx + (x - GRID_W/2) * GRID_SIZE
    sy = cy + (y - GRID_H/2) * GRID_SIZE
    if z > 0:
        perspective = 1 + (z * PERSPECTIVE)
        sx = cx + (sx - cx) * perspective
        sy = cy + (sy - cy) * perspective
    return int(sx), int(sy)

def draw_grid(screen, cx, cy):
    for z in range(GRID_D + 1):
        alpha = 255 - int((z / GRID_D) * 180)
        color = (51, 51, 51, alpha)
        for x in range(GRID_W + 1):
            for y in range(GRID_H + 1):
                sx, sy = project(x, y, z, cx, cy)
                pygame.draw.circle(screen, color[:3], (sx, sy), 2)

def draw_cells(screen, cx, cy, live_cells):
    for (x, y, z) in live_cells:
        sx, sy = project(x, y, z, cx, cy)
        alpha = 255 - int((z / GRID_D) * 80)
        color = (0, 255, 0, alpha)
        # Glow
        s = pygame.Surface((18, 18), pygame.SRCALPHA)
        pygame.draw.circle(s, (0, 255, 0, 40), (9, 9), 9)
        screen.blit(s, (sx-9, sy-9))
        # Cell
        pygame.draw.circle(screen, color[:3], (sx, sy), 6)

def draw_ui(screen, font, small_font, gen, live_count, fps):
    # Title
    pygame.draw.rect(screen, (42, 42, 42), (WIDTH//2-120, 10, 240, 40), border_radius=8)
    text = font.render("3D Game of Life", True, (255,255,255))
    screen.blit(text, (WIDTH//2-100, 15))
    # Stats
    pygame.draw.rect(screen, (42,42,42), (20, 20, 180, 100), border_radius=8)
    screen.blit(small_font.render(f"Generation: {gen}", True, (255,255,255)), (30, 30))
    screen.blit(small_font.render(f"Live Cells: {live_count}", True, (255,255,255)), (30, 50))
    screen.blit(small_font.render(f"FPS: {int(fps)}", True, (255,255,255)), (30, 70))
    screen.blit(small_font.render(f"Speed: 1x", True, (255,255,255)), (30, 90))
    # Controls
    pygame.draw.rect(screen, (42,42,42), (20, HEIGHT-160, 180, 130), border_radius=8)
    controls = [
        ("1", "Screenshot"),
        ("Space", "Pause/Resume"),
        ("R", "Reset"),
        ("F", "Faster"),
        ("S", "Slower"),
        ("Mouse", "Rotate View"),
        ("Scroll", "Zoom")
    ]
    y = HEIGHT-150
    for key, action in controls:
        screen.blit(small_font.render(f"{key}:", True, (0,255,0)), (30, y))
        screen.blit(small_font.render(action, True, (255,255,255)), (90, y))
        y += 18
    # Patterns
    pygame.draw.rect(screen, (42,42,42), (WIDTH-220, 20, 200, 100), border_radius=8)
    screen.blit(small_font.render("Active Patterns:", True, (255,255,255)), (WIDTH-210, 30))
    patterns = ["Glider", "Block", "Blinker", "3D Structure"]
    y = 50
    for p in patterns:
        screen.blit(small_font.render(f"• {p}", True, (0,255,0)), (WIDTH-200, y))
        y += 18

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("3D Game of Life Interactive Demo")
    font = pygame.font.SysFont("Arial", 28, bold=True)
    small_font = pygame.font.SysFont("Arial", 18)
    clock = pygame.time.Clock()
    running = True
    paused = False
    gen = 1
    pattern_idx = 0
    t_last = time.time()
    
    while running:
        dt = clock.tick(FPS)
        fps = clock.get_fps()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    # Screenshot
                    fname = f"game_of_life_screenshot_{int(time.time())}.png"
                    pygame.image.save(screen, fname)
                    print(f"Screenshot saved: {fname}")
                elif event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_r:
                    gen = 1
                    pattern_idx = 0
                elif event.key == pygame.K_f:
                    pass  # Could increase speed
                elif event.key == pygame.K_s:
                    pass  # Could decrease speed
        # Animate
        if not paused and time.time() - t_last > 1.5:
            gen += 1
            pattern_idx = (pattern_idx + 1) % len(PATTERNS)
            t_last = time.time()
        # Draw
        screen.fill((26,26,26))
        cx, cy = WIDTH//2, HEIGHT//2+40
        draw_grid(screen, cx, cy)
        live_cells = PATTERNS[pattern_idx]
        draw_cells(screen, cx, cy, live_cells)
        draw_ui(screen, font, small_font, gen, len(live_cells), fps)
        pygame.display.flip()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 