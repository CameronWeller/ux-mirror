#pragma once

#include <vulkan/vulkan.h>
#include "VmaConfig.h"
#include "VulkanContext.h"

class VulkanMemoryManager {
public:
    VulkanMemoryManager(VulkanContext* context);
    ~VulkanMemoryManager();

    VmaAllocator getVmaAllocator() const { return allocator; }

private:
    VulkanContext* context;
    VmaAllocator allocator;
}; 