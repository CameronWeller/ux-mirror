#!/usr/bin/env python3
"""
UX-MIRROR Core Orchestrator Agent
=================================

Head agent that coordinates all sub-agents and manages the feedback loop
between user experience data and system improvements.

Author: UX-MIRROR System
Version: 1.0.0
"""

import asyncio
import logging
import json
import time
import websockets
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from pathlib import Path
import psutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class AgentStatus:
    """Status information for a connected agent"""
    agent_id: str
    capabilities: List[str]
    status: str  # 'online', 'offline', 'busy', 'error'
    last_heartbeat: datetime
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    connection_info: Dict[str, Any] = field(default_factory=dict)

@dataclass
class UXInsight:
    """Comprehensive UX insight from multiple agents"""
    timestamp: datetime
    source_agents: List[str]
    insight_type: str  # 'performance', 'usability', 'accessibility', 'engagement'
    severity: str  # 'low', 'medium', 'high', 'critical'
    description: str
    recommendations: List[str]
    data: Dict[str, Any]

@dataclass
class SystemState:
    """Current state of the UX monitoring system"""
    active_agents: int
    total_insights_generated: int
    avg_response_time: float
    current_monitoring_targets: List[str]
    system_health: str  # 'excellent', 'good', 'degraded', 'critical'
    last_analysis: Optional[datetime] = None

