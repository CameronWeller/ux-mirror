#include "ComputeShaderDebugger.h"
#include "VulkanContext.h"
#include "VulkanMemoryManager.h"
#include <iostream>
#include <fstream>
#include <sstream>
#include <iomanip>

ComputeShaderDebugger::ComputeShaderDebugger(VulkanContext* context, VulkanMemoryManager* memoryManager)
    : m_context(context)
    , m_memoryManager(memoryManager)
    , m_enabled(true)
    , m_inDispatch(false)
    , m_timestampQueryPool(VK_NULL_HANDLE)
    , m_currentTimestampIndex(0)
    , vkCmdBeginDebugUtilsLabelEXT(nullptr)
    , vkCmdEndDebugUtilsLabelEXT(nullptr)
    , vkCmdInsertDebugUtilsLabelEXT(nullptr) {
    
    initDebugExtensions();
    createTimestampQueryPool();
}

ComputeShaderDebugger::~ComputeShaderDebugger() {
    destroyTimestampQueryPool();
}

void ComputeShaderDebugger::initDebugExtensions() {
    // Load debug extension functions
    vkCmdBeginDebugUtilsLabelEXT = (PFN_vkCmdBeginDebugUtilsLabelEXT)vkGetInstanceProcAddr(
        m_context->getInstance(), "vkCmdBeginDebugUtilsLabelEXT");
    vkCmdEndDebugUtilsLabelEXT = (PFN_vkCmdEndDebugUtilsLabelEXT)vkGetInstanceProcAddr(
        m_context->getInstance(), "vkCmdEndDebugUtilsLabelEXT");
    vkCmdInsertDebugUtilsLabelEXT = (PFN_vkCmdInsertDebugUtilsLabelEXT)vkGetInstanceProcAddr(
        m_context->getInstance(), "vkCmdInsertDebugUtilsLabelEXT");
}

void ComputeShaderDebugger::createTimestampQueryPool() {
    VkQueryPoolCreateInfo createInfo{};
    createInfo.sType = VK_STRUCTURE_TYPE_QUERY_POOL_CREATE_INFO;
    createInfo.queryType = VK_QUERY_TYPE_TIMESTAMP;
    createInfo.queryCount = 1000; // Support up to 1000 timestamps
    
    if (vkCreateQueryPool(m_context->getDevice(), &createInfo, nullptr, &m_timestampQueryPool) != VK_SUCCESS) {
        m_errors.push_back("Failed to create timestamp query pool");
    }
}

void ComputeShaderDebugger::destroyTimestampQueryPool() {
    if (m_timestampQueryPool != VK_NULL_HANDLE) {
        vkDestroyQueryPool(m_context->getDevice(), m_timestampQueryPool, nullptr);
    }
}

bool ComputeShaderDebugger::validateShaderModule(VkShaderModule shaderModule, const std::string& shaderName) {
    if (!m_enabled) return true;
    
    if (shaderModule == VK_NULL_HANDLE) {
        m_errors.push_back("Shader module '" + shaderName + "' is VK_NULL_HANDLE");
        return false;
    }
    
    // Additional validation can be added here
    return true;
}

bool ComputeShaderDebugger::validateComputePipeline(VkPipeline pipeline, const std::string& pipelineName) {
    if (!m_enabled) return true;
    
    if (pipeline == VK_NULL_HANDLE) {
        m_errors.push_back("Compute pipeline '" + pipelineName + "' is VK_NULL_HANDLE");
        return false;
    }
    
    return true;
}

void ComputeShaderDebugger::trackBuffer(VkBuffer buffer, size_t size, const std::string& name) {
    if (!m_enabled) return;
    
    BufferInfo info;
    info.size = size;
    info.name = name;
    info.lastAccessTime = std::chrono::steady_clock::now().time_since_epoch().count();
    
    m_trackedBuffers[buffer] = info;
}

void ComputeShaderDebugger::trackImage(VkImage image, VkExtent3D extent, VkFormat format, const std::string& name) {
    if (!m_enabled) return;
    
    ImageInfo info;
    info.extent = extent;
    info.format = format;
    info.name = name;
    info.lastAccessTime = std::chrono::steady_clock::now().time_since_epoch().count();
    
    m_trackedImages[image] = info;
}

void ComputeShaderDebugger::untrackBuffer(VkBuffer buffer) {
    m_trackedBuffers.erase(buffer);
}

void ComputeShaderDebugger::untrackImage(VkImage image) {
    m_trackedImages.erase(image);
}

void ComputeShaderDebugger::beginDispatch(const std::string& shaderName, uint32_t groupCountX, uint32_t groupCountY, uint32_t groupCountZ) {
    if (!m_enabled) return;
    
    m_currentDispatch.shaderName = shaderName;
    m_currentDispatch.groupCountX = groupCountX;
    m_currentDispatch.groupCountY = groupCountY;
    m_currentDispatch.groupCountZ = groupCountZ;
    m_currentDispatch.startTime = std::chrono::steady_clock::now();
    m_currentDispatch.buffers.clear();
    m_currentDispatch.images.clear();
    
    m_inDispatch = true;
}

