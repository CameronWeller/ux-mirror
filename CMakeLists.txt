cmake_minimum_required(VERSION 3.10)
project(vulkan_3d_game_of_life)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Set output directories
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)

# Find required packages
find_package(Vulkan REQUIRED)
find_package(glm CONFIG REQUIRED)

# Add VMA include directory only
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/external/vma/include)

# Create shader output directory
file(MAKE_DIRECTORY ${CMAKE_BINARY_DIR}/shaders)

# Create shader compilation target
add_custom_target(compile_shaders
    COMMAND ${CMAKE_COMMAND} -E make_directory ${CMAKE_BINARY_DIR}/shaders
    COMMAND glslc ${CMAKE_CURRENT_SOURCE_DIR}/shaders/game_of_life_3d.comp -o ${CMAKE_BINARY_DIR}/shaders/game_of_life_3d.comp.spv
    DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/shaders/game_of_life_3d.comp
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
)

# Add VMA implementation as a separate library
add_library(VmaImplementation STATIC src/VmaImplementation.cpp)
target_include_directories(VmaImplementation PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/include
    ${CMAKE_CURRENT_SOURCE_DIR}/external/vma/include
    ${Vulkan_INCLUDE_DIRS}
)

# Add executable
add_executable(${PROJECT_NAME}
    src/main.cpp
    src/VulkanContext.cpp
    src/GameOfLife3D.cpp
    src/VulkanMemoryManager.cpp
    src/ComputeShaderDebugger.cpp
)

# Include directories
# (VMA include already added globally above)
target_include_directories(${PROJECT_NAME} PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/include
    ${Vulkan_INCLUDE_DIRS}
)

# Link libraries
target_link_libraries(${PROJECT_NAME} PRIVATE
    Vulkan::Vulkan
    glm::glm
    VmaImplementation
)

# Add shader compilation as a dependency
add_dependencies(${PROJECT_NAME} compile_shaders)

# Copy shaders to build directory
add_custom_command(TARGET ${PROJECT_NAME} POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy_directory
    ${CMAKE_CURRENT_SOURCE_DIR}/shaders
    $<TARGET_FILE_DIR:${PROJECT_NAME}>/shaders
)

# Add tests
enable_testing()
add_subdirectory(tests)

# Install targets
install(TARGETS ${PROJECT_NAME}
    RUNTIME DESTINATION bin
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
)

# Install shaders
install(DIRECTORY ${CMAKE_BINARY_DIR}/shaders/
    DESTINATION bin/shaders
    FILES_MATCHING PATTERN "*.spv"
) 