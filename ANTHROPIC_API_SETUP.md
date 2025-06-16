# Anthropic API Setup for UX Mirror Agents

## Overview

This guide helps you set up Anthropic API access with high rate limits for autonomous agent development in the UX Mirror project.

## API Tier Requirements

### Recommended: Scale Tier
- **Rate Limit**: 4,000+ requests per minute
- **Token Limit**: 400,000+ tokens per minute
- **Cost**: Usage-based pricing
- **Best For**: Continuous agent operation

### Minimum: Build Tier
- **Rate Limit**: 1,000 requests per minute
- **Token Limit**: 200,000 tokens per minute
- **Cost**: Lower usage costs
- **Best For**: Development and testing

## Setup Steps

### 1. Create Anthropic Account

1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Sign up for an account
3. Verify your email
4. Complete onboarding

### 2. Upgrade to Higher Tier

1. Navigate to Settings → Plans & Billing
2. Select "Scale" tier for production use
3. Add payment method
4. Set up usage alerts

### 3. Generate API Keys

Create separate API keys for different agents:

```bash
# Naming convention for API keys
ux-mirror-system-architect
ux-mirror-ux-intelligence
ux-mirror-integration
ux-mirror-code-review
ux-mirror-documentation
```

### 4. Secure Storage Setup

#### Option 1: Environment Variables (Development)
```bash
# .env file (DO NOT COMMIT)
ANTHROPIC_API_KEY_SYSTEM_ARCHITECT=sk-ant-...
ANTHROPIC_API_KEY_UX_INTELLIGENCE=sk-ant-...
ANTHROPIC_API_KEY_INTEGRATION=sk-ant-...
ANTHROPIC_API_KEY_CODE_REVIEW=sk-ant-...
ANTHROPIC_API_KEY_DOCUMENTATION=sk-ant-...
```

#### Option 2: GitHub Secrets (Production)
```bash
# Add each key as a GitHub secret
gh secret set ANTHROPIC_API_KEY_SYSTEM_ARCHITECT
gh secret set ANTHROPIC_API_KEY_UX_INTELLIGENCE
gh secret set ANTHROPIC_API_KEY_INTEGRATION
gh secret set ANTHROPIC_API_KEY_CODE_REVIEW
gh secret set ANTHROPIC_API_KEY_DOCUMENTATION
```

#### Option 3: Secure Key Management Service
- AWS Secrets Manager
- Azure Key Vault
- HashiCorp Vault
- Google Secret Manager

### 5. Agent Configuration

Create `agents/config/api_config.py`:

```python
import os
from typing import Dict, Optional
from anthropic import Anthropic
import time
from functools import wraps

class AnthropicConfig:
    """Configuration for Anthropic API access with rate limiting"""
    
    # Rate limits per agent (requests per minute)
    RATE_LIMITS = {
        "system_architect": 800,
        "ux_intelligence": 800,
        "integration": 600,
        "code_review": 600,
        "documentation": 400
    }
    
    # Model selection
    MODEL = "claude-3-opus-20240229"  # Most capable model
    # Alternative: "claude-3-sonnet-20240229" for faster responses
    
    @staticmethod
    def get_api_key(agent_name: str) -> str:
        """Get API key for specific agent"""
        env_var = f"ANTHROPIC_API_KEY_{agent_name.upper()}"
        api_key = os.getenv(env_var)
        if not api_key:
            raise ValueError(f"Missing API key for {agent_name}")
        return api_key
    
    @staticmethod
    def create_client(agent_name: str) -> Anthropic:
        """Create Anthropic client for specific agent"""
        return Anthropic(api_key=AnthropicConfig.get_api_key(agent_name))

class RateLimiter:
    """Rate limiter for API calls"""
    
    def __init__(self, max_calls: int, time_window: int = 60):
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []
    
    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            # Remove old calls outside time window
            self.calls = [call for call in self.calls if now - call < self.time_window]
            
            if len(self.calls) >= self.max_calls:
                sleep_time = self.time_window - (now - self.calls[0])
                if sleep_time > 0:
                    print(f"Rate limit reached. Sleeping for {sleep_time:.2f}s")
                    time.sleep(sleep_time)
                    self.calls = []
            
            self.calls.append(now)
            return func(*args, **kwargs)
        return wrapper

# Agent base class
class BaseAgent:
    """Base class for all agents"""
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.client = AnthropicConfig.create_client(agent_name)
        self.rate_limit = AnthropicConfig.RATE_LIMITS.get(agent_name, 600)
        self.rate_limiter = RateLimiter(self.rate_limit)
    
    @property
    def model(self):
        return AnthropicConfig.MODEL
    
    def send_message(self, messages: list, **kwargs):
        """Send message with rate limiting"""
        return self._send_message_with_limit(messages, **kwargs)
    
    @rate_limiter
    def _send_message_with_limit(self, messages: list, **kwargs):
        """Internal method with rate limiting applied"""
        return self.client.messages.create(
            model=self.model,
            messages=messages,
            **kwargs
        )
```

