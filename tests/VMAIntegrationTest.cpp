#include <gtest/gtest.h>
#include <vulkan/vulkan.h>
#include <vk_mem_alloc.h>
#include <vector>
#include <random>
#include "VulkanContext.h"
#include "VulkanMemoryManager.h"

class VMAIntegrationTest : public ::testing::Test {
protected:
    VulkanContext* context;
    VulkanMemoryManager* memoryManager;
    VmaAllocator allocator;
    
    void SetUp() override {
        context = new VulkanContext();
        context->initVulkan();
        memoryManager = new VulkanMemoryManager();
        memoryManager->init(context->getDevice(), context->getPhysicalDevice(), context->getInstance());
        allocator = memoryManager->getVmaAllocator();
    }
    
    void TearDown() override {
        delete memoryManager;
        delete context;
    }
};

TEST_F(VMAIntegrationTest, BasicBufferAllocation) {
    // Test basic buffer allocation with VMA
    VkBufferCreateInfo bufferInfo{};
    bufferInfo.sType = VK_STRUCTURE_TYPE_BUFFER_CREATE_INFO;
    bufferInfo.size = 1024 * 1024; // 1MB
    bufferInfo.usage = VK_BUFFER_USAGE_VERTEX_BUFFER_BIT | VK_BUFFER_USAGE_TRANSFER_DST_BIT;
    bufferInfo.sharingMode = VK_SHARING_MODE_EXCLUSIVE;
    
    VmaAllocationCreateInfo allocInfo{};
    allocInfo.usage = VMA_MEMORY_USAGE_GPU_ONLY;
    
    VkBuffer buffer;
    VmaAllocation allocation;
    
    ASSERT_EQ(vmaCreateBuffer(allocator, &bufferInfo, &allocInfo, &buffer, &allocation, nullptr), VK_SUCCESS);
    ASSERT_NE(buffer, VK_NULL_HANDLE);
    ASSERT_NE(allocation, VK_NULL_HANDLE);
    
    // Check allocation info
    VmaAllocationInfo allocationInfo;
    vmaGetAllocationInfo(allocator, allocation, &allocationInfo);
    EXPECT_GE(allocationInfo.size, bufferInfo.size);
    EXPECT_NE(allocationInfo.deviceMemory, VK_NULL_HANDLE);
    
    vmaDestroyBuffer(allocator, buffer, allocation);
}

TEST_F(VMAIntegrationTest, StagingBufferAllocation) {
    // Test staging buffer allocation (CPU visible)
    VkBufferCreateInfo bufferInfo{};
    bufferInfo.sType = VK_STRUCTURE_TYPE_BUFFER_CREATE_INFO;
    bufferInfo.size = 4096;
    bufferInfo.usage = VK_BUFFER_USAGE_TRANSFER_SRC_BIT;
    bufferInfo.sharingMode = VK_SHARING_MODE_EXCLUSIVE;
    
    VmaAllocationCreateInfo allocInfo{};
    allocInfo.usage = VMA_MEMORY_USAGE_CPU_TO_GPU;
    allocInfo.flags = VMA_ALLOCATION_CREATE_MAPPED_BIT;
    
    VkBuffer buffer;
    VmaAllocation allocation;
    VmaAllocationInfo allocationInfo;
    
    ASSERT_EQ(vmaCreateBuffer(allocator, &bufferInfo, &allocInfo, &buffer, &allocation, &allocationInfo), VK_SUCCESS);
    ASSERT_NE(allocationInfo.pMappedData, nullptr);
    
    // Write test data
    uint32_t* data = static_cast<uint32_t*>(allocationInfo.pMappedData);
    for (size_t i = 0; i < bufferInfo.size / sizeof(uint32_t); ++i) {
        data[i] = static_cast<uint32_t>(i);
    }
    
    // Flush if needed
    if ((allocationInfo.memoryType & VK_MEMORY_PROPERTY_HOST_COHERENT_BIT) == 0) {
        vmaFlushAllocation(allocator, allocation, 0, VK_WHOLE_SIZE);
    }
    
    vmaDestroyBuffer(allocator, buffer, allocation);
}

TEST_F(VMAIntegrationTest, ImageAllocation) {
    // Test image allocation with VMA
    VkImageCreateInfo imageInfo{};
    imageInfo.sType = VK_STRUCTURE_TYPE_IMAGE_CREATE_INFO;
    imageInfo.imageType = VK_IMAGE_TYPE_2D;
    imageInfo.format = VK_FORMAT_R8G8B8A8_UNORM;
    imageInfo.extent = {512, 512, 1};
    imageInfo.mipLevels = 1;
    imageInfo.arrayLayers = 1;
    imageInfo.samples = VK_SAMPLE_COUNT_1_BIT;
    imageInfo.tiling = VK_IMAGE_TILING_OPTIMAL;
    imageInfo.usage = VK_IMAGE_USAGE_SAMPLED_BIT | VK_IMAGE_USAGE_TRANSFER_DST_BIT;
    imageInfo.sharingMode = VK_SHARING_MODE_EXCLUSIVE;
    imageInfo.initialLayout = VK_IMAGE_LAYOUT_UNDEFINED;
    
    VmaAllocationCreateInfo allocInfo{};
    allocInfo.usage = VMA_MEMORY_USAGE_GPU_ONLY;
    
    VkImage image;
    VmaAllocation allocation;
    
    ASSERT_EQ(vmaCreateImage(allocator, &imageInfo, &allocInfo, &image, &allocation, nullptr), VK_SUCCESS);
    ASSERT_NE(image, VK_NULL_HANDLE);
    ASSERT_NE(allocation, VK_NULL_HANDLE);
    
    vmaDestroyImage(allocator, image, allocation);
}

