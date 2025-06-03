#include "GameOfLife3D.h"
#include <fstream>
#include <stdexcept>

GameOfLife3D::GameOfLife3D(VulkanContext* context, VulkanMemoryManager* memoryManager)
    : context(context), memoryManager(memoryManager), currentBuffer(0) {
}

GameOfLife3D::~GameOfLife3D() {
    // Cleanup Vulkan resources
    vkDestroyPipeline(context->getDevice(), computePipeline, nullptr);
    vkDestroyPipelineLayout(context->getDevice(), pipelineLayout, nullptr);
    vkDestroyDescriptorSetLayout(context->getDevice(), descriptorSetLayout, nullptr);
    vkDestroyDescriptorPool(context->getDevice(), descriptorPool, nullptr);
    vkDestroyShaderModule(context->getDevice(), computeShader, nullptr);
    
    // Cleanup buffers
    for (int i = 0; i < 2; i++) {
        vmaDestroyBuffer(memoryManager->getVmaAllocator(), gridBuffers[i], gridAllocations[i]);
    }
}

void GameOfLife3D::init(uint32_t gridSizeX, uint32_t gridSizeY, uint32_t gridSizeZ) {
    this->gridSizeX = gridSizeX;
    this->gridSizeY = gridSizeY;
    this->gridSizeZ = gridSizeZ;
    
    // Initialize grid state
    size_t totalCells = gridSizeX * gridSizeY * gridSizeZ;
    gridState.resize(totalCells, 0);
    
    // Create compute pipeline
    createComputePipeline();
    
    // Create buffers
    createBuffers();
    
    // Create descriptor sets
    createDescriptorSets();
}

void GameOfLife3D::createComputePipeline() {
    // Load compute shader
    std::ifstream file("shaders/game_of_life_3d.comp.spv", std::ios::ate | std::ios::binary);
    if (!file.is_open()) {
        throw std::runtime_error("Failed to open compute shader file");
    }
    
    size_t fileSize = (size_t)file.tellg();
    std::vector<char> code(fileSize);
    
    file.seekg(0);
    file.read(code.data(), fileSize);
    file.close();
    
    // Create shader module
    VkShaderModuleCreateInfo shaderInfo{};
    shaderInfo.sType = VK_STRUCTURE_TYPE_SHADER_MODULE_CREATE_INFO;
    shaderInfo.codeSize = code.size();
    shaderInfo.pCode = reinterpret_cast<const uint32_t*>(code.data());
    
    if (vkCreateShaderModule(context->getDevice(), &shaderInfo, nullptr, &computeShader) != VK_SUCCESS) {
        throw std::runtime_error("Failed to create compute shader module");
    }
    
    // Create descriptor set layout
    VkDescriptorSetLayoutBinding bindings[2]{};
    bindings[0].binding = 0;
    bindings[0].descriptorType = VK_DESCRIPTOR_TYPE_STORAGE_BUFFER;
    bindings[0].descriptorCount = 1;
    bindings[0].stageFlags = VK_SHADER_STAGE_COMPUTE_BIT;
    
    bindings[1].binding = 1;
    bindings[1].descriptorType = VK_DESCRIPTOR_TYPE_STORAGE_BUFFER;
    bindings[1].descriptorCount = 1;
    bindings[1].stageFlags = VK_SHADER_STAGE_COMPUTE_BIT;
    
    VkDescriptorSetLayoutCreateInfo layoutInfo{};
    layoutInfo.sType = VK_STRUCTURE_TYPE_DESCRIPTOR_SET_LAYOUT_CREATE_INFO;
    layoutInfo.bindingCount = 2;
    layoutInfo.pBindings = bindings;
    
    if (vkCreateDescriptorSetLayout(context->getDevice(), &layoutInfo, nullptr, &descriptorSetLayout) != VK_SUCCESS) {
        throw std::runtime_error("Failed to create descriptor set layout");
    }
    
    // Create pipeline layout
    VkPipelineLayoutCreateInfo pipelineLayoutInfo{};
    pipelineLayoutInfo.sType = VK_STRUCTURE_TYPE_PIPELINE_LAYOUT_CREATE_INFO;
    pipelineLayoutInfo.setLayoutCount = 1;
    pipelineLayoutInfo.pSetLayouts = &descriptorSetLayout;
    
    // Push constants for grid dimensions
    VkPushConstantRange pushConstantRange{};
    pushConstantRange.stageFlags = VK_SHADER_STAGE_COMPUTE_BIT;
    pushConstantRange.offset = 0;
    pushConstantRange.size = sizeof(uint32_t) * 3;  // gridSizeX, Y, Z
    
    pipelineLayoutInfo.pushConstantRangeCount = 1;
    pipelineLayoutInfo.pPushConstantRanges = &pushConstantRange;
    
    if (vkCreatePipelineLayout(context->getDevice(), &pipelineLayoutInfo, nullptr, &pipelineLayout) != VK_SUCCESS) {
        throw std::runtime_error("Failed to create pipeline layout");
    }
    
    // Create compute pipeline
    VkComputePipelineCreateInfo pipelineInfo{};
    pipelineInfo.sType = VK_STRUCTURE_TYPE_COMPUTE_PIPELINE_CREATE_INFO;
    pipelineInfo.stage.sType = VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO;
    pipelineInfo.stage.stage = VK_SHADER_STAGE_COMPUTE_BIT;
    pipelineInfo.stage.module = computeShader;
    pipelineInfo.stage.pName = "main";
    pipelineInfo.layout = pipelineLayout;
    
    if (vkCreateComputePipelines(context->getDevice(), VK_NULL_HANDLE, 1, &pipelineInfo, nullptr, &computePipeline) != VK_SUCCESS) {
        throw std::runtime_error("Failed to create compute pipeline");
    }
}

