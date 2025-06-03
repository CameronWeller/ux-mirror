#include <gtest/gtest.h>
#include <vulkan/vulkan.h>
#include <vector>
#include <fstream>
#include <chrono>
#include "VulkanContext.h"
#include "VulkanMemoryManager.h"
#include "Grid3D.h"

class ComputeShaderTest : public ::testing::Test {
protected:
    VulkanContext* context;
    VulkanMemoryManager* memoryManager;
    
    void SetUp() override {
        context = new VulkanContext();
        context->initVulkan();
        memoryManager = new VulkanMemoryManager();
        memoryManager->init(context->getDevice(), context->getPhysicalDevice(), context->getInstance());
    }
    
    void TearDown() override {
        delete memoryManager;
        delete context;
    }
    
    // Helper function to load shader
    std::vector<char> loadShader(const std::string& filename) {
        std::ifstream file(filename, std::ios::ate | std::ios::binary);
        
        if (!file.is_open()) {
            throw std::runtime_error("Failed to open shader file: " + filename);
        }
        
        size_t fileSize = (size_t)file.tellg();
        std::vector<char> buffer(fileSize);
        
        file.seekg(0);
        file.read(buffer.data(), fileSize);
        file.close();
        
        return buffer;
    }
    
    // Helper to create shader module
    VkShaderModule createShaderModule(const std::vector<char>& code) {
        VkShaderModuleCreateInfo createInfo{};
        createInfo.sType = VK_STRUCTURE_TYPE_SHADER_MODULE_CREATE_INFO;
        createInfo.codeSize = code.size();
        createInfo.pCode = reinterpret_cast<const uint32_t*>(code.data());
        
        VkShaderModule shaderModule;
        if (vkCreateShaderModule(context->getDevice(), &createInfo, nullptr, &shaderModule) != VK_SUCCESS) {
            throw std::runtime_error("Failed to create shader module");
        }
        
        return shaderModule;
    }
};

TEST_F(ComputeShaderTest, ShaderCompilation) {
    // Test that compute shaders compile successfully
    ASSERT_NO_THROW({
        auto shaderCode = loadShader("../shaders/game_of_life_3d.comp.spv");
        ASSERT_GT(shaderCode.size(), 0);
        
        VkShaderModule shaderModule = createShaderModule(shaderCode);
        ASSERT_NE(shaderModule, VK_NULL_HANDLE);
        
        vkDestroyShaderModule(context->getDevice(), shaderModule, nullptr);
    });
}

TEST_F(ComputeShaderTest, ComputePipelineCreation) {
    // Test compute pipeline creation
    auto shaderCode = loadShader("../shaders/game_of_life_3d.comp.spv");
    VkShaderModule shaderModule = createShaderModule(shaderCode);
    
    // Create compute pipeline layout
    VkPipelineLayoutCreateInfo pipelineLayoutInfo{};
    pipelineLayoutInfo.sType = VK_STRUCTURE_TYPE_PIPELINE_LAYOUT_CREATE_INFO;
    
    VkPipelineLayout pipelineLayout;
    ASSERT_EQ(vkCreatePipelineLayout(context->getDevice(), &pipelineLayoutInfo, nullptr, &pipelineLayout), VK_SUCCESS);
    
    // Create compute pipeline
    VkComputePipelineCreateInfo pipelineInfo{};
    pipelineInfo.sType = VK_STRUCTURE_TYPE_COMPUTE_PIPELINE_CREATE_INFO;
    pipelineInfo.stage.sType = VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO;
    pipelineInfo.stage.stage = VK_SHADER_STAGE_COMPUTE_BIT;
    pipelineInfo.stage.module = shaderModule;
    pipelineInfo.stage.pName = "main";
    pipelineInfo.layout = pipelineLayout;
    
    VkPipeline computePipeline;
    ASSERT_EQ(vkCreateComputePipelines(context->getDevice(), VK_NULL_HANDLE, 1, &pipelineInfo, nullptr, &computePipeline), VK_SUCCESS);
    
    // Cleanup
    vkDestroyPipeline(context->getDevice(), computePipeline, nullptr);
    vkDestroyPipelineLayout(context->getDevice(), pipelineLayout, nullptr);
    vkDestroyShaderModule(context->getDevice(), shaderModule, nullptr);
}

