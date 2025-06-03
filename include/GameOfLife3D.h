#pragma once

#include <vulkan/vulkan.h>
#include <vector>
#include <memory>
#include "VulkanContext.h"
#include "VulkanMemoryManager.h"
#include "VmaConfig.h"

class GameOfLife3D {
public:
    GameOfLife3D(VulkanContext* context, VulkanMemoryManager* memoryManager);
    ~GameOfLife3D();

    // Initialize the game
    void init(uint32_t gridSizeX = 64, uint32_t gridSizeY = 64, uint32_t gridSizeZ = 64);
    
    // Update the game state
    void update();
    
    // Render the current state
    void render(VkCommandBuffer cmdBuffer);
    
    // Get the current grid state
    const std::vector<uint32_t>& getGridState() const;
    
    // Set a cell state
    void setCell(uint32_t x, uint32_t y, uint32_t z, uint32_t state);
    
    // Reset the grid
    void reset();

private:
    // Create compute pipeline
    void createComputePipeline();
    
    // Create buffers
    void createBuffers();
    
    // Create descriptor sets
    void createDescriptorSets();
    
    // Record compute commands
    void recordComputeCommands(VkCommandBuffer cmdBuffer);
    
    // Swap input/output buffers
    void swapBuffers();

    VulkanContext* context;
    VulkanMemoryManager* memoryManager;
    
    // Grid dimensions
    uint32_t gridSizeX;
    uint32_t gridSizeY;
    uint32_t gridSizeZ;
    
    // Compute pipeline
    VkPipeline computePipeline;
    VkPipelineLayout pipelineLayout;
    
    // Buffers
    VkBuffer gridBuffers[2];  // Double buffering
    VmaAllocation gridAllocations[2];
    uint32_t currentBuffer;
    
    // Descriptor sets
    VkDescriptorSetLayout descriptorSetLayout;
    VkDescriptorPool descriptorPool;
    VkDescriptorSet descriptorSets[2];
    
    // Shader module
    VkShaderModule computeShader;
    
    // Grid state
    std::vector<uint32_t> gridState;
}; 