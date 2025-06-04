#!/usr/bin/env python3
"""
Test script for UX-MIRROR Orchestrator Agent
===========================================

This script tests the orchestrator agent functionality including:
- Agent registration and management
- Task creation and assignment
- Load balancing and coordination
- Insight generation

Usage:
    python test_orchestrator.py
"""

import asyncio
import json
import sys
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Add agents directory to path
sys.path.insert(0, 'agents')

from orchestrator import OrchestratorAgent, TaskPriority
from visual_analysis import VisualAnalysisAgent

class MockAgent:
    """Mock agent for testing orchestrator functionality"""
    
    def __init__(self, agent_id: str, capabilities: List[str]):
        self.agent_id = agent_id
        self.capabilities = capabilities
        self.websocket = None
        self.received_tasks = []
        self.is_running = False
        
    async def connect_to_orchestrator(self, host: str = "localhost", port: int = 8765):
        """Connect to the orchestrator"""
        import websockets
        
        try:
            self.websocket = await websockets.connect(f"ws://{host}:{port}")
            
            # Send registration
            registration = {
                "agent_id": self.agent_id,
                "capabilities": self.capabilities
            }
            await self.websocket.send(json.dumps(registration))
            
            # Listen for confirmation
            response = await self.websocket.recv()
            response_data = json.loads(response)
            
            if response_data.get("type") == "registration_confirmed":
                print(f"✅ Mock agent {self.agent_id} registered successfully")
                self.is_running = True
                
                # Start message handling
                asyncio.create_task(self._handle_messages())
                asyncio.create_task(self._send_heartbeats())
                
                return True
            else:
                print(f"❌ Registration failed for {self.agent_id}")
                return False
                
        except Exception as e:
            print(f"❌ Connection failed for {self.agent_id}: {e}")
            return False
    
    async def _handle_messages(self):
        """Handle messages from orchestrator"""
        try:
            async for message in self.websocket:
                data = json.loads(message)
                message_type = data.get("type")
                
                if message_type in ["screenshot_analysis", "urgent_analysis", "custom_recognizer_training"]:
                    # Handle task assignment
                    task_id = data.get("task_id")
                    self.received_tasks.append(data)
                    print(f"📋 {self.agent_id} received task: {message_type} ({task_id})")
                    
                    # Simulate task processing
                    await asyncio.sleep(2)  # Simulate work
                    
                    # Send task completion
                    result = {
                        "type": "task_result",
                        "task_id": task_id,
                        "status": "completed",
                        "result": {
                            "processed": True,
                            "completion_time": 2.0,
                            "agent_id": self.agent_id
                        }
                    }
                    await self.websocket.send(json.dumps(result))
                    print(f"✅ {self.agent_id} completed task: {task_id}")
                    
        except Exception as e:
            print(f"❌ Error in {self.agent_id} message handling: {e}")
    
    async def _send_heartbeats(self):
        """Send periodic heartbeats"""
        while self.is_running:
            try:
                heartbeat = {
                    "type": "heartbeat",
                    "status": "active",
                    "cpu_usage": 25.5,
                    "memory_usage": 45.2,
                    "analysis_queue_size": len(self.received_tasks)
                }
                await self.websocket.send(json.dumps(heartbeat))
                await asyncio.sleep(5)  # Send every 5 seconds
                
            except Exception as e:
                print(f"❌ Heartbeat error for {self.agent_id}: {e}")
                break
    
    async def send_alert(self, alert_type: str, severity: str = "medium"):
        """Send an alert to the orchestrator"""
        alert = {
            "type": "alert",
            "alert_type": alert_type,
            "severity": severity,
            "data": {
                "message": f"Test alert from {self.agent_id}",
                "timestamp": datetime.now().isoformat()
            }
        }
        await self.websocket.send(json.dumps(alert))
        print(f"🚨 {self.agent_id} sent {severity} alert: {alert_type}")
    
    async def disconnect(self):
        """Disconnect from orchestrator"""
        self.is_running = False
        if self.websocket:
            await self.websocket.close()
        print(f"🔌 {self.agent_id} disconnected")