### 6. Usage Example

Create `agents/system_architect.py`:

```python
from agents.config.api_config import BaseAgent

class SystemArchitectAgent(BaseAgent):
    """System Architect Agent for UX Mirror"""
    
    def __init__(self):
        super().__init__("system_architect")
        self.system_prompt = """You are the System Architect Agent for the UX Mirror project. 
        Your personality is that of a methodical optimizer who is detail-oriented, 
        performance-focused, and an integration specialist."""
    
    def analyze_architecture(self, code_context: str) -> str:
        """Analyze system architecture and provide recommendations"""
        
        messages = [
            {
                "role": "system",
                "content": self.system_prompt
            },
            {
                "role": "user",
                "content": f"Analyze this architecture and provide optimization recommendations:\n\n{code_context}"
            }
        ]
        
        response = self.send_message(
            messages=messages,
            max_tokens=2000,
            temperature=0.7
        )
        
        return response.content[0].text
    
    def design_component(self, requirements: str) -> str:
        """Design a new system component based on requirements"""
        
        messages = [
            {
                "role": "system",
                "content": self.system_prompt
            },
            {
                "role": "user",
                "content": f"Design a component with these requirements:\n\n{requirements}"
            }
        ]
        
        response = self.send_message(
            messages=messages,
            max_tokens=4000,
            temperature=0.8
        )
        
        return response.content[0].text
```

### 7. Multi-Agent Orchestration

Create `agents/orchestrator.py`:

```python
from typing import Dict, List
from agents.system_architect import SystemArchitectAgent
from agents.ux_intelligence import UXIntelligenceAgent
from agents.integration import IntegrationAgent
import asyncio

class AgentOrchestrator:
    """Orchestrates multiple agents for autonomous development"""
    
    def __init__(self):
        self.agents = {
            "system_architect": SystemArchitectAgent(),
            "ux_intelligence": UXIntelligenceAgent(),
            "integration": IntegrationAgent()
        }
    
    async def collaborative_task(self, task_description: str) -> Dict[str, str]:
        """Execute a task collaboratively across multiple agents"""
        
        # System Architect designs the solution
        architecture = await self.agents["system_architect"].analyze_architecture(task_description)
        
        # UX Intelligence provides user experience insights
        ux_analysis = await self.agents["ux_intelligence"].analyze_ux_impact(architecture)
        
        # Integration Specialist ensures everything works together
        integration_plan = await self.agents["integration"].create_integration_plan(
            architecture, ux_analysis
        )
        
        return {
            "architecture": architecture,
            "ux_analysis": ux_analysis,
            "integration_plan": integration_plan
        }
```

### 8. Monitoring and Analytics

Create `agents/monitoring.py`:

```python
import time
from datetime import datetime
from typing import Dict, List
import json

class APIUsageMonitor:
    """Monitor API usage and costs"""
    
    def __init__(self):
        self.usage_log = []
        self.cost_per_1k_tokens = {
            "claude-3-opus-20240229": {"input": 0.015, "output": 0.075},
            "claude-3-sonnet-20240229": {"input": 0.003, "output": 0.015}
        }
    
    def log_usage(self, agent_name: str, model: str, 
                  input_tokens: int, output_tokens: int):
        """Log API usage"""
        
        cost = self.calculate_cost(model, input_tokens, output_tokens)
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent_name,
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost": cost
        }
        
        self.usage_log.append(entry)
        
        # Save to file
        with open("api_usage_log.json", "a") as f:
            json.dump(entry, f)
            f.write("\n")
    
    def calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for API usage"""
        rates = self.cost_per_1k_tokens.get(model, {"input": 0, "output": 0})
        input_cost = (input_tokens / 1000) * rates["input"]
        output_cost = (output_tokens / 1000) * rates["output"]
        return round(input_cost + output_cost, 4)
    
    def get_daily_usage(self) -> Dict[str, float]:
        """Get usage statistics for today"""
        today = datetime.now().date()
        daily_usage = {"total_cost": 0, "total_requests": 0}
        
        for entry in self.usage_log:
            entry_date = datetime.fromisoformat(entry["timestamp"]).date()
            if entry_date == today:
                daily_usage["total_cost"] += entry["cost"]
                daily_usage["total_requests"] += 1
        
        return daily_usage
```

### 9. Testing Setup

Create `tests/test_anthropic_integration.py`:

```python
import pytest
from agents.config.api_config import AnthropicConfig, BaseAgent
import os

def test_api_key_loading():
    """Test that API keys can be loaded"""
    # Set test environment variable
    os.environ["ANTHROPIC_API_KEY_TEST"] = "sk-ant-test-key"
    
    key = AnthropicConfig.get_api_key("test")
    assert key == "sk-ant-test-key"

def test_rate_limiter():
    """Test rate limiting functionality"""
    from agents.config.api_config import RateLimiter
    import time
    
    limiter = RateLimiter(max_calls=2, time_window=1)
    call_times = []
    
    @limiter
    def test_function():
        call_times.append(time.time())
        return "success"
    
    # First two calls should be immediate
    test_function()
    test_function()
    
    # Third call should be delayed
    start = time.time()
    test_function()
    duration = time.time() - start
    
    assert duration >= 0.9  # Should wait ~1 second
```

## Best Practices

### 1. Rate Limit Management
- Implement exponential backoff for rate limit errors
- Use separate API keys for different agents
- Monitor usage to stay within limits
- Cache responses when possible

### 2. Cost Optimization
- Use Claude 3 Sonnet for simpler tasks
- Implement response caching
- Batch similar requests
- Set appropriate max_tokens limits

### 3. Security
- Never commit API keys to version control
- Rotate keys regularly
- Use least privilege principle
- Monitor for unusual usage patterns

### 4. Error Handling
```python
from anthropic import APIError, RateLimitError

try:
    response = agent.send_message(messages)
except RateLimitError:
    # Implement exponential backoff
    time.sleep(60)
    response = agent.send_message(messages)
except APIError as e:
    # Log error and handle gracefully
    logger.error(f"API Error: {e}")
```

## Integration with UX Mirror

### 1. Autonomous Development Flow
```
User Request → Agent Orchestrator → Multiple Agents → Code Generation → Testing → PR Creation
```

### 2. Agent Communication Protocol
- Agents communicate through structured JSON messages
- Shared context maintained in Redis/PostgreSQL
- Event-driven architecture for real-time updates

### 3. Continuous Learning
- Agents learn from code review feedback
- Performance metrics inform optimization
- User interactions guide UX improvements

## Next Steps

1. **Set up Anthropic account** and upgrade to appropriate tier
2. **Generate API keys** for each agent role
3. **Configure secure storage** for API keys
4. **Implement base agent classes** with rate limiting
5. **Create agent orchestration** system
6. **Set up monitoring** and cost tracking
7. **Test integration** with small tasks
8. **Deploy agents** for autonomous development

## Support Resources

- [Anthropic API Documentation](https://docs.anthropic.com)
- [Rate Limits Guide](https://docs.anthropic.com/claude/reference/rate-limits)
- [Pricing Information](https://www.anthropic.com/pricing)
- [Best Practices](https://docs.anthropic.com/claude/docs/best-practices)

---

*Remember: With great API power comes great responsibility. Use rate limits wisely!* 