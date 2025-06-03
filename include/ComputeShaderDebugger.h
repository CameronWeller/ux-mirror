#pragma once

#include <vulkan/vulkan.h>
#include <vector>
#include <string>
#include <functional>
#include <chrono>
#include <unordered_map>

class VulkanContext;
class VulkanMemoryManager;

struct ComputeDispatchInfo {
    uint32_t groupCountX;
    uint32_t groupCountY;
    uint32_t groupCountZ;
    std::string shaderName;
    std::chrono::steady_clock::time_point startTime;
    std::chrono::steady_clock::time_point endTime;
    std::vector<VkBuffer> buffers;
    std::vector<VkImage> images;
};

struct ShaderDebugData {
    std::vector<uint32_t> outputData;
    std::vector<float> performanceMetrics;
    std::string errorMessages;
};

class ComputeShaderDebugger {
public:
    ComputeShaderDebugger(VulkanContext* context, VulkanMemoryManager* memoryManager);
    ~ComputeShaderDebugger();

    // Enable/disable debugging
    void setEnabled(bool enabled) { m_enabled = enabled; }
    bool isEnabled() const { return m_enabled; }

    // Shader validation
    bool validateShaderModule(VkShaderModule shaderModule, const std::string& shaderName);
    bool validateComputePipeline(VkPipeline pipeline, const std::string& pipelineName);

    // Resource tracking
    void trackBuffer(VkBuffer buffer, size_t size, const std::string& name);
    void trackImage(VkImage image, VkExtent3D extent, VkFormat format, const std::string& name);
    void untrackBuffer(VkBuffer buffer);
    void untrackImage(VkImage image);

    // Dispatch debugging
    void beginDispatch(const std::string& shaderName, uint32_t groupCountX, uint32_t groupCountY, uint32_t groupCountZ);
    void endDispatch();

    // Memory debugging
    void captureBufferData(VkBuffer buffer, size_t offset, size_t size, std::function<void(const void*)> callback);
    void captureImageData(VkImage image, VkImageSubresourceLayers subresource, VkOffset3D offset, VkExtent3D extent, std::function<void(const void*)> callback);

    // Performance analysis
    void insertTimestamp(VkCommandBuffer commandBuffer, const std::string& markerName);
    void retrieveTimestamps(std::unordered_map<std::string, double>& timings);

    // Debug markers (for RenderDoc/NSight)
    void beginDebugLabel(VkCommandBuffer commandBuffer, const std::string& labelName, const float color[4]);
    void endDebugLabel(VkCommandBuffer commandBuffer);
    void insertDebugLabel(VkCommandBuffer commandBuffer, const std::string& labelName, const float color[4]);

    // Barrier validation
    bool validateMemoryBarrier(const VkMemoryBarrier& barrier);
    bool validateBufferMemoryBarrier(const VkBufferMemoryBarrier& barrier);
    bool validateImageMemoryBarrier(const VkImageMemoryBarrier& barrier);

    // Synchronization debugging
    void checkSynchronizationHazards(VkPipelineStageFlags srcStage, VkPipelineStageFlags dstStage,
                                     VkAccessFlags srcAccess, VkAccessFlags dstAccess);

    // Error reporting
    std::vector<std::string> getErrors() const { return m_errors; }
    std::vector<std::string> getWarnings() const { return m_warnings; }
    void clearMessages() { m_errors.clear(); m_warnings.clear(); }

    // Statistics
    struct DebugStatistics {
        uint64_t totalDispatches;
        uint64_t totalBufferBytes;
        uint64_t totalImagePixels;
        double averageDispatchTimeMs;
        std::unordered_map<std::string, uint64_t> dispatchCounts;
        std::unordered_map<std::string, double> shaderTimings;
    };
    DebugStatistics getStatistics() const;

    // Debug output
    void dumpDebugInfo(const std::string& filename) const;
    void printResourceUsage() const;
    void printDispatchHistory() const;

private:
    VulkanContext* m_context;
    VulkanMemoryManager* m_memoryManager;
    bool m_enabled;

    // Resource tracking
    struct BufferInfo {
        size_t size;
        std::string name;
        uint64_t lastAccessTime;
    };
    struct ImageInfo {
        VkExtent3D extent;
        VkFormat format;
        std::string name;
        uint64_t lastAccessTime;
    };
    std::unordered_map<VkBuffer, BufferInfo> m_trackedBuffers;
    std::unordered_map<VkImage, ImageInfo> m_trackedImages;

    // Dispatch tracking
    std::vector<ComputeDispatchInfo> m_dispatchHistory;
    ComputeDispatchInfo m_currentDispatch;
    bool m_inDispatch;

    // Timestamp queries
    VkQueryPool m_timestampQueryPool;
    uint32_t m_currentTimestampIndex;
    std::vector<std::pair<uint32_t, std::string>> m_timestampMarkers;

    // Error tracking
    std::vector<std::string> m_errors;
    std::vector<std::string> m_warnings;

    // Debug extensions
    PFN_vkCmdBeginDebugUtilsLabelEXT vkCmdBeginDebugUtilsLabelEXT;
    PFN_vkCmdEndDebugUtilsLabelEXT vkCmdEndDebugUtilsLabelEXT;
    PFN_vkCmdInsertDebugUtilsLabelEXT vkCmdInsertDebugUtilsLabelEXT;

    void initDebugExtensions();
    void createTimestampQueryPool();
    void destroyTimestampQueryPool();
}; 