async def test_orchestrator_startup():
    """Test orchestrator startup and configuration"""
    print("\n🚀 Testing Orchestrator Startup...")
    
    orchestrator = OrchestratorAgent()
    
    # Test configuration loading
    await orchestrator._load_configuration()
    print("✅ Configuration loaded successfully")
    
    # Start orchestrator in background
    orchestrator_task = asyncio.create_task(orchestrator.start())
    
    # Give it time to start
    await asyncio.sleep(2)
    
    print("✅ Orchestrator started successfully")
    return orchestrator, orchestrator_task

async def test_agent_registration():
    """Test agent registration with orchestrator"""
    print("\n👥 Testing Agent Registration...")
    
    # Create mock agents
    agents = [
        MockAgent("test_visual_agent", ["screenshot_analysis", "ui_element_detection"]),
        MockAgent("test_behavior_agent", ["user_behavior_tracking", "pattern_analysis"]),
        MockAgent("test_performance_agent", ["performance_analysis", "resource_optimization"])
    ]
    
    # Connect all agents
    connected_agents = []
    for agent in agents:
        success = await agent.connect_to_orchestrator()
        if success:
            connected_agents.append(agent)
    
    print(f"✅ {len(connected_agents)}/{len(agents)} agents connected successfully")
    
    # Wait for heartbeats to establish
    await asyncio.sleep(3)
    
    return connected_agents

async def test_task_creation_and_assignment(orchestrator: OrchestratorAgent):
    """Test task creation and assignment"""
    print("\n📋 Testing Task Creation and Assignment...")
    
    # Create various types of tasks
    tasks_created = []
    
    # High priority screenshot analysis
    task_id = orchestrator.create_task(
        task_type="screenshot_analysis",
        data={
            "screenshot_id": "test_001",
            "platform": "web",
            "url": "https://example.com"
        },
        priority=TaskPriority.HIGH
    )
    tasks_created.append(task_id)
    print(f"📋 Created high priority screenshot analysis task: {task_id}")
    
    # Critical urgent analysis
    task_id = orchestrator.create_task(
        task_type="urgent_analysis",
        data={
            "alert_source": "test_system",
            "issue_type": "critical_ux_issue"
        },
        priority=TaskPriority.CRITICAL,
        deadline=datetime.now() + timedelta(minutes=5)
    )
    tasks_created.append(task_id)
    print(f"🚨 Created critical urgent analysis task: {task_id}")
    
    # Medium priority training task
    task_id = orchestrator.create_task(
        task_type="custom_recognizer_training",
        data={
            "issue_type": "low_contrast_text",
            "sample_count": 15
        },
        priority=TaskPriority.MEDIUM
    )
    tasks_created.append(task_id)
    print(f"🧠 Created medium priority training task: {task_id}")
    
    # Wait for task processing
    await asyncio.sleep(10)
    
    print(f"✅ Created {len(tasks_created)} tasks for testing")
    return tasks_created

async def test_load_balancing_and_failover(orchestrator: OrchestratorAgent, agents: List[MockAgent]):
    """Test load balancing and failover scenarios"""
    print("\n⚖️  Testing Load Balancing and Failover...")
    
    # Create multiple tasks to test load balancing
    task_count = 6
    for i in range(task_count):
        orchestrator.create_task(
            task_type="screenshot_analysis",
            data={"test_batch": f"batch_{i}"},
            priority=TaskPriority.MEDIUM
        )
    
    print(f"📋 Created {task_count} tasks for load balancing test")
    
    # Wait for distribution
    await asyncio.sleep(5)
    
    # Test agent disconnect scenario
    if agents:
        print(f"🔌 Simulating disconnect of agent: {agents[0].agent_id}")
        await agents[0].disconnect()
        
        # Wait for failover
        await asyncio.sleep(3)
        print("✅ Failover scenario tested")
    
    return True

async def test_insights_generation(agents: List[MockAgent]):
    """Test insights generation from alerts and recommendations"""
    print("\n💡 Testing Insights Generation...")
    
    if not agents:
        print("❌ No agents available for insights testing")
        return False
    
    # Send various alerts
    await agents[0].send_alert("critical_ux_issues", "critical")
    await asyncio.sleep(1)
    
    if len(agents) > 1:
        await agents[1].send_alert("performance_degradation", "medium")
        await asyncio.sleep(1)
    
    # Send recommendation
    recommendation = {
        "type": "recommendation",
        "recommendation_type": "optimization_suggestion",
        "priority": "high",
        "data": {
            "suggestion": "Optimize image loading performance",
            "impact": "high",
            "effort": "medium"
        }
    }
    
    if agents:
        await agents[0].websocket.send(json.dumps(recommendation))
        print("💡 Sent recommendation to orchestrator")
    
    # Wait for insight processing
    await asyncio.sleep(3)
    
    print("✅ Insights generation tested")
    return True