void GameOfLife3D::createBuffers() {
    VkBufferCreateInfo bufferInfo{};
    bufferInfo.sType = VK_STRUCTURE_TYPE_BUFFER_CREATE_INFO;
    bufferInfo.size = gridState.size() * sizeof(uint32_t);
    bufferInfo.usage = VK_BUFFER_USAGE_STORAGE_BUFFER_BIT;
    bufferInfo.sharingMode = VK_SHARING_MODE_EXCLUSIVE;
    
    VmaAllocationCreateInfo allocInfo{};
    allocInfo.usage = VMA_MEMORY_USAGE_GPU_ONLY;
    
    for (int i = 0; i < 2; i++) {
        if (vmaCreateBuffer(memoryManager->getVmaAllocator(), &bufferInfo, &allocInfo, &gridBuffers[i], &gridAllocations[i], nullptr) != VK_SUCCESS) {
            throw std::runtime_error("Failed to create grid buffer");
        }
    }
}

void GameOfLife3D::createDescriptorSets() {
    // Create descriptor pool
    VkDescriptorPoolSize poolSizes[1]{};
    poolSizes[0].type = VK_DESCRIPTOR_TYPE_STORAGE_BUFFER;
    poolSizes[0].descriptorCount = 4;  // 2 buffers * 2 descriptor sets
    
    VkDescriptorPoolCreateInfo poolInfo{};
    poolInfo.sType = VK_STRUCTURE_TYPE_DESCRIPTOR_POOL_CREATE_INFO;
    poolInfo.poolSizeCount = 1;
    poolInfo.pPoolSizes = poolSizes;
    poolInfo.maxSets = 2;
    
    if (vkCreateDescriptorPool(context->getDevice(), &poolInfo, nullptr, &descriptorPool) != VK_SUCCESS) {
        throw std::runtime_error("Failed to create descriptor pool");
    }
    
    // Allocate descriptor sets
    VkDescriptorSetAllocateInfo allocInfo{};
    allocInfo.sType = VK_STRUCTURE_TYPE_DESCRIPTOR_SET_ALLOCATE_INFO;
    allocInfo.descriptorPool = descriptorPool;
    allocInfo.descriptorSetCount = 1;
    allocInfo.pSetLayouts = &descriptorSetLayout;
    
    for (int i = 0; i < 2; i++) {
        if (vkAllocateDescriptorSets(context->getDevice(), &allocInfo, &descriptorSets[i]) != VK_SUCCESS) {
            throw std::runtime_error("Failed to allocate descriptor set");
        }
        
        // Update descriptor set
        VkDescriptorBufferInfo bufferInfos[2]{};
        bufferInfos[0].buffer = gridBuffers[i];
        bufferInfos[0].offset = 0;
        bufferInfos[0].range = VK_WHOLE_SIZE;
        
        bufferInfos[1].buffer = gridBuffers[1 - i];
        bufferInfos[1].offset = 0;
        bufferInfos[1].range = VK_WHOLE_SIZE;
        
        VkWriteDescriptorSet descriptorWrites[2]{};
        descriptorWrites[0].sType = VK_STRUCTURE_TYPE_WRITE_DESCRIPTOR_SET;
        descriptorWrites[0].dstSet = descriptorSets[i];
        descriptorWrites[0].dstBinding = 0;
        descriptorWrites[0].dstArrayElement = 0;
        descriptorWrites[0].descriptorType = VK_DESCRIPTOR_TYPE_STORAGE_BUFFER;
        descriptorWrites[0].descriptorCount = 1;
        descriptorWrites[0].pBufferInfo = &bufferInfos[0];
        
        descriptorWrites[1].sType = VK_STRUCTURE_TYPE_WRITE_DESCRIPTOR_SET;
        descriptorWrites[1].dstSet = descriptorSets[i];
        descriptorWrites[1].dstBinding = 1;
        descriptorWrites[1].dstArrayElement = 0;
        descriptorWrites[1].descriptorType = VK_DESCRIPTOR_TYPE_STORAGE_BUFFER;
        descriptorWrites[1].descriptorCount = 1;
        descriptorWrites[1].pBufferInfo = &bufferInfos[1];
        
        vkUpdateDescriptorSets(context->getDevice(), 2, descriptorWrites, 0, nullptr);
    }
}