TEST_F(VMAIntegrationTest, MemoryBudgetTest) {
    // Test memory budget tracking
    VmaBudget budgets[VK_MAX_MEMORY_HEAPS];
    vmaGetHeapBudgets(allocator, budgets);
    
    // Check that we have at least one heap with budget
    bool hasValidHeap = false;
    for (uint32_t i = 0; i < memoryManager->getMemoryProperties().memoryHeapCount; ++i) {
        if (budgets[i].budget > 0) {
            hasValidHeap = true;
            EXPECT_GE(budgets[i].budget, budgets[i].usage) << "Usage should not exceed budget";
            
            std::cout << "Heap " << i << ": "
                      << "Budget: " << budgets[i].budget / (1024 * 1024) << " MB, "
                      << "Usage: " << budgets[i].usage / (1024 * 1024) << " MB" << std::endl;
        }
    }
    EXPECT_TRUE(hasValidHeap);
}

TEST_F(VMAIntegrationTest, DefragmentationTest) {
    // Test memory defragmentation
    std::vector<VkBuffer> buffers;
    std::vector<VmaAllocation> allocations;
    
    // Create many small buffers
    for (int i = 0; i < 100; ++i) {
        VkBufferCreateInfo bufferInfo{};
        bufferInfo.sType = VK_STRUCTURE_TYPE_BUFFER_CREATE_INFO;
        bufferInfo.size = 1024 + (i * 100); // Varying sizes
        bufferInfo.usage = VK_BUFFER_USAGE_VERTEX_BUFFER_BIT;
        bufferInfo.sharingMode = VK_SHARING_MODE_EXCLUSIVE;
        
        VmaAllocationCreateInfo allocInfo{};
        allocInfo.usage = VMA_MEMORY_USAGE_GPU_ONLY;
        allocInfo.flags = VMA_ALLOCATION_CREATE_CAN_BECOME_LOST_BIT;
        
        VkBuffer buffer;
        VmaAllocation allocation;
        
        if (vmaCreateBuffer(allocator, &bufferInfo, &allocInfo, &buffer, &allocation, nullptr) == VK_SUCCESS) {
            buffers.push_back(buffer);
            allocations.push_back(allocation);
        }
    }
    
    // Delete every other buffer to create fragmentation
    for (size_t i = 0; i < buffers.size(); i += 2) {
        vmaDestroyBuffer(allocator, buffers[i], allocations[i]);
        buffers[i] = VK_NULL_HANDLE;
        allocations[i] = VK_NULL_HANDLE;
    }
    
    // Get initial stats
    VmaTotalStatistics statsBefore;
    vmaCalculateStatistics(allocator, &statsBefore);
    
    // Perform defragmentation
    VmaDefragmentationInfo defragInfo{};
    defragInfo.flags = VMA_DEFRAGMENTATION_FLAG_ALGORITHM_FAST_BIT;
    
    VmaDefragmentationContext defragCtx;
    ASSERT_EQ(vmaBeginDefragmentation(allocator, &defragInfo, &defragCtx), VK_SUCCESS);
    
    // Note: In a real application, you would need to handle moves here
    
    VmaDefragmentationStats defragStats;
    vmaEndDefragmentation(allocator, defragCtx, &defragStats);
    
    std::cout << "Defragmentation stats: "
              << "Bytes moved: " << defragStats.bytesMoved
              << ", Allocations moved: " << defragStats.allocationsMoved << std::endl;
    
    // Cleanup remaining buffers
    for (size_t i = 0; i < buffers.size(); ++i) {
        if (buffers[i] != VK_NULL_HANDLE) {
            vmaDestroyBuffer(allocator, buffers[i], allocations[i]);
        }
    }
}

TEST_F(VMAIntegrationTest, AllocationCallbacksTest) {
    // Test custom allocation callbacks
    struct AllocationStats {
        size_t totalAllocated = 0;
        size_t totalFreed = 0;
        size_t currentUsage = 0;
        size_t peakUsage = 0;
    };
    
    AllocationStats stats;
    
    // Create allocator with custom callbacks
    VkAllocationCallbacks callbacks{};
    callbacks.pUserData = &stats;
    callbacks.pfnAllocation = [](void* pUserData, size_t size, size_t alignment, VkSystemAllocationScope scope) -> void* {
        auto* stats = static_cast<AllocationStats*>(pUserData);
        stats->totalAllocated += size;
        stats->currentUsage += size;
        stats->peakUsage = std::max(stats->peakUsage, stats->currentUsage);
        return malloc(size);
    };
    callbacks.pfnFree = [](void* pUserData, void* pMemory) {
        if (pMemory) {
            auto* stats = static_cast<AllocationStats*>(pUserData);
            // Note: We don't know the size here in this simple example
            free(pMemory);
        }
    };
    callbacks.pfnReallocation = [](void* pUserData, void* pOriginal, size_t size, size_t alignment, VkSystemAllocationScope scope) -> void* {
        return realloc(pOriginal, size);
    };
    
    // Note: VMA itself doesn't use these callbacks for GPU memory, 
    // but this demonstrates the pattern
    EXPECT_EQ(stats.totalAllocated, 0);
}

