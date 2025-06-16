"""
Base Agent Class - Common functionality for all agents.
Reduces code duplication across agent implementations.
"""

import asyncio
import json
import logging
import websockets
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class AgentMetrics:
    """Standard metrics tracked by all agents"""
    messages_processed: int = 0
    errors_encountered: int = 0
    uptime_seconds: float = 0.0
    last_activity: Optional[datetime] = None
    custom_metrics: Dict[str, Any] = field(default_factory=dict)

class BaseAgent(ABC):
    """
    Base class for all UX-MIRROR agents.
    Provides common functionality like WebSocket connection, heartbeat, metrics tracking.
    """
    
    def __init__(self, agent_id: str, agent_type: str, capabilities: List[str],
                 orchestrator_host: str = "localhost", orchestrator_port: int = 8765):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.capabilities = capabilities
        self.orchestrator_host = orchestrator_host
        self.orchestrator_port = orchestrator_port
        
        # Connection state
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.connected = False
        self.running = False
        
        # Metrics
        self.metrics = AgentMetrics()
        self.start_time = datetime.now()
        
        # Configuration (can be overridden by subclasses)
        self.config = self._get_default_config()
        
        logger.info(f"Initialized {agent_type} agent: {agent_id}")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for the agent"""
        return {
            'heartbeat_interval': 30,  # seconds
            'reconnect_delay': 5,      # seconds
            'max_reconnect_attempts': 10,
            'batch_size': 100,
            'log_level': 'INFO'
        }
    
    async def start(self):
        """Start the agent"""
        self.running = True
        logger.info(f"Starting {self.agent_type} agent: {self.agent_id}")
        
        # Connect to orchestrator
        await self._connect_to_orchestrator()
        
        # Start background tasks
        background_tasks = [
            self._heartbeat_loop(),
            self._metrics_update_loop(),
            self._reconnect_loop(),
            self.run()  # Main agent logic
        ]
        
        try:
            await asyncio.gather(*background_tasks)
        except Exception as e:
            logger.error(f"Agent error: {e}")
        finally:
            await self.stop()
    
    async def stop(self):
        """Stop the agent"""
        logger.info(f"Stopping {self.agent_type} agent: {self.agent_id}")
        self.running = False
        
        if self.websocket:
            await self.websocket.close()
        
        # Allow subclasses to perform cleanup
        await self.cleanup()
    
    async def _connect_to_orchestrator(self):
        """Connect to the orchestrator"""
        uri = f"ws://{self.orchestrator_host}:{self.orchestrator_port}"
        
        try:
            self.websocket = await websockets.connect(uri)
            self.connected = True
            
            # Register with orchestrator
            await self._register()
            
            logger.info(f"Connected to orchestrator at {uri}")
        except Exception as e:
            logger.error(f"Failed to connect to orchestrator: {e}")
            self.connected = False
    
    async def _register(self):
        """Register agent with orchestrator"""
        registration_data = {
            "type": "agent_registration",
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "capabilities": self.capabilities,
            "timestamp": datetime.now().isoformat()
        }
        
        await self.send_message(registration_data)
        
        # Wait for configuration response
        response = await self.websocket.recv()
        config_data = json.loads(response)
        
        if config_data.get("status") == "registered":
            # Update configuration with orchestrator's settings
            if "config" in config_data:
                self.config.update(config_data["config"])
            logger.info(f"Successfully registered with orchestrator")
    
    async def send_message(self, data: Dict[str, Any]):
        """Send message to orchestrator"""
        if not self.connected or not self.websocket:
            logger.warning("Not connected to orchestrator")
            return
        
        try:
            # Always include agent_id
            data["agent_id"] = self.agent_id
            data["timestamp"] = datetime.now().isoformat()
            
            await self.websocket.send(json.dumps(data))
            self.metrics.messages_processed += 1
            self.metrics.last_activity = datetime.now()
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            self.metrics.errors_encountered += 1
            self.connected = False
    
    async def _heartbeat_loop(self):
        """Send periodic heartbeat to orchestrator"""
        while self.running:
            if self.connected:
                heartbeat_data = {
                    "type": "agent_heartbeat",
                    "performance": self.get_performance_metrics()
                }
                await self.send_message(heartbeat_data)
            
            await asyncio.sleep(self.config.get('heartbeat_interval', 30))
    
    async def _metrics_update_loop(self):
        """Update agent metrics periodically"""
        while self.running:
            self.metrics.uptime_seconds = (datetime.now() - self.start_time).total_seconds()
            
            # Allow subclasses to update custom metrics
            await self.update_custom_metrics()
            
            await asyncio.sleep(10)  # Update every 10 seconds
    
    async def _reconnect_loop(self):
        """Attempt to reconnect if connection is lost"""
        reconnect_attempts = 0
        
        while self.running:
            if not self.connected and reconnect_attempts < self.config.get('max_reconnect_attempts', 10):
                logger.info(f"Attempting to reconnect... (attempt {reconnect_attempts + 1})")
                
                try:
                    await self._connect_to_orchestrator()
                    reconnect_attempts = 0  # Reset on successful connection
                except Exception as e:
                    logger.error(f"Reconnection failed: {e}")
                    reconnect_attempts += 1
            
            await asyncio.sleep(self.config.get('reconnect_delay', 5))
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        return {
            "messages_processed": self.metrics.messages_processed,
            "errors_encountered": self.metrics.errors_encountered,
            "uptime_seconds": self.metrics.uptime_seconds,
            "last_activity": self.metrics.last_activity.isoformat() if self.metrics.last_activity else None,
            **self.metrics.custom_metrics
        }
    
    @abstractmethod
    async def run(self):
        """
        Main agent logic - must be implemented by subclasses.
        This method should contain the core functionality of the agent.
        """
        pass
    
    async def cleanup(self):
        """
        Cleanup method called when agent stops.
        Can be overridden by subclasses for custom cleanup.
        """
        pass
    
    async def update_custom_metrics(self):
        """
        Update custom metrics specific to the agent.
        Can be overridden by subclasses.
        """
        pass
    
    # Utility methods for common agent operations
    
    async def report_insight(self, insight_type: str, severity: str, 
                           description: str, recommendations: List[str] = None,
                           data: Dict[str, Any] = None):
        """Report an insight to the orchestrator"""
        insight_data = {
            "type": f"{self.agent_type}_result",
            "insight_type": insight_type,
            "severity": severity,
            "description": description,
            "recommendations": recommendations or [],
            "data": data or {}
        }
        
        await self.send_message(insight_data)
    
    async def log_error(self, error: Exception, context: str = ""):
        """Log an error and report to orchestrator"""
        logger.error(f"{context}: {error}")
        self.metrics.errors_encountered += 1
        
        error_data = {
            "type": "agent_error",
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context
        }
        
        await self.send_message(error_data)
    
    def validate_config(self):
        """Validate agent configuration"""
        required_keys = ['heartbeat_interval', 'reconnect_delay']
        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"Missing required configuration: {key}")