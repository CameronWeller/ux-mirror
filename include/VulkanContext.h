#pragma once

#include <vulkan/vulkan.h>
#include <vector>
#include <string>

class VulkanContext {
public:
    VulkanContext();
    ~VulkanContext();

    void initVulkan();
    
    VkInstance getInstance() const { return instance; }
    VkPhysicalDevice getPhysicalDevice() const { return physicalDevice; }
    VkDevice getDevice() const { return device; }
    uint32_t getComputeQueueFamily() const { return computeQueueFamily; }
    
    VkCommandBuffer beginSingleTimeCommands();
    void endSingleTimeCommands(VkCommandBuffer cmdBuffer);

private:
    void createInstance();
    void pickPhysicalDevice();
    void createLogicalDevice();
    void createCommandPool();
    
    bool checkValidationLayerSupport();
    std::vector<const char*> getRequiredExtensions();
    
    VkInstance instance;
    VkPhysicalDevice physicalDevice;
    VkDevice device;
    VkCommandPool commandPool;
    uint32_t computeQueueFamily;
    
    const std::vector<const char*> validationLayers = {
        "VK_LAYER_KHRONOS_validation"
    };
    
    const std::vector<const char*> deviceExtensions = {
        VK_KHR_SWAPCHAIN_EXTENSION_NAME
    };
}; 