class CoreOrchestrator:
    """
    Core Orchestrator Agent - The central hub of the UX-MIRROR system.
    
    Responsibilities:
    - Coordinate all sub-agents
    - Manage the feedback loop between UX data and improvements
    - Provide unified API for external systems
    - Monitor system health and performance
    - Generate actionable insights from agent data
    """
    
    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        
        # Use port manager for reliable port allocation
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
            from ux_tester.port_manager import get_port_manager
            
            port_manager = get_port_manager()
            allocated_port = port_manager.allocate_port("core_orchestrator", port)
            self.port = allocated_port if allocated_port else port
            logger.info(f"PortManager allocated port {self.port} for core_orchestrator")
        except ImportError as e:
            # Fallback if port manager not available
            self.port = port
            logger.warning(f"PortManager not available ({e}), using default port {port}")
            
        self.running = False
        
        # Agent management
        self.connected_agents: Dict[str, AgentStatus] = {}
        self.agent_connections: Dict[str, websockets.WebSocketServerProtocol] = {}
        
        # Insights and analytics
        self.insights_buffer: List[UXInsight] = []
        self.system_metrics: Dict[str, Any] = {}
        
        # System state
        self.system_state = SystemState(
            active_agents=0,
            total_insights_generated=0,
            avg_response_time=0.0,
            current_monitoring_targets=[],
            system_health="good"
        )
        
        # Configuration
        self.config = {
            'max_insights_buffer': 1000,
            'heartbeat_timeout': 60,  # seconds
            'analysis_interval': 10,  # seconds
            'auto_generate_insights': True,
            'real_time_monitoring': False
        }
        
        # Performance tracking
        self.start_time = datetime.now()
        self.total_messages_processed = 0
        
        logger.info(f"Core Orchestrator initialized on port {self.port}")
    
    async def start(self):
        """Start the Core Orchestrator"""
        self.running = True
        logger.info(f"Starting Core Orchestrator on {self.host}:{self.port}")
        
        # Start WebSocket server for agents
        server = await websockets.serve(
            self._handle_agent_connection,
            self.host,
            self.port
        )
        
        # Start background tasks
        background_tasks = [
            self._monitor_agent_health(),
            self._generate_insights(),
            self._system_health_monitor(),
            self._cleanup_old_data()
        ]
        
        try:
            # Run server and background tasks concurrently
            await asyncio.gather(
                server.wait_closed(),
                *background_tasks
            )
        except Exception as e:
            logger.error(f"Orchestrator error: {e}")
        finally:
            self.running = False
            logger.info("Core Orchestrator stopped")
    
    async def _handle_agent_connection(self, websocket, path="/"):
        """Handle new agent connections"""
        agent_id = None
        
        try:
            logger.info(f"New agent connection from {websocket.remote_address} (path: {path})")
            
            async for message in websocket:
                try:
                    data = json.loads(message)
                    response = await self._process_agent_message(data, websocket)
                    
                    # Store agent_id from registration
                    if data.get("type") == "agent_registration":
                        agent_id = data.get("agent_id")
                        self.agent_connections[agent_id] = websocket
                    
                    # Send response if any
                    if response:
                        await websocket.send(json.dumps(response))
                        
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON from agent: {e}")
                    await websocket.send(json.dumps({"status": "error", "message": "Invalid JSON"}))
                except Exception as e:
                    logger.error(f"Error processing agent message: {e}")
                    await websocket.send(json.dumps({"status": "error", "message": str(e)}))
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Agent {agent_id or 'unknown'} disconnected")
        except Exception as e:
            logger.error(f"Agent connection error: {e}")
        finally:
            # Clean up agent connection
            if agent_id and agent_id in self.agent_connections:
                del self.agent_connections[agent_id]
                self._remove_agent(agent_id)
    
    async def _process_agent_message(self, data: Dict[str, Any], 
                                   websocket: websockets.WebSocketServerProtocol) -> Optional[Dict[str, Any]]:
        """Process messages from agents"""
        message_type = data.get("type")
        agent_id = data.get("agent_id")
        
        self.total_messages_processed += 1
        
        if message_type == "agent_registration":
            return await self._handle_agent_registration(data, websocket)
        elif message_type == "agent_heartbeat":
            return await self._handle_agent_heartbeat(data)
        elif message_type == "visual_analysis_result":
            return await self._handle_visual_analysis(data)
        elif message_type == "metrics_intelligence_result":
            return await self._handle_metrics_intelligence(data)
        elif message_type == "baseline_comparison":
            return await self._handle_baseline_comparison(data)
        elif message_type == "friction_point_detected":
            return await self._handle_friction_point(data)
        else:
            logger.warning(f"Unknown message type from {agent_id}: {message_type}")
            return {"status": "error", "message": "Unknown message type"}
    
    async def _handle_agent_registration(self, data: Dict[str, Any], 
                                       websocket: websockets.WebSocketServerProtocol) -> Dict[str, Any]:
        """Handle agent registration"""
        agent_id = data.get("agent_id")
        capabilities = data.get("capabilities", [])
        
        # Register the agent
        self.connected_agents[agent_id] = AgentStatus(
            agent_id=agent_id,
            capabilities=capabilities,
            status="online",
            last_heartbeat=datetime.now(),
            connection_info={
                "address": str(websocket.remote_address),
                "registered_at": datetime.now().isoformat()
            }
        )
        
        self.system_state.active_agents = len(self.connected_agents)
        
        logger.info(f"Agent registered: {agent_id} with capabilities: {capabilities}")
        
        # Send configuration to agent
        return {
            "status": "registered",
            "agent_id": agent_id,
            "config": self._get_agent_config(agent_id),
            "system_state": {
                "total_agents": len(self.connected_agents),
                "monitoring_active": self.config['real_time_monitoring']
            }
        }
    
    async def _handle_agent_heartbeat(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle agent heartbeat"""
        agent_id = data.get("agent_id")
        
        if agent_id in self.connected_agents:
            agent = self.connected_agents[agent_id]
            agent.last_heartbeat = datetime.now()
            agent.status = "online"
            
            # Update performance metrics
            if "performance" in data:
                agent.performance_metrics.update(data["performance"])
        
        return {"status": "acknowledged"}
    
    async def _handle_visual_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle visual analysis results"""
        analysis = data.get("analysis", {})
        
        # Create insight from visual analysis
        if analysis.get("accessibility_issues") or analysis.get("quality_score", 1.0) < 0.7:
            insight = UXInsight(
                timestamp=datetime.now(),
                source_agents=["visual_analysis_agent"],
                insight_type="usability",
                severity=self._assess_severity(analysis),
                description=self._create_visual_description(analysis),
                recommendations=analysis.get("recommendations", []),
                data=analysis
            )
            
            await self._add_insight(insight)
        
        # Update system metrics
        self.system_metrics["last_visual_analysis"] = analysis
        self.system_state.last_analysis = datetime.now()
        
        return {"status": "processed"}
    
    async def _handle_metrics_intelligence(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle metrics intelligence results"""
        metrics = data.get("metrics", {})
        
        # Process performance insights
        if metrics.get("performance_issues"):
            insight = UXInsight(
                timestamp=datetime.now(),
                source_agents=["metrics_intelligence_agent"],
                insight_type="performance",
                severity="high" if metrics.get("critical_issues") else "medium",
                description="Performance degradation detected",
                recommendations=metrics.get("recommendations", []),
                data=metrics
            )
            
            await self._add_insight(insight)
        
        return {"status": "processed"}
    
    async def _handle_baseline_comparison(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle baseline comparison results"""
        change_score = data.get("change_score", 0.0)
        
        if change_score > 0.3:  # Significant change threshold
            insight = UXInsight(
                timestamp=datetime.now(),
                source_agents=["visual_analysis_agent"],
                insight_type="usability",
                severity="medium",
                description=f"Significant UI change detected (score: {change_score:.2f})",
                recommendations=["Review UI changes for user impact"],
                data=data
            )
            
            await self._add_insight(insight)
        
        return {"status": "processed"}
    
    async def _handle_friction_point(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle friction point detection"""
        insight = UXInsight(
            timestamp=datetime.now(),
            source_agents=["metrics_intelligence_agent"],
            insight_type="engagement",
            severity="high",
            description=data.get("description", "User friction point detected"),
            recommendations=data.get("recommendations", []),
            data=data
        )
        
        await self._add_insight(insight)
        
        return {"status": "processed"}
    
    def _assess_severity(self, analysis: Dict[str, Any]) -> str:
        """Assess severity of visual analysis issues"""
        quality_score = analysis.get("quality_score", 1.0)
        accessibility_issues = len(analysis.get("accessibility_issues", []))
        
        if quality_score < 0.5 or accessibility_issues > 5:
            return "critical"
        elif quality_score < 0.7 or accessibility_issues > 2:
            return "high"
        elif quality_score < 0.8 or accessibility_issues > 0:
            return "medium"
        else:
            return "low"
    
    def _create_visual_description(self, analysis: Dict[str, Any]) -> str:
        """Create description from visual analysis"""
        quality_score = analysis.get("quality_score", 1.0)
        ui_elements = analysis.get("ui_elements_detected", 0)
        accessibility_issues = len(analysis.get("accessibility_issues", []))
        
        desc = f"Visual analysis: Quality score {quality_score:.2f}, {ui_elements} UI elements detected"
        
        if accessibility_issues > 0:
            desc += f", {accessibility_issues} accessibility issues found"
        
        return desc
    
    async def _add_insight(self, insight: UXInsight):
        """Add insight to buffer and process"""
        self.insights_buffer.append(insight)
        self.system_state.total_insights_generated += 1
        
        # Limit buffer size
        if len(self.insights_buffer) > self.config['max_insights_buffer']:
            self.insights_buffer.pop(0)
        
        # Log high severity insights
        if insight.severity in ["high", "critical"]:
            logger.warning(f"High severity insight: {insight.description}")
        
        # Send to interested agents or external systems
        await self._broadcast_insight(insight)
    
    async def _broadcast_insight(self, insight: UXInsight):
        """Broadcast insight to relevant agents or systems"""
        # Could send to external monitoring systems, dashboards, etc.
        # For now, just log
        logger.info(f"Broadcasting insight: {insight.description}")
    
    def _get_agent_config(self, agent_id: str) -> Dict[str, Any]:
        """Get configuration for specific agent"""
        base_config = {
            "monitoring_interval": 5.0,
            "enable_gpu": True,
            "log_level": "INFO"
        }
        
        # Agent-specific configurations
        if agent_id == "visual_analysis_agent":
            base_config.update({
                "quality_threshold": 0.7,
                "change_threshold": 0.1,
                "max_elements_track": 50
            })
        elif agent_id == "metrics_intelligence_agent":
            base_config.update({
                "performance_threshold": 500,  # ms
                "memory_threshold": 0.8,  # 80%
                "batch_size": 100
            })
        
        return base_config
    
    def _remove_agent(self, agent_id: str):
        """Remove disconnected agent"""
        if agent_id in self.connected_agents:
            del self.connected_agents[agent_id]
            self.system_state.active_agents = len(self.connected_agents)
            logger.info(f"Agent removed: {agent_id}")
        
        if agent_id in self.agent_connections:
            del self.agent_connections[agent_id]
    
    async def _monitor_agent_health(self):
        """Monitor health of connected agents"""
        while self.running:
            current_time = datetime.now()
            timeout_threshold = timedelta(seconds=self.config['heartbeat_timeout'])
            
            # Check for timed out agents
            timeout_agents = []
            for agent_id, agent in self.connected_agents.items():
                if current_time - agent.last_heartbeat > timeout_threshold:
                    agent.status = "offline"
                    timeout_agents.append(agent_id)
            
            # Remove timed out agents
            for agent_id in timeout_agents:
                logger.warning(f"Agent timeout: {agent_id}")
                self._remove_agent(agent_id)
            
            await asyncio.sleep(30)  # Check every 30 seconds
    
    async def _generate_insights(self):
        """Generate higher-level insights from agent data"""
        while self.running:
            if self.config['auto_generate_insights'] and len(self.insights_buffer) > 0:
                await self._analyze_insight_patterns()
            
            await asyncio.sleep(self.config['analysis_interval'])
    
    async def _analyze_insight_patterns(self):
        """Analyze patterns in collected insights"""
        recent_insights = [
            insight for insight in self.insights_buffer
            if (datetime.now() - insight.timestamp).total_seconds() < 300  # Last 5 minutes
        ]
        
        if len(recent_insights) < 3:
            return
        
        # Pattern analysis
        insight_types = {}
        severity_counts = {}
        
        for insight in recent_insights:
            insight_types[insight.insight_type] = insight_types.get(insight.insight_type, 0) + 1
            severity_counts[insight.severity] = severity_counts.get(insight.severity, 0) + 1
        
        # Generate meta-insights
        if severity_counts.get("high", 0) > 2:
            meta_insight = UXInsight(
                timestamp=datetime.now(),
                source_agents=["core_orchestrator"],
                insight_type="system",
                severity="critical",
                description=f"Multiple high-severity issues detected: {severity_counts}",
                recommendations=["Immediate attention required", "Review recent changes"],
                data={"pattern_analysis": {"types": insight_types, "severity": severity_counts}}
            )
            
            await self._add_insight(meta_insight)
    
    async def _system_health_monitor(self):
        """Monitor overall system health"""
        while self.running:
            # Calculate system health metrics
            cpu_usage = psutil.cpu_percent(interval=1)
            memory_usage = psutil.virtual_memory().percent
            
            # Assess system health
            health_score = 100
            
            if cpu_usage > 80:
                health_score -= 20
            if memory_usage > 80:
                health_score -= 20
            if len(self.connected_agents) == 0:
                health_score -= 30
            
            # Update system health
            if health_score >= 80:
                self.system_state.system_health = "excellent"
            elif health_score >= 60:
                self.system_state.system_health = "good"
            elif health_score >= 40:
                self.system_state.system_health = "degraded"
            else:
                self.system_state.system_health = "critical"
            
            # Update metrics
            self.system_metrics.update({
                "cpu_usage": cpu_usage,
                "memory_usage": memory_usage,
                "health_score": health_score,
                "uptime": (datetime.now() - self.start_time).total_seconds(),
                "messages_processed": self.total_messages_processed
            })
            
            await asyncio.sleep(60)  # Check every minute
    
    async def _cleanup_old_data(self):
        """Clean up old insights and metrics"""
        while self.running:
            current_time = datetime.now()
            cutoff_time = current_time - timedelta(hours=24)  # Keep last 24 hours
            
            # Remove old insights
            self.insights_buffer = [
                insight for insight in self.insights_buffer
                if insight.timestamp > cutoff_time
            ]
            
            await asyncio.sleep(3600)  # Cleanup every hour
    
    # Public API methods for external access
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status"""
        return {
            "system_state": {
                "active_agents": self.system_state.active_agents,
                "total_insights": self.system_state.total_insights_generated,
                "system_health": self.system_state.system_health,
                "last_analysis": self.system_state.last_analysis.isoformat() if self.system_state.last_analysis else None
            },
            "connected_agents": {
                agent_id: {
                    "capabilities": agent.capabilities,
                    "status": agent.status,
                    "last_heartbeat": agent.last_heartbeat.isoformat()
                }
                for agent_id, agent in self.connected_agents.items()
            },
            "system_metrics": self.system_metrics
        }
    
    def get_recent_insights(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent insights"""
        recent = self.insights_buffer[-limit:] if len(self.insights_buffer) > limit else self.insights_buffer
        
        return [
            {
                "timestamp": insight.timestamp.isoformat(),
                "source_agents": insight.source_agents,
                "type": insight.insight_type,
                "severity": insight.severity,
                "description": insight.description,
                "recommendations": insight.recommendations
            }
            for insight in recent
        ]
    
    async def send_command_to_agent(self, agent_id: str, command: Dict[str, Any]) -> bool:
        """Send command to specific agent"""
        if agent_id in self.agent_connections:
            try:
                await self.agent_connections[agent_id].send(json.dumps(command))
                return True
            except Exception as e:
                logger.error(f"Error sending command to {agent_id}: {e}")
                return False
        return False
    
    async def start_monitoring(self, targets: List[str] = None):
        """Start real-time monitoring"""
        self.config['real_time_monitoring'] = True
        self.system_state.current_monitoring_targets = targets or []
        
        # Send start monitoring command to all agents
        command = {
            "type": "start_monitoring",
            "targets": targets,
            "interval": self.config['analysis_interval']
        }
        
        for agent_id in self.connected_agents:
            await self.send_command_to_agent(agent_id, command)
        
        logger.info("Real-time monitoring started")
    
    async def stop_monitoring(self):
        """Stop real-time monitoring"""
        self.config['real_time_monitoring'] = False
        self.system_state.current_monitoring_targets = []
        
        # Send stop monitoring command to all agents
        command = {"type": "stop_monitoring"}
        
        for agent_id in self.connected_agents:
            await self.send_command_to_agent(agent_id, command)
        
        logger.info("Real-time monitoring stopped")

def main():
    """Run the Core Orchestrator"""
    import argparse
    
    parser = argparse.ArgumentParser(description="UX-MIRROR Core Orchestrator")
    parser.add_argument("--host", default="localhost", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8765, help="Port to bind to")
    parser.add_argument("--auto-insights", action="store_true", 
                       help="Enable automatic insight generation")
    
    args = parser.parse_args()
    
    # Create orchestrator
    orchestrator = CoreOrchestrator(args.host, args.port)
    
    if args.auto_insights:
        orchestrator.config['auto_generate_insights'] = True
    
    try:
        asyncio.run(orchestrator.start())
    except KeyboardInterrupt:
        logger.info("Core Orchestrator stopped by user")
    except Exception as e:
        logger.error(f"Orchestrator failed: {e}")

if __name__ == "__main__":
    main() 