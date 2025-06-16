cmake_minimum_required(VERSION 3.20)
project(UXMirror VERSION 0.1.0 LANGUAGES CXX)

# Set C++ standard
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Project options
option(BUILD_TESTS "Build test suite" ON)
option(BUILD_EXAMPLES "Build example applications" ON)
option(BUILD_DOCUMENTATION "Build documentation" OFF)
option(ENABLE_SANITIZERS "Enable sanitizers for debug builds" OFF)
option(USE_CUDA "Use NVIDIA CUDA instead of AMD HIP" OFF)

# Set default build type
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE "Release" CACHE STRING "Build type" FORCE)
endif()

# Output directories
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)

# Find required packages
find_package(Vulkan REQUIRED)
find_package(Threads REQUIRED)

# Find compute backend
if(USE_CUDA)
    find_package(CUDAToolkit REQUIRED)
    set(COMPUTE_BACKEND "CUDA")
    set(COMPUTE_LIBRARIES CUDA::cudart CUDA::cuda_driver)
else()
    find_package(hip REQUIRED)
    set(COMPUTE_BACKEND "HIP")
    set(COMPUTE_LIBRARIES hip::device)
endif()

# Compiler flags
if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
    add_compile_options(-Wall -Wextra -Wpedantic)
    if(CMAKE_BUILD_TYPE STREQUAL "Debug")
        add_compile_options(-g -O0)
        if(ENABLE_SANITIZERS)
            add_compile_options(-fsanitize=address -fsanitize=undefined)
            add_link_options(-fsanitize=address -fsanitize=undefined)
        endif()
    else()
        add_compile_options(-O3 -march=native)
    endif()
elseif(MSVC)
    add_compile_options(/W4)
    if(CMAKE_BUILD_TYPE STREQUAL "Debug")
        add_compile_options(/Od /Zi)
    else()
        add_compile_options(/O2)
    endif()
endif()

# Add subdirectories
add_subdirectory(core)
add_subdirectory(analysis)
add_subdirectory(intelligence)
add_subdirectory(integration)

if(BUILD_TESTS)
    enable_testing()
    add_subdirectory(tests)
endif()

if(BUILD_EXAMPLES)
    add_subdirectory(examples)
endif()

if(BUILD_DOCUMENTATION)
    add_subdirectory(docs)
endif()

# Install rules
include(GNUInstallDirs)

install(DIRECTORY include/ux_mirror
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)

# Package configuration
include(CMakePackageConfigHelpers)

configure_package_config_file(
    ${CMAKE_CURRENT_SOURCE_DIR}/cmake/UXMirrorConfig.cmake.in
    ${CMAKE_CURRENT_BINARY_DIR}/UXMirrorConfig.cmake
    INSTALL_DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/UXMirror
)

write_basic_package_version_file(
    ${CMAKE_CURRENT_BINARY_DIR}/UXMirrorConfigVersion.cmake
    VERSION ${PROJECT_VERSION}
    COMPATIBILITY SameMajorVersion
)

install(FILES
    ${CMAKE_CURRENT_BINARY_DIR}/UXMirrorConfig.cmake
    ${CMAKE_CURRENT_BINARY_DIR}/UXMirrorConfigVersion.cmake
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/UXMirror
)

# Summary
message(STATUS "")
message(STATUS "UX Mirror Configuration Summary:")
message(STATUS "  Version:          ${PROJECT_VERSION}")
message(STATUS "  Build Type:       ${CMAKE_BUILD_TYPE}")
message(STATUS "  Compute Backend:  ${COMPUTE_BACKEND}")
message(STATUS "  Build Tests:      ${BUILD_TESTS}")
message(STATUS "  Build Examples:   ${BUILD_EXAMPLES}")
message(STATUS "  Build Docs:       ${BUILD_DOCUMENTATION}")
message(STATUS "  Sanitizers:       ${ENABLE_SANITIZERS}")
message(STATUS "") 