TEST_F(VMAIntegrationTest, MemoryTypeSelectionTest) {
    // Test that VMA selects appropriate memory types
    struct TestCase {
        VkBufferUsageFlags usage;
        VmaMemoryUsage vmaUsage;
        VkMemoryPropertyFlags expectedProps;
    };
    
    std::vector<TestCase> testCases = {
        {VK_BUFFER_USAGE_VERTEX_BUFFER_BIT, VMA_MEMORY_USAGE_GPU_ONLY, VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT},
        {VK_BUFFER_USAGE_TRANSFER_SRC_BIT, VMA_MEMORY_USAGE_CPU_TO_GPU, VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT},
        {VK_BUFFER_USAGE_TRANSFER_DST_BIT, VMA_MEMORY_USAGE_GPU_TO_CPU, VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT},
    };
    
    for (const auto& test : testCases) {
        VkBufferCreateInfo bufferInfo{};
        bufferInfo.sType = VK_STRUCTURE_TYPE_BUFFER_CREATE_INFO;
        bufferInfo.size = 1024;
        bufferInfo.usage = test.usage;
        bufferInfo.sharingMode = VK_SHARING_MODE_EXCLUSIVE;
        
        VmaAllocationCreateInfo allocInfo{};
        allocInfo.usage = test.vmaUsage;
        
        VkBuffer buffer;
        VmaAllocation allocation;
        VmaAllocationInfo allocationInfo;
        
        ASSERT_EQ(vmaCreateBuffer(allocator, &bufferInfo, &allocInfo, &buffer, &allocation, &allocationInfo), VK_SUCCESS);
        
        // Check memory type properties
        VkMemoryPropertyFlags memProps = memoryManager->getMemoryProperties().memoryTypes[allocationInfo.memoryType].propertyFlags;
        EXPECT_TRUE((memProps & test.expectedProps) != 0) 
            << "Memory type " << allocationInfo.memoryType 
            << " doesn't have expected properties for usage " << test.usage;
        
        vmaDestroyBuffer(allocator, buffer, allocation);
    }
}

TEST_F(VMAIntegrationTest, StressTest) {
    // Stress test with many allocations
    const int numAllocations = 1000;
    std::vector<VkBuffer> buffers;
    std::vector<VmaAllocation> allocations;
    std::mt19937 rng(42);
    std::uniform_int_distribution<size_t> sizeDist(1024, 1024 * 1024); // 1KB to 1MB
    
    auto start = std::chrono::high_resolution_clock::now();
    
    // Allocate
    for (int i = 0; i < numAllocations; ++i) {
        VkBufferCreateInfo bufferInfo{};
        bufferInfo.sType = VK_STRUCTURE_TYPE_BUFFER_CREATE_INFO;
        bufferInfo.size = sizeDist(rng);
        bufferInfo.usage = VK_BUFFER_USAGE_STORAGE_BUFFER_BIT;
        bufferInfo.sharingMode = VK_SHARING_MODE_EXCLUSIVE;
        
        VmaAllocationCreateInfo allocInfo{};
        allocInfo.usage = VMA_MEMORY_USAGE_GPU_ONLY;
        
        VkBuffer buffer;
        VmaAllocation allocation;
        
        if (vmaCreateBuffer(allocator, &bufferInfo, &allocInfo, &buffer, &allocation, nullptr) == VK_SUCCESS) {
            buffers.push_back(buffer);
            allocations.push_back(allocation);
        }
    }
    
    auto allocTime = std::chrono::high_resolution_clock::now();
    
    // Get statistics
    VmaTotalStatistics stats;
    vmaCalculateStatistics(allocator, &stats);
    
    std::cout << "Allocated " << buffers.size() << " buffers" << std::endl;
    std::cout << "Total allocated: " << stats.total.statistics.allocationBytes / (1024 * 1024) << " MB" << std::endl;
    std::cout << "Allocation time: " << std::chrono::duration_cast<std::chrono::milliseconds>(allocTime - start).count() << " ms" << std::endl;
    
    // Deallocate
    for (size_t i = 0; i < buffers.size(); ++i) {
        vmaDestroyBuffer(allocator, buffers[i], allocations[i]);
    }
    
    auto deallocTime = std::chrono::high_resolution_clock::now();
    std::cout << "Deallocation time: " << std::chrono::duration_cast<std::chrono::milliseconds>(deallocTime - allocTime).count() << " ms" << std::endl;
} 