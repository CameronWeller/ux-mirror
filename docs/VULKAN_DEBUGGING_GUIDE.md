# Vulkan Debugging Guide for 3D Game of Life

## Table of Contents
1. [Overview](#overview)
2. [Common Issues and Solutions](#common-issues-and-solutions)
3. [Compute Shader Debugging](#compute-shader-debugging)
4. [VMA Integration Debugging](#vma-integration-debugging)
5. [Performance Debugging](#performance-debugging)
6. [Tools and Utilities](#tools-and-utilities)

## Overview

This guide provides comprehensive debugging strategies for the 3D Game of Life Vulkan implementation, focusing on compute shaders, memory management, and performance optimization.

## Common Issues and Solutions

### 1. Validation Layer Errors

**Problem**: Vulkan validation layers report errors during runtime.

**Solution**:
```cpp
// Enable validation layers in debug builds
#ifdef DEBUG
const std::vector<const char*> validationLayers = {
    "VK_LAYER_KHRONOS_validation"
};
#endif

// Check for specific validation errors
vkCreateInstance(&createInfo, nullptr, &instance);
```

**Common validation errors**:
- `VUID-vkCmdDispatch-None-02690`: Descriptor set not bound
- `VUID-VkBufferMemoryBarrier-buffer-01931`: Invalid buffer in barrier
- `VUID-vkCmdPipelineBarrier-srcStageMask-01168`: Invalid pipeline stage

### 2. Device Lost Errors

**Problem**: `VK_ERROR_DEVICE_LOST` occurs during heavy compute operations.

**Debugging steps**:
1. Check for infinite loops in compute shaders
2. Verify workgroup sizes don't exceed device limits
3. Add timeout detection:

```cpp
VkResult result = vkQueueWaitIdle(computeQueue);
if (result == VK_ERROR_DEVICE_LOST) {
    // Log GPU state before crash
    dumpGPUState();
    // Attempt recovery
    recreateComputePipeline();
}
```

### 3. Memory Allocation Failures

**Problem**: `VK_ERROR_OUT_OF_DEVICE_MEMORY` or `VK_ERROR_OUT_OF_HOST_MEMORY`

**Solution**:
```cpp
// Monitor memory usage
VmaBudget budgets[VK_MAX_MEMORY_HEAPS];
vmaGetHeapBudgets(allocator, budgets);

for (uint32_t i = 0; i < memoryHeapCount; ++i) {
    if (budgets[i].usage > budgets[i].budget * 0.9) {
        LOG_WARNING("Heap %d near capacity: %llu / %llu MB", 
                    i, budgets[i].usage / 1048576, budgets[i].budget / 1048576);
    }
}
```

## Compute Shader Debugging

### 1. Shader Compilation Issues

**Debug shader compilation**:
```bash
# Compile with debug info
glslc -g -o shader.spv shader.comp

# Validate SPIR-V
spirv-val shader.spv

# Disassemble for inspection
spirv-dis shader.spv -o shader.dis
```

### 2. Workgroup Size Debugging

**Common issues**:
- Workgroup size exceeds device limits
- Inefficient workgroup dimensions

**Debug code**:
```cpp
void validateWorkgroupSize(VkPhysicalDevice physicalDevice, uint32_t x, uint32_t y, uint32_t z) {
    VkPhysicalDeviceProperties props;
    vkGetPhysicalDeviceProperties(physicalDevice, &props);
    
    assert(x <= props.limits.maxComputeWorkGroupSize[0]);
    assert(y <= props.limits.maxComputeWorkGroupSize[1]);
    assert(z <= props.limits.maxComputeWorkGroupSize[2]);
    assert(x * y * z <= props.limits.maxComputeWorkGroupInvocations);
}
```

### 3. Synchronization Issues

**Debug barriers**:
```cpp
// Add comprehensive barrier
VkMemoryBarrier memBarrier = {
    .sType = VK_STRUCTURE_TYPE_MEMORY_BARRIER,
    .srcAccessMask = VK_ACCESS_SHADER_WRITE_BIT,
    .dstAccessMask = VK_ACCESS_SHADER_READ_BIT
};

vkCmdPipelineBarrier(
    commandBuffer,
    VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,
    VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,
    0,
    1, &memBarrier,
    0, nullptr,
    0, nullptr
);
```

### 4. Debug Output from Shaders

**Add debug buffer**:
```glsl
// In compute shader
layout(set = 1, binding = 0) buffer DebugBuffer {
    uint debugData[];
} debug;

void main() {
    uint globalID = gl_GlobalInvocationID.x;
    
    // Debug output
    debug.debugData[globalID] = computeResult;
    
    // Add memory barrier for debug buffer
    memoryBarrierBuffer();
}
```

## VMA Integration Debugging

### 1. Allocation Debugging

**Enable VMA debug features**:
```cpp
VmaAllocatorCreateInfo allocatorInfo = {};
allocatorInfo.flags = VMA_ALLOCATOR_CREATE_EXT_MEMORY_BUDGET_BIT;
allocatorInfo.vulkanApiVersion = VK_API_VERSION_1_2;

// Enable memory tracking
allocatorInfo.pRecordSettings = &recordSettings;
```

### 2. Memory Leak Detection

**Track allocations**:
```cpp
class VMADebugger {
    std::unordered_map<VmaAllocation, AllocationInfo> allocations;
    
public:
    void trackAllocation(VmaAllocation alloc, const char* name, size_t size) {
        allocations[alloc] = {name, size, getCurrentTime()};
    }
    
    void untrackAllocation(VmaAllocation alloc) {
        allocations.erase(alloc);
    }
    
    void reportLeaks() {
        for (const auto& [alloc, info] : allocations) {
            LOG_ERROR("Leaked allocation: %s, size: %zu", info.name, info.size);
        }
    }
};
```

### 3. Defragmentation Debugging

**Monitor defragmentation**:
```cpp
VmaDefragmentationInfo defragInfo = {};
defragInfo.flags = VMA_DEFRAGMENTATION_FLAG_ALGORITHM_EXTENSIVE_BIT;
defragInfo.maxBytesPerPass = 256 * 1024 * 1024; // 256 MB
defragInfo.maxAllocationsPerPass = 1024;

VmaDefragmentationContext defragCtx;
vmaBeginDefragmentation(allocator, &defragInfo, &defragCtx);

// Process moves
VmaDefragmentationPassMoveInfo passInfo = {};
vmaBeginDefragmentationPass(allocator, defragCtx, &passInfo);

// Log moves for debugging
for (uint32_t i = 0; i < passInfo.moveCount; ++i) {
    LOG_DEBUG("Moving allocation from heap %d to heap %d",
              passInfo.pMoves[i].srcAllocation,
              passInfo.pMoves[i].dstTmpAllocation);
}
```

## Performance Debugging

### 1. GPU Timing

**Add timestamp queries**:
```cpp
class GPUTimer {
    VkQueryPool queryPool;
    uint32_t queryCount = 0;
    
public:
    void begin(VkCommandBuffer cmd) {
        vkCmdResetQueryPool(cmd, queryPool, 0, 2);
        vkCmdWriteTimestamp(cmd, VK_PIPELINE_STAGE_TOP_OF_PIPE_BIT, queryPool, 0);
    }
    
    void end(VkCommandBuffer cmd) {
        vkCmdWriteTimestamp(cmd, VK_PIPELINE_STAGE_BOTTOM_OF_PIPE_BIT, queryPool, 1);
    }
    
    double getElapsedMs() {
        uint64_t timestamps[2];
        vkGetQueryPoolResults(device, queryPool, 0, 2, sizeof(timestamps), 
                            timestamps, sizeof(uint64_t), VK_QUERY_RESULT_64_BIT);
        
        double nsPerTick = physicalDeviceProps.limits.timestampPeriod;
        return (timestamps[1] - timestamps[0]) * nsPerTick / 1000000.0;
    }
};
```

### 2. Memory Bandwidth Analysis

**Monitor bandwidth usage**:
```cpp
struct BandwidthMonitor {
    size_t bytesRead = 0;
    size_t bytesWritten = 0;
    double elapsedSeconds = 0;
    
    double getReadBandwidthGBps() {
        return (bytesRead / 1e9) / elapsedSeconds;
    }
    
    double getWriteBandwidthGBps() {
        return (bytesWritten / 1e9) / elapsedSeconds;
    }
};
```

### 3. Occupancy Analysis

**Calculate theoretical occupancy**:
```cpp
struct OccupancyCalculator {
    uint32_t calculateOccupancy(
        uint32_t registersPerThread,
        uint32_t sharedMemoryPerBlock,
        uint32_t threadsPerBlock,
        const VkPhysicalDeviceLimits& limits) {
        
        uint32_t maxBlocksByRegs = limits.maxComputeWorkGroupInvocations / registersPerThread;
        uint32_t maxBlocksByShared = limits.maxComputeSharedMemorySize / sharedMemoryPerBlock;
        uint32_t maxBlocksByThreads = limits.maxComputeWorkGroupInvocations / threadsPerBlock;
        
        return std::min({maxBlocksByRegs, maxBlocksByShared, maxBlocksByThreads});
    }
};
```

## Tools and Utilities

### 1. RenderDoc Integration

```cpp
// RenderDoc API integration
#ifdef USE_RENDERDOC
    RENDERDOC_API_1_1_2 *rdoc_api = NULL;
    if (HMODULE mod = GetModuleHandleA("renderdoc.dll")) {
        pRENDERDOC_GetAPI RENDERDOC_GetAPI = 
            (pRENDERDOC_GetAPI)GetProcAddress(mod, "RENDERDOC_GetAPI");
        RENDERDOC_GetAPI(eRENDERDOC_API_Version_1_1_2, (void **)&rdoc_api);
    }
    
    // Trigger capture
    if (rdoc_api) rdoc_api->StartFrameCapture(NULL, NULL);
#endif
```

### 2. NVIDIA Nsight Integration

```cpp
// Nsight markers
void insertNsightMarker(VkCommandBuffer cmd, const char* markerName) {
    if (vkCmdBeginDebugUtilsLabelEXT) {
        VkDebugUtilsLabelEXT label = {
            .sType = VK_STRUCTURE_TYPE_DEBUG_UTILS_LABEL_EXT,
            .pLabelName = markerName,
            .color = {1.0f, 0.0f, 0.0f, 1.0f}
        };
        vkCmdBeginDebugUtilsLabelEXT(cmd, &label);
    }
}
```

### 3. Custom Debug Overlay

```cpp
class DebugOverlay {
    void render() {
        ImGui::Begin("Vulkan Debug Info");
        
        // Memory info
        ImGui::Text("GPU Memory: %.2f / %.2f MB", 
                    currentUsage / 1048576.0f, totalMemory / 1048576.0f);
        
        // Compute metrics
        ImGui::Text("Compute Dispatches: %d", dispatchCount);
        ImGui::Text("Average Dispatch Time: %.3f ms", avgDispatchTime);
        
        // Synchronization info
        ImGui::Text("Pipeline Barriers: %d", barrierCount);
        ImGui::Text("Queue Submits: %d", submitCount);
        
        ImGui::End();
    }
};
```

## Best Practices

1. **Always enable validation layers in debug builds**
2. **Use debug markers for all major operations**
3. **Monitor memory usage continuously**
4. **Profile before optimizing**
5. **Test on multiple GPU vendors**
6. **Keep debug and release shader variants**
7. **Log all Vulkan errors with context**
8. **Use compute shader printf when available**

## Troubleshooting Checklist

- [ ] Validation layers enabled and error-free
- [ ] All resources properly synchronized
- [ ] Memory budgets not exceeded
- [ ] Compute workgroup sizes within limits
- [ ] Proper queue family ownership transfers
- [ ] Descriptor sets correctly bound
- [ ] Pipeline barriers correctly placed
- [ ] No device lost errors
- [ ] Performance within expected bounds
- [ ] Memory leaks checked with VMA stats 