void ComputeShaderDebugger::endDispatch() {
    if (!m_enabled || !m_inDispatch) return;
    
    m_currentDispatch.endTime = std::chrono::steady_clock::now();
    m_dispatchHistory.push_back(m_currentDispatch);
    m_inDispatch = false;
    
    // Keep history size manageable
    if (m_dispatchHistory.size() > 1000) {
        m_dispatchHistory.erase(m_dispatchHistory.begin());
    }
}

void ComputeShaderDebugger::insertTimestamp(VkCommandBuffer commandBuffer, const std::string& markerName) {
    if (!m_enabled || m_currentTimestampIndex >= 1000) return;
    
    vkCmdWriteTimestamp(commandBuffer, VK_PIPELINE_STAGE_BOTTOM_OF_PIPE_BIT, 
                       m_timestampQueryPool, m_currentTimestampIndex);
    
    m_timestampMarkers.push_back({m_currentTimestampIndex, markerName});
    m_currentTimestampIndex++;
}

void ComputeShaderDebugger::beginDebugLabel(VkCommandBuffer commandBuffer, const std::string& labelName, const float color[4]) {
    if (!m_enabled || !vkCmdBeginDebugUtilsLabelEXT) return;
    
    VkDebugUtilsLabelEXT label{};
    label.sType = VK_STRUCTURE_TYPE_DEBUG_UTILS_LABEL_EXT;
    label.pLabelName = labelName.c_str();
    memcpy(label.color, color, sizeof(float) * 4);
    
    vkCmdBeginDebugUtilsLabelEXT(commandBuffer, &label);
}

void ComputeShaderDebugger::endDebugLabel(VkCommandBuffer commandBuffer) {
    if (!m_enabled || !vkCmdEndDebugUtilsLabelEXT) return;
    
    vkCmdEndDebugUtilsLabelEXT(commandBuffer);
}

void ComputeShaderDebugger::insertDebugLabel(VkCommandBuffer commandBuffer, const std::string& labelName, const float color[4]) {
    if (!m_enabled || !vkCmdInsertDebugUtilsLabelEXT) return;
    
    VkDebugUtilsLabelEXT label{};
    label.sType = VK_STRUCTURE_TYPE_DEBUG_UTILS_LABEL_EXT;
    label.pLabelName = labelName.c_str();
    memcpy(label.color, color, sizeof(float) * 4);
    
    vkCmdInsertDebugUtilsLabelEXT(commandBuffer, &label);
}

bool ComputeShaderDebugger::validateMemoryBarrier(const VkMemoryBarrier& barrier) {
    if (!m_enabled) return true;
    
    // Check for common issues
    if (barrier.srcAccessMask == 0 && barrier.dstAccessMask == 0) {
        m_warnings.push_back("Memory barrier has both srcAccessMask and dstAccessMask set to 0");
    }
    
    return true;
}

bool ComputeShaderDebugger::validateBufferMemoryBarrier(const VkBufferMemoryBarrier& barrier) {
    if (!m_enabled) return true;
    
    if (barrier.buffer == VK_NULL_HANDLE) {
        m_errors.push_back("Buffer memory barrier has VK_NULL_HANDLE buffer");
        return false;
    }
    
    if (barrier.size == 0) {
        m_warnings.push_back("Buffer memory barrier has size of 0");
    }
    
    return true;
}

void ComputeShaderDebugger::checkSynchronizationHazards(VkPipelineStageFlags srcStage, 
                                                        VkPipelineStageFlags dstStage,
                                                        VkAccessFlags srcAccess, 
                                                        VkAccessFlags dstAccess) {
    if (!m_enabled) return;
    
    // Check for write-after-write hazards
    if ((srcAccess & VK_ACCESS_SHADER_WRITE_BIT) && (dstAccess & VK_ACCESS_SHADER_WRITE_BIT)) {
        m_warnings.push_back("Potential write-after-write hazard detected");
    }
    
    // Check for missing stages
    if (srcStage == 0 || dstStage == 0) {
        m_errors.push_back("Pipeline barrier has invalid stage flags");
    }
}

