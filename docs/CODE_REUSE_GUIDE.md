# Code Reuse Guide for UX-MIRROR & 3D Game of Life

This guide outlines strategies and patterns for maximizing code reuse across the codebase, reducing duplication and improving maintainability.

## Table of Contents
1. [Core Principles](#core-principles)
2. [Shared Components](#shared-components)
3. [Design Patterns](#design-patterns)
4. [Refactoring Strategies](#refactoring-strategies)
5. [Best Practices](#best-practices)
6. [Examples](#examples)

## Core Principles

### 1. **DRY (Don't Repeat Yourself)**
- Extract common functionality into shared modules
- Use inheritance and composition effectively
- Create reusable utilities for common operations

### 2. **Single Responsibility**
- Each module/class should have one clear purpose
- Makes code more reusable and testable

### 3. **Dependency Injection**
- Pass dependencies rather than hardcoding them
- Makes components more flexible and reusable

## Shared Components

### 1. **Configuration Management**
```python
# Instead of multiple config loading implementations:
from src.common.config_manager import get_config, get_agent_config

# Usage in any module:
api_key = get_config('openai_api_key')
agent_config = get_agent_config('visual_analysis_agent')
```

### 2. **Base Agent Class**
```python
# All agents should inherit from BaseAgent:
from src.common.base_agent import BaseAgent

class MyCustomAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="my_agent",
            agent_type="custom",
            capabilities=["analyze", "report"]
        )
    
    async def run(self):
        # Your agent logic here
        pass
```

### 3. **Common Utilities**
```python
from src.common.utils import (
    ensure_directory,
    safe_json_load,
    safe_json_save,
    Timer,
    async_retry,
    setup_logger
)

# Use throughout the codebase:
data = safe_json_load('config.json')
ensure_directory('output/results')

with Timer("Processing"):
    # Your code here
    pass
```

### 4. **Singleton Pattern Usage**
```python
# Existing singletons:
from src.ux_tester.port_manager import get_port_manager
from src.capture.screenshot_handler import get_screenshot_handler
from src.analysis.ui_element_detector import get_ui_detector

# Use the singleton instances:
port_manager = get_port_manager()
port = port_manager.allocate_port("my_service")
```

## Design Patterns

### 1. **Factory Pattern for Similar Objects**
```python
class AgentFactory:
    """Create agents based on type"""
    
    @staticmethod
    def create_agent(agent_type: str, config: dict):
        agents = {
            'visual': VisualAnalysisAgent,
            'metrics': MetricsIntelligenceAgent,
            'baseline': BaselineComparisonAgent
        }
        
        agent_class = agents.get(agent_type)
        if agent_class:
            return agent_class(**config)
        raise ValueError(f"Unknown agent type: {agent_type}")
```

### 2. **Decorator Pattern for Common Functionality**
```python
# Use decorators for cross-cutting concerns:
from src.common.utils import async_retry, measure_performance

@async_retry(max_attempts=3)
@measure_performance
async def fetch_data(url: str):
    # Your code here
    pass
```

### 3. **Strategy Pattern for Algorithms**
```python
class AnalysisStrategy(ABC):
    @abstractmethod
    def analyze(self, data): pass

class VisualAnalysisStrategy(AnalysisStrategy):
    def analyze(self, data):
        # Visual analysis logic
        pass

class MetricsAnalysisStrategy(AnalysisStrategy):
    def analyze(self, data):
        # Metrics analysis logic
        pass
```

## Refactoring Strategies

### 1. **Extract Common Code**
```python
# Before: Duplicated in multiple files
def load_config():
    with open('config.json') as f:
        return json.load(f)

# After: Use shared utility
from src.common.utils import safe_json_load
config = safe_json_load('config.json')
```

### 2. **Consolidate Similar Classes**
```python
# Instead of multiple similar agent classes:
class BaseMonitoringAgent(BaseAgent):
    """Base class for all monitoring agents"""
    
    def __init__(self, monitor_type: str, **kwargs):
        super().__init__(**kwargs)
        self.monitor_type = monitor_type
    
    async def monitor(self):
        # Common monitoring logic
        pass
```

### 3. **Use Composition Over Inheritance**
```python
# Compose functionality using mixins:
class LoggingMixin:
    def log_activity(self, activity: str):
        logger.info(f"{self.__class__.__name__}: {activity}")

class MetricsMixin:
    def track_metric(self, name: str, value: float):
        self.metrics[name] = value

class MyAgent(BaseAgent, LoggingMixin, MetricsMixin):
    # Inherits all functionality
    pass
```

## Best Practices

### 1. **Import Organization**
```python
# Create __init__.py files to expose common interfaces:
# src/common/__init__.py
from .config_manager import get_config, get_agent_config
from .base_agent import BaseAgent
from .utils import *

# Then import simply:
from src.common import get_config, BaseAgent, ensure_directory
```

### 2. **Configuration Templates**
```python
# Define configuration schemas:
from dataclasses import dataclass

@dataclass
class AgentConfig:
    heartbeat_interval: int = 30
    batch_size: int = 100
    retry_attempts: int = 3
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})
```

### 3. **Error Handling Patterns**
```python
# Use consistent error handling:
from src.common.utils import SafeExecutor

with SafeExecutor("database_operation", default_return=[]):
    result = database.query("SELECT * FROM users")
    # Errors are logged but don't crash the app
```

### 4. **Testing Utilities**
```python
# Create test fixtures and utilities:
class BaseTestCase:
    """Base class for all tests"""
    
    @classmethod
    def setUpClass(cls):
        cls.config = get_config()
        cls.temp_dir = ensure_directory('tests/temp')
    
    def create_mock_agent(self, agent_type: str):
        # Common mock creation logic
        pass
```

## Examples

### Example 1: Refactoring Agent Creation
```python
# Before: Duplicated in each agent file
class VisualAgent:
    def __init__(self):
        self.config = self.load_config()
        self.websocket = None
        self.connected = False
        self.setup_logging()
        self.connect_to_orchestrator()
    
    def load_config(self):
        # Duplicate config loading
        pass
    
    def connect_to_orchestrator(self):
        # Duplicate connection logic
        pass

# After: Using BaseAgent
class VisualAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="visual_agent_001",
            agent_type="visual_analysis",
            capabilities=["screenshot", "ui_detection", "accessibility"]
        )
    
    async def run(self):
        # Only the unique logic for this agent
        while self.running:
            screenshot = await self.capture_screenshot()
            analysis = await self.analyze_image(screenshot)
            await self.report_insight("visual", "medium", 
                                    f"Found {len(analysis.ui_elements)} UI elements")
```

### Example 2: Consolidating Utilities
```python
# Before: Scattered across files
# file1.py
def ensure_dir(path):
    Path(path).mkdir(exist_ok=True)

# file2.py
def create_directory(directory):
    os.makedirs(directory, exist_ok=True)

# After: Use common utility
from src.common.utils import ensure_directory

# Everywhere:
output_dir = ensure_directory('results/analysis')
```

### Example 3: Configuration Consolidation
```python
# Before: Each module loads config differently
# agent1.py
config = json.load(open('agent1_config.json'))

# agent2.py
config = {}
with open('config.env') as f:
    for line in f:
        k, v = line.split('=')
        config[k] = v

# After: Unified configuration
from src.common.config_manager import get_config, get_agent_config

# Any module:
api_key = get_config('anthropic_api_key')
my_config = get_agent_config('my_agent')
```

## Migration Checklist

When refactoring existing code:

- [ ] Identify duplicate code patterns
- [ ] Extract common functionality to shared modules
- [ ] Update imports to use shared components
- [ ] Test thoroughly to ensure no regressions
- [ ] Update documentation
- [ ] Remove old duplicate code
- [ ] Add deprecation warnings if needed

## Performance Considerations

1. **Lazy Loading**: Import heavy modules only when needed
2. **Caching**: Use `@lru_cache` for expensive operations
3. **Connection Pooling**: Reuse connections (WebSocket, database)
4. **Batch Operations**: Process data in batches when possible

## Future Improvements

1. **Plugin System**: Create a plugin architecture for easy extension
2. **Service Registry**: Central registry for all services/agents
3. **Event Bus**: Decouple components using events
4. **Dependency Container**: Manage dependencies centrally

By following these patterns and using the shared components, you can significantly reduce code duplication and improve maintainability across the project.