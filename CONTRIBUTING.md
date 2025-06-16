# Contributing to UX Mirror

Thank you for your interest in contributing to UX Mirror! This document provides guidelines and instructions for contributing to the project.

## 🎯 Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md). Please read it before contributing.

## 🚀 Getting Started

### Prerequisites

Before contributing, ensure you have:

1. **Development Environment**
   - C++20 compatible compiler (GCC 11+, Clang 13+, MSVC 2022+)
   - CMake 3.20+
   - Vulkan SDK 1.3+
   - AMD ROCm 5.0+ or NVIDIA CUDA 11.0+
   - Python 3.8+ (for tooling)
   - Git with LFS support

2. **Recommended Tools**
   - clang-format (for code formatting)
   - clang-tidy (for static analysis)
   - Valgrind or AddressSanitizer (for memory debugging)
   - RenderDoc (for graphics debugging)

### Setting Up Your Development Environment

```bash
# Fork and clone the repository
git clone https://github.com/YOUR_USERNAME/ux-mirror.git
cd ux-mirror

# Add upstream remote
git remote add upstream https://github.com/ORIGINAL_OWNER/ux-mirror.git

# Install development dependencies
pip install -r requirements-dev.txt

# Set up pre-commit hooks
pre-commit install

# Build the project
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Debug -DBUILD_TESTS=ON
cmake --build . --parallel
```

## 📝 Development Workflow

### 1. Find or Create an Issue

- Check existing issues for something you'd like to work on
- If creating a new issue, use our issue templates
- Comment on the issue to let others know you're working on it

### 2. Create a Feature Branch

```bash
# Update your local main branch
git checkout main
git pull upstream main

# Create a feature branch
git checkout -b feature/your-feature-name
```

### 3. Make Your Changes

- Write clean, well-documented code
- Follow our coding standards (see below)
- Add tests for new functionality
- Update documentation as needed

### 4. Test Your Changes

```bash
# Run all tests
cd build
ctest --verbose

# Run specific test suite
ctest -R TestSuiteName

# Run with sanitizers
cmake .. -DENABLE_SANITIZERS=ON
cmake --build . --parallel
ctest
```

### 5. Submit a Pull Request

- Push your branch to your fork
- Create a pull request against the main branch
- Fill out the PR template completely
- Link the related issue(s)

## 💻 Coding Standards

### C++ Style Guide

We follow the [Google C++ Style Guide](https://google.github.io/styleguide/cppguide.html) with these modifications:

1. **File Naming**
   - Headers: `.hpp`
   - Source files: `.cpp`
   - Use snake_case for filenames

2. **Code Formatting**
   - Use the provided `.clang-format` file
   - Run `clang-format -i src/**/*.{hpp,cpp}` before committing

3. **Naming Conventions**
   ```cpp
   // Classes and structs: PascalCase
   class MetricsCollector {
   public:
       // Public methods: camelCase
       void collectMetrics();
       
   private:
       // Private members: m_ prefix + camelCase
       int m_sampleRate;
       
       // Constants: k prefix + PascalCase
       static constexpr int kMaxSamples = 1000;
   };
   
   // Functions: camelCase
   void processData();
   
   // Namespaces: snake_case
   namespace ux_mirror {
   namespace metrics {
   }
   }
   ```

4. **Memory Management**
   - Prefer RAII and smart pointers
   - Use `std::unique_ptr` for single ownership
   - Use `std::shared_ptr` sparingly
   - Document any raw pointer usage

5. **Error Handling**
   - Use `std::expected` or `std::optional` for recoverable errors
   - Use exceptions for unrecoverable errors
   - Always check Vulkan/HIP return codes

### Python Style Guide

For Python tooling, follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with:
- Line length: 100 characters
- Use type hints for all functions
- Use `black` for formatting

## 🧪 Testing Guidelines

### Test Categories

1. **Unit Tests**
   - Test individual components in isolation
   - Use Google Test framework
   - Aim for >80% code coverage

2. **Integration Tests**
   - Test component interactions
   - Test Vulkan-HIP interop
   - Test data flow between systems

3. **Performance Tests**
   - Benchmark critical paths
   - Track performance regressions
   - Test GPU utilization

### Writing Tests

```cpp
#include <gtest/gtest.h>
#include "ux_mirror/metrics/collector.hpp"

namespace ux_mirror::tests {

class MetricsCollectorTest : public ::testing::Test {
protected:
    void SetUp() override {
        // Test setup
    }
    
    void TearDown() override {
        // Test cleanup
    }
};

TEST_F(MetricsCollectorTest, CollectsBasicMetrics) {
    // Arrange
    MetricsCollector collector;
    
    // Act
    auto metrics = collector.collect();
    
    // Assert
    EXPECT_TRUE(metrics.has_value());
    EXPECT_GT(metrics->frameTime, 0.0f);
}

} // namespace ux_mirror::tests
```

## 📚 Documentation

### Code Documentation

- Use Doxygen-style comments for all public APIs
- Include examples in documentation
- Document any non-obvious implementation details

```cpp
/**
 * @brief Collects performance metrics from the GPU
 * 
 * This class provides real-time collection of GPU performance metrics
 * including utilization, memory usage, and timing information.
 * 
 * @example
 * ```cpp
 * MetricsCollector collector;
 * auto metrics = collector.collect();
 * if (metrics) {
 *     std::cout << "GPU Usage: " << metrics->gpuUsage << "%\n";
 * }
 * ```
 */
class MetricsCollector {
    // ...
};
```

### User Documentation

- Update relevant documentation in the `docs/` directory
- Include code examples
- Add diagrams where helpful (use Mermaid)

## 🎯 Areas We Need Help

### High Priority

1. **Vulkan Ray Tracing**
   - Optimize ray tracing pipeline
   - Implement efficient BVH updates
   - Add support for RT extensions

2. **HIP Kernel Optimization**
   - Optimize memory access patterns
   - Implement efficient reduction operations
   - Add multi-GPU support

3. **Cross-Platform Testing**
   - Test on various GPU vendors
   - Ensure consistent behavior
   - Performance profiling

### Good First Issues

Look for issues labeled `good first issue` for:
- Documentation improvements
- Simple bug fixes
- Test coverage improvements
- Code cleanup tasks

## 🔄 Pull Request Process

1. **Before Submitting**
   - Ensure all tests pass
   - Run code formatters
   - Update documentation
   - Add changelog entry

2. **PR Requirements**
   - Clear description of changes
   - Link to related issue(s)
   - Screenshots/videos for UI changes
   - Performance impact analysis

3. **Review Process**
   - At least one maintainer approval required
   - All CI checks must pass
   - Address review feedback promptly

## 🏗️ Architecture Decisions

When proposing significant changes:

1. Create an Architecture Decision Record (ADR)
2. Discuss in an issue before implementing
3. Consider performance implications
4. Ensure backward compatibility

## 📊 Performance Considerations

- Profile before and after changes
- Document performance impacts
- Consider GPU memory usage
- Optimize for real-time constraints

## 🤝 Community

- Join our [Discord server](https://discord.gg/YOUR_INVITE)
- Participate in design discussions
- Help other contributors
- Share your use cases

## ❓ Questions?

- Check the [FAQ](docs/FAQ.md)
- Ask in Discord
- Open a discussion on GitHub

Thank you for contributing to UX Mirror! Your efforts help make UX analysis and optimization accessible to everyone. 