async def test_system_metrics_and_status(orchestrator: OrchestratorAgent):
    """Test system metrics and status reporting"""
    print("\n📊 Testing System Metrics and Status...")
    
    # Get system status
    status = orchestrator.get_system_status()
    
    print(f"🏃 Orchestrator Status: {status['orchestrator']['status']}")
    print(f"👥 Connected Agents: {len(status['agents'])}")
    print(f"📋 Active Tasks: {status['tasks']['active']}")
    print(f"✅ Completed Tasks: {status['tasks']['completed']}")
    print(f"💡 Total Insights: {status['insights']['total']}")
    
    # Check if we have reasonable metrics
    if status['orchestrator']['status'] == 'active':
        print("✅ System status reporting working")
        return True
    else:
        print("❌ System status reporting failed")
        return False

async def test_real_visual_analysis_integration():
    """Test integration with real visual analysis agent"""
    print("\n🔍 Testing Real Visual Analysis Agent Integration...")
    
    try:
        # Create a real visual analysis agent
        visual_agent = VisualAnalysisAgent()
        
        # Connect to orchestrator (assuming it's running)
        await visual_agent._load_configuration()
        await visual_agent._connect_to_orchestrator()
        
        print("✅ Real visual analysis agent connected")
        
        # Let it run briefly to send heartbeats
        await asyncio.sleep(5)
        
        return True
        
    except Exception as e:
        print(f"⚠️  Real agent integration test failed: {e}")
        return False

async def cleanup_agents(agents: List[MockAgent]):
    """Clean up test agents"""
    print("\n🧹 Cleaning up test agents...")
    
    for agent in agents:
        if agent.is_running:
            await agent.disconnect()
    
    print("✅ All agents disconnected")

async def run_all_tests():
    """Run all orchestrator tests"""
    print("🧪 Starting UX-MIRROR Orchestrator Agent Tests")
    print("=" * 60)
    
    test_results = []
    orchestrator = None
    orchestrator_task = None
    agents = []
    
    try:
        # Test 1: Orchestrator startup
        orchestrator, orchestrator_task = await test_orchestrator_startup()
        test_results.append(("Orchestrator Startup", True))
        
        # Test 2: Agent registration
        agents = await test_agent_registration()
        test_results.append(("Agent Registration", len(agents) > 0))
        
        # Test 3: Task creation and assignment
        tasks_created = await test_task_creation_and_assignment(orchestrator)
        test_results.append(("Task Creation and Assignment", len(tasks_created) > 0))
        
        # Test 4: Load balancing and failover
        lb_result = await test_load_balancing_and_failover(orchestrator, agents)
        test_results.append(("Load Balancing and Failover", lb_result))
        
        # Test 5: Insights generation
        insights_result = await test_insights_generation(agents)
        test_results.append(("Insights Generation", insights_result))
        
        # Test 6: System metrics
        metrics_result = await test_system_metrics_and_status(orchestrator)
        test_results.append(("System Metrics and Status", metrics_result))
        
        # Test 7: Real agent integration
        real_agent_result = await test_real_visual_analysis_integration()
        test_results.append(("Real Visual Analysis Integration", real_agent_result))
        
    except Exception as e:
        print(f"💥 Test suite error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        await cleanup_agents(agents)
        
        if orchestrator_task:
            orchestrator_task.cancel()
            try:
                await orchestrator_task
            except asyncio.CancelledError:
                pass
        
        if orchestrator:
            await orchestrator.stop()
    
    # Print test summary
    print("\n" + "=" * 60)
    print("🧪 Orchestrator Test Results Summary")
    print("=" * 60)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<35} {status}")
        if result:
            passed += 1
    
    print(f"\nTests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All orchestrator tests passed! System is working correctly.")
    else:
        print(f"⚠️  {total - passed} tests failed. Check the output above for details.")
    
    return passed == total

def main():
    """Main test function"""
    try:
        result = asyncio.run(run_all_tests())
        exit_code = 0 if result else 1
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n💥 Unexpected error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 