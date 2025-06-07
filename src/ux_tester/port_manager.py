"""
Port Management System for UX-MIRROR
Handles dynamic port allocation and conflict detection.

Task: PORT-002A - Create port_manager.py with find_available_port functionality
"""

import socket
import logging
import threading
import time
from typing import Optional, List, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

@dataclass
class PortAllocation:
    """Information about a port allocation"""
    port: int
    allocated_at: datetime
    allocated_to: str  # Process/agent identifier
    in_use: bool = True

class PortManager:
    """
    Manages port allocation for UX-MIRROR system components.
    Prevents port conflicts and provides dynamic allocation.
    """
    
    def __init__(self, start_port: int = 8765, end_port: int = 8864):
        """
        Initialize PortManager
        
        Args:
            start_port: Starting port number for allocation range
            end_port: Ending port number for allocation range
        """
        self.start_port = start_port
        self.end_port = end_port
        self.allocated_ports: Set[int] = set()
        self.port_allocations: List[PortAllocation] = []
        self._lock = threading.Lock()
        
        logger.info(f"PortManager initialized with range {start_port}-{end_port}")
    
    def find_available_port(self, start: Optional[int] = None, end: Optional[int] = None) -> Optional[int]:
        """
        Find an available port in the specified range.
        
        Args:
            start: Starting port (defaults to self.start_port)
            end: Ending port (defaults to self.end_port)
            
        Returns:
            Available port number or None if no ports available
        """
        if start is None:
            start = self.start_port
        if end is None:
            end = self.end_port
            
        with self._lock:
            for port in range(start, end + 1):
                if self._is_port_available(port):
                    return port
        
        logger.warning(f"No available ports in range {start}-{end}")
        return None
    
    def _is_port_available(self, port: int) -> bool:
        """
        Check if a port is available for allocation.
        
        Args:
            port: Port number to check
            
        Returns:
            True if port is available, False otherwise
        """
        # Check if already allocated by us
        if port in self.allocated_ports:
            return False
        
        # Test if port is actually bindable
        return self._test_port_bind(port)
    
    def _test_port_bind(self, port: int) -> bool:
        """
        Test if a port can be bound (i.e., is not in use by another process).
        
        Args:
            port: Port number to test
            
        Returns:
            True if port can be bound, False otherwise
        """
        try:
            # Test TCP binding
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.bind(('localhost', port))
                return True
        except OSError:
            return False
    
    def allocate_port(self, requester_id: str, preferred_port: Optional[int] = None) -> Optional[int]:
        """
        Allocate a port to a requester.
        
        Args:
            requester_id: Identifier for the requester (e.g., "visual_analysis_agent")
            preferred_port: Preferred port number (will try this first)
            
        Returns:
            Allocated port number or None if allocation failed
        """
        with self._lock:
            # Try preferred port first if specified
            if preferred_port and self._is_port_available(preferred_port):
                return self._complete_allocation(preferred_port, requester_id)
            
            # Find any available port
            available_port = self.find_available_port()
            if available_port:
                return self._complete_allocation(available_port, requester_id)
            
            logger.error(f"Failed to allocate port for {requester_id}")
            return None
    
    def _complete_allocation(self, port: int, requester_id: str) -> int:
        """
        Complete the port allocation process.
        
        Args:
            port: Port number to allocate
            requester_id: Identifier for the requester
            
        Returns:
            Allocated port number
        """
        self.allocated_ports.add(port)
        allocation = PortAllocation(
            port=port,
            allocated_at=datetime.now(),
            allocated_to=requester_id,
            in_use=True
        )
        self.port_allocations.append(allocation)
        
        logger.info(f"Port {port} allocated to {requester_id}")
        return port
    
    def release_port(self, port: int, requester_id: str) -> bool:
        """
        Release a previously allocated port.
        
        Args:
            port: Port number to release
            requester_id: Identifier of the requester who allocated the port
            
        Returns:
            True if port was successfully released, False otherwise
        """
        with self._lock:
            if port not in self.allocated_ports:
                logger.warning(f"Attempted to release unallocated port {port}")
                return False
            
            # Find the allocation record
            for allocation in self.port_allocations:
                if allocation.port == port and allocation.allocated_to == requester_id:
                    allocation.in_use = False
                    self.allocated_ports.remove(port)
                    logger.info(f"Port {port} released by {requester_id}")
                    return True
            
            logger.warning(f"Port {port} not allocated to {requester_id}")
            return False
    
    def get_port_pool(self, requester_id: str, pool_size: int = 10) -> List[int]:
        """
        Allocate a pool of ports for a requester.
        
        Args:
            requester_id: Identifier for the requester
            pool_size: Number of ports to allocate
            
        Returns:
            List of allocated port numbers
        """
        allocated_ports = []
        
        for i in range(pool_size):
            port = self.allocate_port(f"{requester_id}_pool_{i}")
            if port:
                allocated_ports.append(port)
            else:
                logger.warning(f"Could only allocate {len(allocated_ports)} of {pool_size} requested ports")
                break
        
        logger.info(f"Allocated port pool of {len(allocated_ports)} ports to {requester_id}")
        return allocated_ports
    
    def cleanup_expired_allocations(self, max_age_hours: int = 24) -> int:
        """
        Clean up expired allocations that are no longer in use.
        
        Args:
            max_age_hours: Maximum age in hours before allocation is considered expired
            
        Returns:
            Number of allocations cleaned up
        """
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        cleaned_count = 0
        
        with self._lock:
            for allocation in self.port_allocations[:]:  # Copy list to iterate safely
                if allocation.allocated_at < cutoff_time and not allocation.in_use:
                    self.port_allocations.remove(allocation)
                    if allocation.port in self.allocated_ports:
                        self.allocated_ports.remove(allocation.port)
                    cleaned_count += 1
        
        if cleaned_count > 0:
            logger.info(f"Cleaned up {cleaned_count} expired port allocations")
        
        return cleaned_count
    
    def get_allocation_status(self) -> dict:
        """
        Get current allocation status and statistics.
        
        Returns:
            Dictionary with allocation status information
        """
        with self._lock:
            total_range = self.end_port - self.start_port + 1
            allocated_count = len(self.allocated_ports)
            available_count = total_range - allocated_count
            
            return {
                "port_range": f"{self.start_port}-{self.end_port}",
                "total_ports": total_range,
                "allocated_ports": allocated_count,
                "available_ports": available_count,
                "utilization_percent": (allocated_count / total_range) * 100,
                "active_allocations": [
                    {
                        "port": alloc.port,
                        "allocated_to": alloc.allocated_to,
                        "allocated_at": alloc.allocated_at.isoformat(),
                        "in_use": alloc.in_use
                    }
                    for alloc in self.port_allocations if alloc.in_use
                ]
            }
    
    def is_port_allocated(self, port: int) -> bool:
        """
        Check if a port is currently allocated.
        
        Args:
            port: Port number to check
            
        Returns:
            True if port is allocated, False otherwise
        """
        return port in self.allocated_ports

# Global instance for easy access
_port_manager_instance: Optional[PortManager] = None

def get_port_manager() -> PortManager:
    """
    Get the global PortManager instance.
    
    Returns:
        Global PortManager instance
    """
    global _port_manager_instance
    if _port_manager_instance is None:
        _port_manager_instance = PortManager()
    return _port_manager_instance

def find_available_port(start: int = 8765, end: int = 8864) -> Optional[int]:
    """
    Convenience function to find an available port.
    
    Args:
        start: Starting port number
        end: Ending port number
        
    Returns:
        Available port number or None
    """
    return get_port_manager().find_available_port(start, end) 