#include "VulkanMemoryManager.h"
#include <stdexcept>

VulkanMemoryManager::VulkanMemoryManager(VulkanContext* context) : context(context) {
    VmaAllocatorCreateInfo allocatorInfo = {};
    allocatorInfo.vulkanApiVersion = VK_API_VERSION_1_0;
    allocatorInfo.physicalDevice = context->getPhysicalDevice();
    allocatorInfo.device = context->getDevice();
    allocatorInfo.instance = context->getInstance();

    if (vmaCreateAllocator(&allocatorInfo, &allocator) != VK_SUCCESS) {
        throw std::runtime_error("Failed to create VMA allocator");
    }
}

VulkanMemoryManager::~VulkanMemoryManager() {
    vmaDestroyAllocator(allocator);
} 