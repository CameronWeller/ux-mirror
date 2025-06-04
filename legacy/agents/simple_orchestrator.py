#!/usr/bin/env python3
"""
UX-MIRROR Simple Orchestrator
=============================

Lightweight coordinator for the three main UX-MIRROR agents:
- Visual Analysis Agent
- Metrics Intelligence Agent  
- Autonomous Implementation Agent

This orchestrator focuses on simple message passing and basic coordination,
not complex system management.

Author: UX-MIRROR System
Version: 1.0.0
"""

import asyncio
import logging
import json
from typing import Dict, Any
from datetime import datetime
import websockets

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SimpleOrchestrator:
    """
    Lightweight orchestrator that just coordinates agent communication
    and basic task routing.
    """
    
    def __init__(self, port: int = 8765):
        self.port = port
        self.server = None
        self.connected_agents: Dict[str, websockets.WebSocketServerProtocol] = {}
        
        logger.info("Simple UX-MIRROR Orchestrator initialized")
    
    async def start(self):
        """Start the simple orchestrator server"""
        logger.info(f"Starting Simple Orchestrator on port {self.port}...")
        
        self.server = await websockets.serve(
            self._handle_agent_connection,
            "localhost",
            self.port
        )
        
        logger.info(f"Orchestrator listening on ws://localhost:{self.port}")
        
        # Simple coordination loop
        await self._coordinate()
    
    async def _handle_agent_connection(self, websocket, path):
        """Handle agent connections"""
        agent_id = None
        try:
            # Wait for agent registration
            registration_message = await websocket.recv()
            registration_data = json.loads(registration_message)
            agent_id = registration_data.get("agent_id")
            
            if not agent_id:
                await websocket.send(json.dumps({"error": "Missing agent_id"}))
                return
            
            # Register agent
            self.connected_agents[agent_id] = websocket
            logger.info(f"Agent connected: {agent_id}")
            
            # Send simple acknowledgment
            await websocket.send(json.dumps({
                "type": "registration_ack",
                "status": "connected"
            }))
            
            # Handle messages from this agent
            async for message in websocket:
                await self._handle_agent_message(agent_id, json.loads(message))
                
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Agent disconnected: {agent_id}")
        except Exception as e:
            logger.error(f"Error handling agent {agent_id}: {e}")
        finally:
            if agent_id and agent_id in self.connected_agents:
                del self.connected_agents[agent_id]
    
    async def _handle_agent_message(self, agent_id: str, message: Dict[str, Any]):
        """Handle messages from agents"""
        message_type = message.get("type")
        
        if message_type == "heartbeat":
            # Just acknowledge heartbeats
            pass
        elif message_type == "recommendation":
            await self._route_recommendation(agent_id, message)
        elif message_type == "deployment_request":
            await self._handle_deployment_request(agent_id, message)
        elif message_type == "status_update":
            logger.info(f"{agent_id}: {message.get('status', 'unknown')}")
        else:
            logger.debug(f"Unhandled message from {agent_id}: {message_type}")
    
    async def _route_recommendation(self, source_agent: str, message: Dict[str, Any]):
        """Route recommendations to the appropriate agent"""
        recommendation = message.get("recommendation", {})
        rec_type = recommendation.get("type", "")
        
        # Route visual/UX recommendations to implementation agent
        if "autonomous_implementation" in self.connected_agents:
            forward_message = {
                "type": "implement_recommendation",
                "recommendation": {
                    "source_agent": source_agent,
                    "type": rec_type,
                    "data": recommendation.get("data", {}),
                    "priority": recommendation.get("priority", "medium"),
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            await self._send_to_agent("autonomous_implementation", forward_message)
            logger.info(f"Forwarded {rec_type} recommendation from {source_agent} to implementation agent")
        else:
            logger.warning("No implementation agent connected to handle recommendation")
    
    async def _handle_deployment_request(self, agent_id: str, message: Dict[str, Any]):
        """Handle deployment requests (simple approval for now)"""
        request_id = message.get("request_id")
        
        # Simple validation - just check if code exists
        code_changes = message.get("code_changes", {})
        if code_changes.get("code"):
            # Approve the deployment
            await self._send_to_agent(agent_id, {
                "type": "deployment_approved",
                "request_id": request_id
            })
            logger.info(f"Approved deployment: {request_id}")
        else:
            # Reject empty deployments
            await self._send_to_agent(agent_id, {
                "type": "deployment_rejected", 
                "request_id": request_id,
                "reason": "No code provided"
            })
            logger.warning(f"Rejected deployment: {request_id} - no code")
    
    async def _send_to_agent(self, agent_id: str, message: Dict[str, Any]):
        """Send message to specific agent"""
        if agent_id in self.connected_agents:
            try:
                await self.connected_agents[agent_id].send(json.dumps(message))
            except Exception as e:
                logger.error(f"Failed to send message to {agent_id}: {e}")
        else:
            logger.warning(f"Agent {agent_id} not connected")
    
    async def _coordinate(self):
        """Simple coordination loop"""
        while True:
            try:
                # Just log system status periodically
                active_agents = len(self.connected_agents)
                if active_agents > 0:
                    agent_list = ", ".join(self.connected_agents.keys())
                    logger.info(f"Active agents ({active_agents}): {agent_list}")
                else:
                    logger.info("No agents connected")
                
                await asyncio.sleep(60)  # Status update every minute
                
            except Exception as e:
                logger.error(f"Error in coordination loop: {e}")
                await asyncio.sleep(30)

def main():
    """Main entry point"""
    orchestrator = SimpleOrchestrator()
    
    try:
        asyncio.run(orchestrator.start())
    except KeyboardInterrupt:
        logger.info("Simple Orchestrator shutting down...")
    except Exception as e:
        logger.error(f"Orchestrator error: {e}")

if __name__ == "__main__":
    main() 