TEST_F(ComputeShaderTest, MemoryBarrierTest) {
    // Test memory barriers for compute shader synchronization
    VkCommandPool commandPool;
    VkCommandPoolCreateInfo poolInfo{};
    poolInfo.sType = VK_STRUCTURE_TYPE_COMMAND_POOL_CREATE_INFO;
    poolInfo.queueFamilyIndex = context->getComputeQueueFamily();
    poolInfo.flags = VK_COMMAND_POOL_CREATE_RESET_COMMAND_BUFFER_BIT;
    
    ASSERT_EQ(vkCreateCommandPool(context->getDevice(), &poolInfo, nullptr, &commandPool), VK_SUCCESS);
    
    VkCommandBuffer commandBuffer;
    VkCommandBufferAllocateInfo allocInfo{};
    allocInfo.sType = VK_STRUCTURE_TYPE_COMMAND_BUFFER_ALLOCATE_INFO;
    allocInfo.commandPool = commandPool;
    allocInfo.level = VK_COMMAND_BUFFER_LEVEL_PRIMARY;
    allocInfo.commandBufferCount = 1;
    
    ASSERT_EQ(vkAllocateCommandBuffers(context->getDevice(), &allocInfo, &commandBuffer), VK_SUCCESS);
    
    // Begin recording
    VkCommandBufferBeginInfo beginInfo{};
    beginInfo.sType = VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO;
    ASSERT_EQ(vkBeginCommandBuffer(commandBuffer, &beginInfo), VK_SUCCESS);
    
    // Test buffer memory barrier
    VkBufferMemoryBarrier bufferBarrier{};
    bufferBarrier.sType = VK_STRUCTURE_TYPE_BUFFER_MEMORY_BARRIER;
    bufferBarrier.srcAccessMask = VK_ACCESS_SHADER_WRITE_BIT;
    bufferBarrier.dstAccessMask = VK_ACCESS_SHADER_READ_BIT;
    bufferBarrier.srcQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED;
    bufferBarrier.dstQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED;
    bufferBarrier.buffer = VK_NULL_HANDLE; // Would be actual buffer in real use
    bufferBarrier.offset = 0;
    bufferBarrier.size = VK_WHOLE_SIZE;
    
    vkCmdPipelineBarrier(
        commandBuffer,
        VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,
        VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,
        0,
        0, nullptr,
        1, &bufferBarrier,
        0, nullptr
    );
    
    ASSERT_EQ(vkEndCommandBuffer(commandBuffer), VK_SUCCESS);
    
    vkDestroyCommandPool(context->getDevice(), commandPool, nullptr);
}

TEST_F(ComputeShaderTest, DispatchDimensionsTest) {
    // Test various dispatch dimensions for compute shaders
    struct DispatchTest {
        uint32_t gridSize;
        uint32_t localSize;
        uint32_t expectedGroups;
    };
    
    std::vector<DispatchTest> tests = {
        {64, 8, 8},
        {128, 8, 16},
        {256, 16, 16},
        {100, 8, 13}, // Not evenly divisible
    };
    
    for (const auto& test : tests) {
        uint32_t groupCount = (test.gridSize + test.localSize - 1) / test.localSize;
        EXPECT_EQ(groupCount, test.expectedGroups) 
            << "Grid size: " << test.gridSize 
            << ", Local size: " << test.localSize;
    }
}

TEST_F(ComputeShaderTest, SharedMemoryLimitsTest) {
    // Test shared memory limits
    VkPhysicalDeviceProperties properties;
    vkGetPhysicalDeviceProperties(context->getPhysicalDevice(), &properties);
    
    // Check compute shader shared memory limit
    uint32_t maxSharedMemory = properties.limits.maxComputeSharedMemorySize;
    EXPECT_GT(maxSharedMemory, 0) << "Device should support shared memory";
    
    // Check workgroup limits
    uint32_t maxWorkGroupSizeX = properties.limits.maxComputeWorkGroupSize[0];
    uint32_t maxWorkGroupSizeY = properties.limits.maxComputeWorkGroupSize[1];
    uint32_t maxWorkGroupSizeZ = properties.limits.maxComputeWorkGroupSize[2];
    uint32_t maxInvocations = properties.limits.maxComputeWorkGroupInvocations;
    
    EXPECT_GE(maxWorkGroupSizeX, 128) << "X dimension should support at least 128";
    EXPECT_GE(maxWorkGroupSizeY, 128) << "Y dimension should support at least 128";
    EXPECT_GE(maxWorkGroupSizeZ, 64) << "Z dimension should support at least 64";
    EXPECT_GE(maxInvocations, 128) << "Should support at least 128 invocations";
}

TEST_F(ComputeShaderTest, PerformanceBenchmark) {
    // Simple performance benchmark for compute dispatch
    const int iterations = 100;
    
    // Create dummy command buffer for timing
    VkCommandPool commandPool;
    VkCommandPoolCreateInfo poolInfo{};
    poolInfo.sType = VK_STRUCTURE_TYPE_COMMAND_POOL_CREATE_INFO;
    poolInfo.queueFamilyIndex = context->getComputeQueueFamily();
    
    vkCreateCommandPool(context->getDevice(), &poolInfo, nullptr, &commandPool);
    
    VkCommandBuffer commandBuffer;
    VkCommandBufferAllocateInfo allocInfo{};
    allocInfo.sType = VK_STRUCTURE_TYPE_COMMAND_BUFFER_ALLOCATE_INFO;
    allocInfo.commandPool = commandPool;
    allocInfo.level = VK_COMMAND_BUFFER_LEVEL_PRIMARY;
    allocInfo.commandBufferCount = 1;
    
    vkAllocateCommandBuffers(context->getDevice(), &allocInfo, &commandBuffer);
    
    auto start = std::chrono::high_resolution_clock::now();
    
    for (int i = 0; i < iterations; ++i) {
        VkCommandBufferBeginInfo beginInfo{};
        beginInfo.sType = VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO;
        beginInfo.flags = VK_COMMAND_BUFFER_USAGE_ONE_TIME_SUBMIT_BIT;
        
        vkBeginCommandBuffer(commandBuffer, &beginInfo);
        // Simulate compute dispatch
        vkEndCommandBuffer(commandBuffer);
        vkResetCommandBuffer(commandBuffer, 0);
    }
    
    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
    
    std::cout << "Average command buffer record time: " 
              << duration.count() / iterations << " microseconds" << std::endl;
    
    vkDestroyCommandPool(context->getDevice(), commandPool, nullptr);
} 