void GameOfLife3D::update() {
    // Record and submit compute commands
    VkCommandBuffer cmdBuffer = context->beginSingleTimeCommands();
    recordComputeCommands(cmdBuffer);
    context->endSingleTimeCommands(cmdBuffer);
    
    // Swap buffers for next frame
    swapBuffers();
}

void GameOfLife3D::recordComputeCommands(VkCommandBuffer cmdBuffer) {
    // Bind compute pipeline
    vkCmdBindPipeline(cmdBuffer, VK_PIPELINE_BIND_POINT_COMPUTE, computePipeline);
    
    // Bind descriptor set
    vkCmdBindDescriptorSets(cmdBuffer, VK_PIPELINE_BIND_POINT_COMPUTE, pipelineLayout, 0, 1, &descriptorSets[currentBuffer], 0, nullptr);
    
    // Push constants for grid dimensions
    uint32_t pushConstants[3] = { gridSizeX, gridSizeY, gridSizeZ };
    vkCmdPushConstants(cmdBuffer, pipelineLayout, VK_SHADER_STAGE_COMPUTE_BIT, 0, sizeof(pushConstants), pushConstants);
    
    // Dispatch compute shader
    vkCmdDispatch(cmdBuffer, 
                 (gridSizeX + 7) / 8,  // Ceiling division by workgroup size
                 (gridSizeY + 7) / 8,
                 (gridSizeZ + 7) / 8);
}

void GameOfLife3D::swapBuffers() {
    currentBuffer = 1 - currentBuffer;
}

void GameOfLife3D::setCell(uint32_t x, uint32_t y, uint32_t z, uint32_t state) {
    if (x >= gridSizeX || y >= gridSizeY || z >= gridSizeZ) {
        return;
    }
    
    size_t index = x + y * gridSizeX + z * gridSizeX * gridSizeY;
    gridState[index] = state;
}

void GameOfLife3D::reset() {
    std::fill(gridState.begin(), gridState.end(), 0);
}

const std::vector<uint32_t>& GameOfLife3D::getGridState() const {
    return gridState;
} 