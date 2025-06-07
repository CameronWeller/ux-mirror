"""
Unit tests for PortManager
Tests for PORT-002: Port Management System
"""

import pytest
import socket
import threading
import time
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from ux_tester.port_manager import PortManager, PortAllocation, get_port_manager, find_available_port


class TestPortManager:
    """Test cases for PortManager class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.port_manager = PortManager(start_port=9000, end_port=9010)
    
    def test_init(self):
        """Test PortManager initialization"""
        assert self.port_manager.start_port == 9000
        assert self.port_manager.end_port == 9010
        assert len(self.port_manager.allocated_ports) == 0
        assert len(self.port_manager.port_allocations) == 0
    
    def test_find_available_port_success(self):
        """Test finding an available port successfully"""
        port = self.port_manager.find_available_port()
        assert port is not None
        assert 9000 <= port <= 9010
    
    def test_find_available_port_custom_range(self):
        """Test finding port in custom range"""
        port = self.port_manager.find_available_port(start=9005, end=9007)
        if port is not None:  # May be None if all ports in range are busy
            assert 9005 <= port <= 9007
    
    @patch('ux_tester.port_manager.socket.socket')
    def test_find_available_port_no_ports_available(self, mock_socket):
        """Test when no ports are available"""
        # Mock socket to always fail binding
        mock_sock = MagicMock()
        mock_sock.__enter__.return_value = mock_sock
        mock_sock.bind.side_effect = OSError("Port in use")
        mock_socket.return_value = mock_sock
        
        port = self.port_manager.find_available_port()
        assert port is None
    
    def test_allocate_port_success(self):
        """Test successful port allocation"""
        port = self.port_manager.allocate_port("test_agent")
        
        assert port is not None
        assert port in self.port_manager.allocated_ports
        assert len(self.port_manager.port_allocations) == 1
        
        allocation = self.port_manager.port_allocations[0]
        assert allocation.port == port
        assert allocation.allocated_to == "test_agent"
        assert allocation.in_use is True
    
    def test_allocate_port_preferred(self):
        """Test port allocation with preferred port"""
        preferred_port = 9005
        
        # First check if the port is actually available
        if self.port_manager._is_port_available(preferred_port):
            port = self.port_manager.allocate_port("test_agent", preferred_port)
            assert port == preferred_port
        else:
            # If preferred port not available, should get a different one
            port = self.port_manager.allocate_port("test_agent", preferred_port)
            assert port != preferred_port or port is None
    
    def test_release_port_success(self):
        """Test successful port release"""
        # First allocate a port
        port = self.port_manager.allocate_port("test_agent")
        assert port is not None
        
        # Then release it
        result = self.port_manager.release_port(port, "test_agent")
        assert result is True
        assert port not in self.port_manager.allocated_ports
        
        # Find the allocation record and verify it's marked as not in use
        allocation = next((a for a in self.port_manager.port_allocations if a.port == port), None)
        assert allocation is not None
        assert allocation.in_use is False
    
    def test_release_port_not_allocated(self):
        """Test releasing a port that wasn't allocated"""
        result = self.port_manager.release_port(9999, "test_agent")
        assert result is False
    
    def test_release_port_wrong_requester(self):
        """Test releasing a port with wrong requester ID"""
        # Allocate port to one agent
        port = self.port_manager.allocate_port("agent1")
        assert port is not None
        
        # Try to release with different agent ID
        result = self.port_manager.release_port(port, "agent2")
        assert result is False
        assert port in self.port_manager.allocated_ports
    
    def test_get_port_pool(self):
        """Test allocating a pool of ports"""
        pool_size = 3
        ports = self.port_manager.get_port_pool("test_agent", pool_size)
        
        # Should get some ports (may be less than requested if not enough available)
        assert len(ports) > 0
        assert len(ports) <= pool_size
        
        # All ports should be allocated
        for port in ports:
            assert port in self.port_manager.allocated_ports
    
    def test_cleanup_expired_allocations(self):
        """Test cleanup of expired allocations"""
        # Allocate and immediately release a port
        port = self.port_manager.allocate_port("test_agent")
        self.port_manager.release_port(port, "test_agent")
        
        # Manually set the allocation time to be old
        allocation = next((a for a in self.port_manager.port_allocations if a.port == port), None)
        assert allocation is not None
        allocation.allocated_at = datetime.now() - timedelta(hours=25)
        
        # Run cleanup
        cleaned = self.port_manager.cleanup_expired_allocations(max_age_hours=24)
        assert cleaned == 1
        
        # Allocation should be removed
        remaining_allocations = [a for a in self.port_manager.port_allocations if a.port == port]
        assert len(remaining_allocations) == 0
    
    def test_get_allocation_status(self):
        """Test getting allocation status"""
        # Allocate some ports
        port1 = self.port_manager.allocate_port("agent1")
        port2 = self.port_manager.allocate_port("agent2")
        
        status = self.port_manager.get_allocation_status()
        
        assert "port_range" in status
        assert "total_ports" in status
        assert "allocated_ports" in status
        assert "available_ports" in status
        assert "utilization_percent" in status
        assert "active_allocations" in status
        
        assert status["allocated_ports"] >= 2  # At least the two we allocated
        assert len(status["active_allocations"]) >= 2
    
    def test_is_port_allocated(self):
        """Test checking if port is allocated"""
        port = self.port_manager.allocate_port("test_agent")
        
        assert self.port_manager.is_port_allocated(port) is True
        assert self.port_manager.is_port_allocated(9999) is False
    
    def test_thread_safety(self):
        """Test thread safety of port allocation"""
        allocated_ports = []
        errors = []
        
        def allocate_ports():
            try:
                for i in range(3):
                    port = self.port_manager.allocate_port(f"thread_agent_{threading.current_thread().ident}_{i}")
                    if port:
                        allocated_ports.append(port)
                    time.sleep(0.01)  # Small delay to increase chance of race conditions
            except Exception as e:
                errors.append(e)
        
        # Start multiple threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=allocate_ports)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check results
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(allocated_ports) > 0
        assert len(set(allocated_ports)) == len(allocated_ports), "Duplicate ports allocated"


class TestGlobalFunctions:
    """Test global convenience functions"""
    
    def test_get_port_manager_singleton(self):
        """Test that get_port_manager returns singleton"""
        pm1 = get_port_manager()
        pm2 = get_port_manager()
        assert pm1 is pm2
    
    def test_find_available_port_function(self):
        """Test convenience function"""
        port = find_available_port(start=9020, end=9030)
        if port is not None:  # May be None if no ports available
            assert 9020 <= port <= 9030


class TestPortAllocation:
    """Test PortAllocation dataclass"""
    
    def test_port_allocation_creation(self):
        """Test creating PortAllocation"""
        now = datetime.now()
        allocation = PortAllocation(
            port=8080,
            allocated_at=now,
            allocated_to="test_agent"
        )
        
        assert allocation.port == 8080
        assert allocation.allocated_at == now
        assert allocation.allocated_to == "test_agent"
        assert allocation.in_use is True  # Default value 