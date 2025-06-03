cmake_minimum_required(VERSION 3.10)

# Add test executable
add_executable(tests
    test_main.cpp
)

target_include_directories(tests PRIVATE
    ${CMAKE_SOURCE_DIR}/include
    ${Vulkan_INCLUDE_DIRS}
)

target_link_libraries(tests PRIVATE
    Vulkan::Vulkan
    glm::glm
    VulkanMemoryAllocator
)

add_test(NAME tests COMMAND tests) 