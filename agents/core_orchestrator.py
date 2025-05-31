#!/usr/bin/env python3
"""
UX-MIRROR Core Orchestrator Agent
==================================

Primary agent responsible for coordinating all sub-agents and managing the
self-programming GPU-driven feedback loop that defines the UX-MIRROR system.

Author: UX-MIRROR System
Version: 1.0.0
"""

import asyncio
import logging
import time
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import websockets
import torch
import psutil
import GPUtil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class AgentStatus:
    """Status information for sub-agents"""
    agent_id: str
    status: str  # 'active', 'idle', 'error', 'initializing'
    last_heartbeat: datetime
    gpu_usage: float
    cpu_usage: float
    memory_usage: float
    current_task: Optional[str] = None
    error_message: Optional[str] = None

@dataclass
class GPUResourceAllocation:
    """GPU resource allocation across agents"""
    metrics_intelligence: float = 0.3
    visual_analysis: float = 0.4
    autonomous_implementation: float = 0.2
    core_orchestrator: float = 0.1

class UXMirrorCoreOrchestrator:
    """
    Primary agent that coordinates all UX-MIRROR system operations.
    
    This agent serves as the central hub for:
    - Agent coordination and communication
    - GPU resource management and allocation
    - Self-programming decision making
    - Quality assurance and deployment validation
    - System evolution and optimization
    """
    
    def __init__(self, config_path: str = "config/orchestrator_config.json"):
        self.config = self._load_config(config_path)
        self.agents: Dict[str, AgentStatus] = {}
        self.gpu_allocation = GPUResourceAllocation()
        self.websocket_server = None
        self.active_connections: Dict[str, websockets.WebSocketServerProtocol] = {}
        
        # GPU and system monitoring
        self.gpu_available = torch.cuda.is_available()
        self.device = torch.device("cuda" if self.gpu_available else "cpu")
        
        # Performance metrics tracking
        self.metrics_history = {
            'coordination_latency': [],
            'gpu_utilization': [],
            'deployment_success_rate': [],
            'system_uptime': time.time()
        }
        
        # Self-programming state
        self.improvement_queue = []
        self.deployment_pending = []
        
        logger.info(f"UX-MIRROR Core Orchestrator initialized on {self.device}")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load orchestrator configuration"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Config file {config_path} not found, using defaults")
            return {
                "websocket_port": 8765,
                "heartbeat_interval": 5.0,
                "max_deployment_queue": 10,
                "gpu_reallocation_threshold": 0.8,
                "coordination_timeout": 10.0
            }
    
    async def start(self):
        """Start the core orchestrator and all sub-agents"""
        logger.info("Starting UX-MIRROR Core Orchestrator...")
        
        # Initialize WebSocket server for agent communication
        self.websocket_server = await websockets.serve(
            self._handle_agent_connection,
            "localhost",
            self.config["websocket_port"]
        )
        
        logger.info(f"WebSocket server started on port {self.config['websocket_port']}")
        
        # Start monitoring and coordination tasks
        tasks = [
            self._monitor_system_health(),
            self._coordinate_agents(),
            self._manage_gpu_resources(),
            self._process_improvement_queue(),
            self._handle_deployments()
        ]
        
        await asyncio.gather(*tasks)
    
    async def _handle_agent_connection(self, websocket, path):
        """Handle incoming connections from sub-agents"""
        agent_id = None
        try:
            # Agent registration
            registration_message = await websocket.recv()
            registration_data = json.loads(registration_message)
            agent_id = registration_data.get("agent_id")
            
            if not agent_id:
                await websocket.send(json.dumps({"error": "Missing agent_id"}))
                return
            
            self.active_connections[agent_id] = websocket
            self.agents[agent_id] = AgentStatus(
                agent_id=agent_id,
                status="initializing",
                last_heartbeat=datetime.now(),
                gpu_usage=0.0,
                cpu_usage=0.0,
                memory_usage=0.0
            )
            
            logger.info(f"Agent {agent_id} connected and registered")
            
            # Send initial GPU allocation
            await self._send_gpu_allocation(agent_id)
            
            # Handle agent messages
            async for message in websocket:
                await self._process_agent_message(agent_id, json.loads(message))
                
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Agent {agent_id} disconnected")
        except Exception as e:
            logger.error(f"Error handling agent {agent_id}: {e}")
        finally:
            if agent_id:
                self.active_connections.pop(agent_id, None)
                self.agents.pop(agent_id, None)
    
    async def _process_agent_message(self, agent_id: str, message: Dict[str, Any]):
        """Process messages from sub-agents"""
        message_type = message.get("type")
        
        if message_type == "heartbeat":
            await self._handle_heartbeat(agent_id, message)
        elif message_type == "status_update":
            await self._handle_status_update(agent_id, message)
        elif message_type == "recommendation":
            await self._handle_recommendation(agent_id, message)
        elif message_type == "alert":
            await self._handle_alert(agent_id, message)
        elif message_type == "resource_request":
            await self._handle_resource_request(agent_id, message)
        elif message_type == "deployment_request":
            await self._handle_deployment_request(agent_id, message)
        else:
            logger.warning(f"Unknown message type from {agent_id}: {message_type}")
    
    async def _handle_heartbeat(self, agent_id: str, message: Dict[str, Any]):
        """Process heartbeat from sub-agent"""
        if agent_id in self.agents:
            self.agents[agent_id].last_heartbeat = datetime.now()
            self.agents[agent_id].status = message.get("status", "active")
            self.agents[agent_id].gpu_usage = message.get("gpu_usage", 0.0)
            self.agents[agent_id].cpu_usage = message.get("cpu_usage", 0.0)
            self.agents[agent_id].memory_usage = message.get("memory_usage", 0.0)
    
    async def _handle_recommendation(self, agent_id: str, message: Dict[str, Any]):
        """Process improvement recommendations from sub-agents"""
        recommendation = {
            'source_agent': agent_id,
            'type': message.get('recommendation_type'),
            'priority': message.get('priority', 'medium'),
            'data': message.get('data'),
            'timestamp': datetime.now(),
            'processed': False
        }
        
        self.improvement_queue.append(recommendation)
        logger.info(f"Added recommendation from {agent_id}: {recommendation['type']}")
        
        # Send acknowledgment
        await self._send_to_agent(agent_id, {
            "type": "recommendation_ack",
            "recommendation_id": len(self.improvement_queue) - 1
        })
    
    async def _handle_deployment_request(self, agent_id: str, message: Dict[str, Any]):
        """Handle deployment requests from Autonomous Implementation Agent"""
        if agent_id != "autonomous_implementation":
            logger.warning(f"Deployment request from unauthorized agent: {agent_id}")
            return
        
        deployment = {
            'request_id': message.get('request_id'),
            'code_changes': message.get('code_changes'),
            'target_platforms': message.get('target_platforms', []),
            'validation_tests': message.get('validation_tests', []),
            'rollback_plan': message.get('rollback_plan'),
            'estimated_impact': message.get('estimated_impact'),
            'timestamp': datetime.now()
        }
        
        # Validate deployment request
        validation_result = await self._validate_deployment(deployment)
        
        if validation_result['approved']:
            self.deployment_pending.append(deployment)
            await self._send_to_agent(agent_id, {
                "type": "deployment_approved",
                "request_id": deployment['request_id']
            })
            logger.info(f"Deployment approved: {deployment['request_id']}")
        else:
            await self._send_to_agent(agent_id, {
                "type": "deployment_rejected",
                "request_id": deployment['request_id'],
                "reason": validation_result['reason']
            })
            logger.warning(f"Deployment rejected: {validation_result['reason']}")
    
    async def _validate_deployment(self, deployment: Dict[str, Any]) -> Dict[str, Any]:
        """Validate deployment request for safety and quality"""
        # TODO: Implement comprehensive validation logic
        # - Static code analysis
        # - Security scanning
        # - Performance impact assessment
        # - Cross-platform compatibility check
        
        # For now, basic validation
        required_fields = ['code_changes', 'target_platforms', 'rollback_plan']
        for field in required_fields:
            if field not in deployment or not deployment[field]:
                return {
                    'approved': False,
                    'reason': f'Missing required field: {field}'
                }
        
        return {'approved': True, 'reason': 'Validation passed'}
    
    async def _manage_gpu_resources(self):
        """Dynamically manage GPU resource allocation across agents"""
        while True:
            try:
                if self.gpu_available:
                    # Get current GPU utilization
                    gpus = GPUtil.getGPUs()
                    if gpus:
                        current_utilization = gpus[0].load
                        
                        # Reallocate based on agent workloads
                        await self._optimize_gpu_allocation(current_utilization)
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in GPU resource management: {e}")
                await asyncio.sleep(60)
    
    async def _optimize_gpu_allocation(self, current_utilization: float):
        """Optimize GPU allocation based on current workloads"""
        # Get agent workload demands
        workload_demands = {}
        for agent_id, agent_status in self.agents.items():
            if agent_status.status == "active":
                workload_demands[agent_id] = agent_status.gpu_usage
        
        # Dynamically adjust allocations
        if current_utilization > self.config["gpu_reallocation_threshold"]:
            # High utilization - optimize for critical tasks
            if "metrics_intelligence" in workload_demands:
                self.gpu_allocation.metrics_intelligence = min(0.4, 
                    self.gpu_allocation.metrics_intelligence + 0.1)
                self.gpu_allocation.visual_analysis = max(0.3, 
                    self.gpu_allocation.visual_analysis - 0.1)
        
        # Send updated allocations to agents
        for agent_id in self.active_connections:
            await self._send_gpu_allocation(agent_id)
    
    async def _send_gpu_allocation(self, agent_id: str):
        """Send GPU allocation to specific agent"""
        allocation_map = {
            "metrics_intelligence": self.gpu_allocation.metrics_intelligence,
            "visual_analysis": self.gpu_allocation.visual_analysis,
            "autonomous_implementation": self.gpu_allocation.autonomous_implementation,
            "core_orchestrator": self.gpu_allocation.core_orchestrator
        }
        
        await self._send_to_agent(agent_id, {
            "type": "gpu_allocation",
            "allocation": allocation_map.get(agent_id, 0.1),
            "total_allocation": allocation_map
        })
    
    async def _send_to_agent(self, agent_id: str, message: Dict[str, Any]):
        """Send message to specific agent"""
        if agent_id in self.active_connections:
            try:
                await self.active_connections[agent_id].send(json.dumps(message))
            except Exception as e:
                logger.error(f"Failed to send message to {agent_id}: {e}")
    
    async def _coordinate_agents(self):
        """Main coordination loop"""
        while True:
            try:
                # Check agent health
                current_time = datetime.now()
                for agent_id, agent_status in list(self.agents.items()):
                    time_since_heartbeat = (current_time - agent_status.last_heartbeat).total_seconds()
                    
                    if time_since_heartbeat > self.config["coordination_timeout"]:
                        logger.warning(f"Agent {agent_id} has not sent heartbeat in {time_since_heartbeat}s")
                        agent_status.status = "error"
                        agent_status.error_message = "Heartbeat timeout"
                
                # Log system status
                active_agents = sum(1 for a in self.agents.values() if a.status == "active")
                logger.info(f"Active agents: {active_agents}/{len(self.agents)}")
                
                await asyncio.sleep(self.config["heartbeat_interval"])
                
            except Exception as e:
                logger.error(f"Error in agent coordination: {e}")
                await asyncio.sleep(10)
    
    async def _monitor_system_health(self):
        """Monitor overall system health and performance"""
        while True:
            try:
                # System metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                
                # GPU metrics
                gpu_utilization = 0.0
                if self.gpu_available:
                    gpus = GPUtil.getGPUs()
                    if gpus:
                        gpu_utilization = gpus[0].load * 100
                
                # Update metrics history
                self.metrics_history['gpu_utilization'].append(gpu_utilization)
                if len(self.metrics_history['gpu_utilization']) > 1000:
                    self.metrics_history['gpu_utilization'].pop(0)
                
                # Calculate uptime
                uptime_hours = (time.time() - self.metrics_history['system_uptime']) / 3600
                
                logger.info(f"System Health - CPU: {cpu_percent}%, Memory: {memory.percent}%, GPU: {gpu_utilization}%, Uptime: {uptime_hours:.1f}h")
                
                await asyncio.sleep(60)  # Monitor every minute
                
            except Exception as e:
                logger.error(f"Error in system health monitoring: {e}")
                await asyncio.sleep(60)
    
    async def _process_improvement_queue(self):
        """Process improvement recommendations from all agents"""
        while True:
            try:
                if self.improvement_queue:
                    # Sort by priority and timestamp
                    self.improvement_queue.sort(
                        key=lambda x: (
                            {'high': 0, 'medium': 1, 'low': 2}[x['priority']],
                            x['timestamp']
                        )
                    )
                    
                    # Process next recommendation
                    recommendation = self.improvement_queue.pop(0)
                    await self._process_recommendation(recommendation)
                
                await asyncio.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                logger.error(f"Error processing improvement queue: {e}")
                await asyncio.sleep(10)
    
    async def _process_recommendation(self, recommendation: Dict[str, Any]):
        """Process a single improvement recommendation"""
        logger.info(f"Processing recommendation from {recommendation['source_agent']}: {recommendation['type']}")
        
        # Forward to Autonomous Implementation Agent for code generation
        if "autonomous_implementation" in self.active_connections:
            await self._send_to_agent("autonomous_implementation", {
                "type": "implement_recommendation",
                "recommendation": recommendation
            })
        else:
            logger.warning("Autonomous Implementation Agent not available")
    
    async def _handle_deployments(self):
        """Handle pending deployments"""
        while True:
            try:
                if self.deployment_pending:
                    deployment = self.deployment_pending.pop(0)
                    success = await self._execute_deployment(deployment)
                    
                    # Update metrics
                    self.metrics_history['deployment_success_rate'].append(1 if success else 0)
                    if len(self.metrics_history['deployment_success_rate']) > 100:
                        self.metrics_history['deployment_success_rate'].pop(0)
                
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Error handling deployments: {e}")
                await asyncio.sleep(30)
    
    async def _execute_deployment(self, deployment: Dict[str, Any]) -> bool:
        """Execute a validated deployment"""
        # TODO: Implement actual deployment logic
        # - Apply code changes
        # - Run validation tests
        # - Monitor for issues
        # - Rollback if necessary
        
        logger.info(f"Executing deployment: {deployment['request_id']}")
        
        # Simulate deployment process
        await asyncio.sleep(2)
        
        # For now, simulate 90% success rate
        import random
        success = random.random() < 0.9
        
        if success:
            logger.info(f"Deployment successful: {deployment['request_id']}")
        else:
            logger.error(f"Deployment failed: {deployment['request_id']}")
        
        return success

def main():
    """Main entry point for the Core Orchestrator"""
    orchestrator = UXMirrorCoreOrchestrator()
    
    try:
        asyncio.run(orchestrator.start())
    except KeyboardInterrupt:
        logger.info("Core Orchestrator shutting down...")
    except Exception as e:
        logger.error(f"Core Orchestrator error: {e}")

if __name__ == "__main__":
    main() 