ComputeShaderDebugger::DebugStatistics ComputeShaderDebugger::getStatistics() const {
    DebugStatistics stats{};
    
    stats.totalDispatches = m_dispatchHistory.size();
    
    // Calculate total buffer bytes
    for (const auto& [buffer, info] : m_trackedBuffers) {
        stats.totalBufferBytes += info.size;
    }
    
    // Calculate total image pixels
    for (const auto& [image, info] : m_trackedImages) {
        stats.totalImagePixels += info.extent.width * info.extent.height * info.extent.depth;
    }
    
    // Calculate average dispatch time and counts
    if (!m_dispatchHistory.empty()) {
        double totalTime = 0;
        for (const auto& dispatch : m_dispatchHistory) {
            auto duration = std::chrono::duration_cast<std::chrono::microseconds>(
                dispatch.endTime - dispatch.startTime).count() / 1000.0;
            totalTime += duration;
            stats.dispatchCounts[dispatch.shaderName]++;
            stats.shaderTimings[dispatch.shaderName] += duration;
        }
        stats.averageDispatchTimeMs = totalTime / m_dispatchHistory.size();
    }
    
    return stats;
}

void ComputeShaderDebugger::dumpDebugInfo(const std::string& filename) const {
    std::ofstream file(filename);
    if (!file.is_open()) {
        return;
    }
    
    file << "=== Compute Shader Debug Report ===" << std::endl;
    file << "Generated at: " << std::chrono::system_clock::now().time_since_epoch().count() << std::endl;
    file << std::endl;
    
    // Dump statistics
    auto stats = getStatistics();
    file << "Total Dispatches: " << stats.totalDispatches << std::endl;
    file << "Total Buffer Memory: " << stats.totalBufferBytes / (1024.0 * 1024.0) << " MB" << std::endl;
    file << "Total Image Pixels: " << stats.totalImagePixels / 1000000.0 << " MP" << std::endl;
    file << "Average Dispatch Time: " << stats.averageDispatchTimeMs << " ms" << std::endl;
    file << std::endl;
    
    // Dump errors and warnings
    file << "Errors (" << m_errors.size() << "):" << std::endl;
    for (const auto& error : m_errors) {
        file << "  - " << error << std::endl;
    }
    file << std::endl;
    
    file << "Warnings (" << m_warnings.size() << "):" << std::endl;
    for (const auto& warning : m_warnings) {
        file << "  - " << warning << std::endl;
    }
    
    file.close();
}

void ComputeShaderDebugger::printResourceUsage() const {
    std::cout << "=== Resource Usage ===" << std::endl;
    std::cout << "Tracked Buffers: " << m_trackedBuffers.size() << std::endl;
    
    size_t totalBufferMemory = 0;
    for (const auto& [buffer, info] : m_trackedBuffers) {
        totalBufferMemory += info.size;
        std::cout << "  - " << info.name << ": " << info.size / 1024.0 << " KB" << std::endl;
    }
    
    std::cout << "Total Buffer Memory: " << totalBufferMemory / (1024.0 * 1024.0) << " MB" << std::endl;
    std::cout << std::endl;
    
    std::cout << "Tracked Images: " << m_trackedImages.size() << std::endl;
    for (const auto& [image, info] : m_trackedImages) {
        std::cout << "  - " << info.name << ": " 
                  << info.extent.width << "x" << info.extent.height << "x" << info.extent.depth 
                  << std::endl;
    }
}

void ComputeShaderDebugger::printDispatchHistory() const {
    std::cout << "=== Dispatch History (last 10) ===" << std::endl;
    
    size_t start = m_dispatchHistory.size() > 10 ? m_dispatchHistory.size() - 10 : 0;
    
    for (size_t i = start; i < m_dispatchHistory.size(); ++i) {
        const auto& dispatch = m_dispatchHistory[i];
        auto duration = std::chrono::duration_cast<std::chrono::microseconds>(
            dispatch.endTime - dispatch.startTime).count() / 1000.0;
        
        std::cout << std::setw(3) << i << ": " << dispatch.shaderName 
                  << " [" << dispatch.groupCountX << "," << dispatch.groupCountY << "," << dispatch.groupCountZ << "]"
                  << " - " << duration << " ms" << std::endl;
    }
}

// Stub implementations for methods that require more complex implementation
void ComputeShaderDebugger::captureBufferData(VkBuffer buffer, size_t offset, size_t size, 
                                              std::function<void(const void*)> callback) {
    // This would require creating a staging buffer and copying data
    // Left as stub for now
}

void ComputeShaderDebugger::captureImageData(VkImage image, VkImageSubresourceLayers subresource, 
                                             VkOffset3D offset, VkExtent3D extent, 
                                             std::function<void(const void*)> callback) {
    // This would require creating a staging buffer and copying image data
    // Left as stub for now
}

void ComputeShaderDebugger::retrieveTimestamps(std::unordered_map<std::string, double>& timings) {
    // This would require querying the timestamp pool and calculating timings
    // Left as stub for now
}

bool ComputeShaderDebugger::validateImageMemoryBarrier(const VkImageMemoryBarrier& barrier) {
    if (!m_enabled) return true;
    
    if (barrier.image == VK_NULL_HANDLE) {
        m_errors.push_back("Image memory barrier has VK_NULL_HANDLE image");
        return false;
    }
    
    return true;
} 