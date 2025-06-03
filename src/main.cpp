#include "VulkanContext.h"
#include "GameOfLife3D.h"
#include "VulkanMemoryManager.h"
#include <iostream>
#include <vector>
#include <array>
#include <chrono>
#include <thread>

const uint32_t GRID_SIZE = 32;
const uint32_t NUM_CELLS = GRID_SIZE * GRID_SIZE * GRID_SIZE;

void printGrid(const std::vector<uint32_t>& grid, uint32_t size) {
    for (uint32_t z = 0; z < size; z++) {
        std::cout << "Layer " << z << ":" << std::endl;
        for (uint32_t y = 0; y < size; y++) {
            for (uint32_t x = 0; x < size; x++) {
                uint32_t index = z * size * size + y * size + x;
                std::cout << (grid[index] ? "■ " : "□ ");
            }
            std::cout << std::endl;
        }
        std::cout << std::endl;
    }
}

int main() {
    try {
        // Initialize Vulkan context
        VulkanContext context;
        context.initVulkan();
        
        // Initialize memory manager
        VulkanMemoryManager memoryManager(&context);
        
        // Create and initialize Game of Life
        GameOfLife3D game(&context, &memoryManager);
        game.init(GRID_SIZE, GRID_SIZE, GRID_SIZE);
        
        // Create a simple glider pattern
        game.setCell(0, 0, 0, 1);
        game.setCell(1, 0, 0, 1);
        game.setCell(2, 0, 0, 1);
        game.setCell(1, 1, 0, 1);
        game.setCell(2, 1, 0, 1);
        game.setCell(2, 2, 0, 1);
        
        // Main simulation loop
        for (int i = 0; i < 100; i++) {
            std::cout << "\033[2J\033[1;1H"; // Clear screen
            std::cout << "Step " << i << std::endl;
            
            // Update simulation
            game.update();
            
            // Print current state
            printGrid(game.getGridState(), GRID_SIZE);
            
            // Add a small delay to make the visualization visible
            std::this_thread::sleep_for(std::chrono::milliseconds(500));
        }
        
    } catch (const std::exception& e) {
        std::cerr << e.what() << std::endl;
        return -1;
    }
    
    return 0;
} 