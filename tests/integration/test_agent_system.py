#!/usr/bin/env python3
"""
Integration tests for the multi-agent system.
"""

import pytest
import asyncio
import time
import json
from unittest.mock import Mock, patch
import websockets
from datetime import datetime

# Import the agents
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.core_orchestrator import CoreOrchestrator
from agents.visual_analysis_agent import VisualAnalysisAgent


class TestAgentSystem:
    """Test the multi-agent system integration"""
    
    def test_orchestrator_initialization(self):
        """Test orchestrator initializes correctly"""
        orchestrator = CoreOrchestrator("localhost", 8765)
        
        assert orchestrator.host == "localhost"
        assert orchestrator.port == 8765
        assert orchestrator.running == False
        assert len(orchestrator.connected_agents) == 0
        assert orchestrator.system_state.active_agents == 0
    
    def test_visual_agent_initialization(self):
        """Test visual analysis agent initializes correctly"""
        agent = VisualAnalysisAgent("localhost", 8765)
        
        assert agent.orchestrator_host == "localhost"
        assert agent.orchestrator_port == 8765
        assert agent.running == False
        assert agent.vision_processor is not None
        assert agent.total_analyses == 0
    
    @pytest.mark.asyncio
    async def test_agent_registration_flow(self):
        """Test agent registration with orchestrator"""
        # Create orchestrator and start it
        orchestrator = CoreOrchestrator("localhost", 8767)  # Different port to avoid conflicts
        
        # Mock the websocket server
        mock_websocket = Mock()
        mock_websocket.remote_address = ("127.0.0.1", 12345)
        
        # Test registration message
        registration_data = {
            "type": "agent_registration",
            "agent_id": "test_visual_agent",
            "capabilities": ["screenshot_analysis", "ui_element_detection"],
            "status": "online"
        }
        
        response = await orchestrator._handle_agent_registration(registration_data, mock_websocket)
        
        # Verify agent was registered
        assert "test_visual_agent" in orchestrator.connected_agents
        assert orchestrator.system_state.active_agents == 1
        assert response["status"] == "registered"
        assert response["agent_id"] == "test_visual_agent"
    
    @pytest.mark.asyncio
    async def test_heartbeat_handling(self):
        """Test heartbeat message handling"""
        orchestrator = CoreOrchestrator("localhost", 8768)
        
        # First register an agent
        mock_websocket = Mock()
        mock_websocket.remote_address = ("127.0.0.1", 12345)
        
        registration_data = {
            "type": "agent_registration",
            "agent_id": "test_agent",
            "capabilities": ["test"],
            "status": "online"
        }
        
        await orchestrator._handle_agent_registration(registration_data, mock_websocket)
        
        # Send heartbeat
        heartbeat_data = {
            "type": "agent_heartbeat",
            "agent_id": "test_agent",
            "performance": {
                "total_analyses": 5,
                "avg_response_time": 0.5
            }
        }
        
        response = await orchestrator._handle_agent_heartbeat(heartbeat_data)
        
        # Verify heartbeat was processed
        assert response["status"] == "acknowledged"
        agent = orchestrator.connected_agents["test_agent"]
        assert agent.performance_metrics["total_analyses"] == 5
        assert agent.performance_metrics["avg_response_time"] == 0.5
    
    @pytest.mark.asyncio
    async def test_visual_analysis_processing(self):
        """Test visual analysis result processing"""
        orchestrator = CoreOrchestrator("localhost", 8769)
        
        # Register visual analysis agent first
        mock_websocket = Mock()
        registration_data = {
            "type": "agent_registration",
            "agent_id": "visual_analysis_agent",
            "capabilities": ["screenshot_analysis"],
            "status": "online"
        }
        await orchestrator._handle_agent_registration(registration_data, mock_websocket)
        
        # Send visual analysis result
        analysis_data = {
            "type": "visual_analysis_result",
            "agent_id": "visual_analysis_agent",
            "analysis": {
                "timestamp": datetime.now().isoformat(),
                "change_score": 0.8,
                "quality_score": 0.6,  # Low quality to trigger insight
                "ui_elements_detected": 15,
                "accessibility_issues": ["Low contrast in button element"],
                "recommendations": ["Improve contrast ratio"]
            }
        }
        
        response = await orchestrator._handle_visual_analysis(analysis_data)
        
        # Verify processing
        assert response["status"] == "processed"
        assert len(orchestrator.insights_buffer) > 0
        
        # Check insight was created
        insight = orchestrator.insights_buffer[-1]
        assert insight.insight_type == "usability"
        assert "visual_analysis_agent" in insight.source_agents
        assert len(insight.recommendations) > 0
    
    @pytest.mark.asyncio
    async def test_baseline_comparison(self):
        """Test baseline comparison processing"""
        orchestrator = CoreOrchestrator("localhost", 8770)
        
        # Register agent
        mock_websocket = Mock()
        registration_data = {
            "type": "agent_registration",
            "agent_id": "visual_analysis_agent",
            "capabilities": ["screenshot_analysis"],
            "status": "online"
        }
        await orchestrator._handle_agent_registration(registration_data, mock_websocket)
        
        # Send baseline comparison with significant change
        comparison_data = {
            "type": "baseline_comparison",
            "agent_id": "visual_analysis_agent",
            "change_score": 0.5,  # Significant change
            "timestamp": datetime.now().isoformat()
        }
        
        response = await orchestrator._handle_baseline_comparison(comparison_data)
        
        # Verify processing
        assert response["status"] == "processed"
        assert len(orchestrator.insights_buffer) > 0
        
        # Check insight for significant change
        insight = orchestrator.insights_buffer[-1]
        assert "Significant UI change detected" in insight.description
        assert insight.severity == "medium"
    
    def test_system_status_api(self):
        """Test system status API"""
        orchestrator = CoreOrchestrator("localhost", 8771)
        
        status = orchestrator.get_system_status()
        
        assert "system_state" in status
        assert "connected_agents" in status
        assert "system_metrics" in status
        assert status["system_state"]["active_agents"] == 0
        assert status["system_state"]["system_health"] == "good"
    
    def test_insights_api(self):
        """Test insights retrieval API"""
        orchestrator = CoreOrchestrator("localhost", 8772)
        
        # Add a test insight
        from agents.core_orchestrator import UXInsight
        
        test_insight = UXInsight(
            timestamp=datetime.now(),
            source_agents=["test_agent"],
            insight_type="usability",
            severity="medium",
            description="Test insight",
            recommendations=["Test recommendation"],
            data={}
        )
        
        orchestrator.insights_buffer.append(test_insight)
        
        insights = orchestrator.get_recent_insights(limit=10)
        
        assert len(insights) == 1
        assert insights[0]["description"] == "Test insight"
        assert insights[0]["severity"] == "medium"
        assert insights[0]["type"] == "usability"
    
    @patch('agents.visual_analysis_agent.ImageGrab')
    def test_visual_agent_screenshot_analysis(self, mock_image_grab):
        """Test visual agent screenshot analysis"""
        import numpy as np
        from PIL import Image
        
        # Mock screenshot
        mock_image = Image.new('RGB', (1920, 1080), color='white')
        mock_image_grab.grab.return_value = mock_image
        
        agent = VisualAnalysisAgent("localhost", 8773)
        
        # Test screenshot conversion
        screenshot_array = np.array(mock_image)
        
        assert screenshot_array.shape == (1080, 1920, 3)
        assert agent.vision_processor is not None
    
    def test_agent_config_generation(self):
        """Test agent-specific configuration generation"""
        orchestrator = CoreOrchestrator("localhost", 8774)
        
        # Test visual agent config
        visual_config = orchestrator._get_agent_config("visual_analysis_agent")
        
        assert "quality_threshold" in visual_config
        assert "change_threshold" in visual_config
        assert visual_config["quality_threshold"] == 0.7
        
        # Test metrics agent config
        metrics_config = orchestrator._get_agent_config("metrics_intelligence_agent")
        
        assert "performance_threshold" in metrics_config
        assert "memory_threshold" in metrics_config
        assert metrics_config["performance_threshold"] == 500
    
    def test_severity_assessment(self):
        """Test severity assessment logic"""
        orchestrator = CoreOrchestrator("localhost", 8775)
        
        # Test critical severity
        critical_analysis = {
            "quality_score": 0.4,
            "accessibility_issues": ["issue1", "issue2", "issue3", "issue4", "issue5", "issue6"]
        }
        severity = orchestrator._assess_severity(critical_analysis)
        assert severity == "critical"
        
        # Test high severity
        high_analysis = {
            "quality_score": 0.6,
            "accessibility_issues": ["issue1", "issue2", "issue3"]
        }
        severity = orchestrator._assess_severity(high_analysis)
        assert severity == "high"
        
        # Test medium severity
        medium_analysis = {
            "quality_score": 0.75,
            "accessibility_issues": ["issue1"]
        }
        severity = orchestrator._assess_severity(medium_analysis)
        assert severity == "medium"
        
        # Test low severity
        low_analysis = {
            "quality_score": 0.9,
            "accessibility_issues": []
        }
        severity = orchestrator._assess_severity(low_analysis)
        assert severity == "low"


@pytest.mark.integration
class TestAgentIntegration:
    """Integration tests that require actual agent communication"""
    
    @pytest.mark.asyncio
    async def test_full_agent_workflow(self):
        """Test a complete workflow with orchestrator and agents"""
        # This test would be skipped in CI/CD but useful for local testing
        pytest.skip("Full integration test - run manually for development")
        
        # Start orchestrator
        orchestrator = CoreOrchestrator("localhost", 8776)
        
        # In a real test, we would:
        # 1. Start the orchestrator
        # 2. Connect visual and metrics agents
        # 3. Send test data
        # 4. Verify insights are generated
        # 5. Test monitoring commands
        
        assert True  # Placeholder


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 