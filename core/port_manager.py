#!/usr/bin/env python3
"""
Port Management for UX-MIRROR

Handles port allocation and conflict resolution for the unified system.
"""

import socket
import logging
from typing import Optional, List, Dict
from dataclasses import dataclass
from pathlib import Path
import json
import time

logger = logging.getLogger(__name__)

@dataclass
class PortAllocation:
    """Port allocation information"""
    port: int
    service: str
    allocated_at: float
    process_id: Optional[int] = None
    is_active: bool = True

class PortManager:
    """Manages port allocation for UX-MIRROR services"""
    
    def __init__(self, base_port: int = 8765, port_range: int = 100):
        self.base_port = base_port
        self.port_range = port_range
        self.allocations: Dict[str, PortAllocation] = {}
        self.allocation_file = Path("config/port_allocations.json")
        self.allocation_file.parent.mkdir(exist_ok=True)
        
        # Load existing allocations
        self._load_allocations()
        
    def allocate_port(self, service_name: str, preferred_port: Optional[int] = None) -> int:
        """
        Allocate a port for a service
        
        Args:
            service_name: Name of the service requesting the port
            preferred_port: Preferred port if available
            
        Returns:
            Allocated port number
            
        Raises:
            RuntimeError: If no ports are available
        """
        # Check if service already has a port
        if service_name in self.allocations:
            existing = self.allocations[service_name]
            if self._is_port_available(existing.port):
                logger.info(f"Reusing existing port {existing.port} for {service_name}")
                existing.is_active = True
                existing.allocated_at = time.time()
                self._save_allocations()
                return existing.port
            else:
                logger.warning(f"Previously allocated port {existing.port} for {service_name} is no longer available")
                del self.allocations[service_name]
        
        # Try preferred port first
        if preferred_port and self._is_port_available(preferred_port):
            port = preferred_port
        else:
            # Find available port in range
            port = self._find_available_port()
        
        if port is None:
            raise RuntimeError(f"No available ports in range {self.base_port}-{self.base_port + self.port_range}")
        
        # Allocate the port
        allocation = PortAllocation(
            port=port,
            service=service_name,
            allocated_at=time.time(),
            is_active=True
        )
        
        self.allocations[service_name] = allocation
        self._save_allocations()
        
        logger.info(f"Allocated port {port} for service {service_name}")
        return port
    
    def release_port(self, service_name: str) -> bool:
        """
        Release a port allocated to a service
        
        Args:
            service_name: Name of the service
            
        Returns:
            True if port was released, False if not found
        """
        if service_name in self.allocations:
            allocation = self.allocations[service_name]
            allocation.is_active = False
            logger.info(f"Released port {allocation.port} from service {service_name}")
            self._save_allocations()
            return True
        
        return False
    
    def get_port(self, service_name: str) -> Optional[int]:
        """
        Get the allocated port for a service
        
        Args:
            service_name: Name of the service
            
        Returns:
            Port number if allocated, None otherwise
        """
        if service_name in self.allocations:
            allocation = self.allocations[service_name]
            if allocation.is_active:
                return allocation.port
        
        return None
    
    def cleanup_stale_allocations(self, max_age_hours: int = 24) -> int:
        """
        Clean up stale allocations
        
        Args:
            max_age_hours: Maximum age of allocations to keep
            
        Returns:
            Number of allocations cleaned up
        """
        current_time = time.time()
        cutoff_time = current_time - (max_age_hours * 3600)
        
        stale_services = []
        for service_name, allocation in self.allocations.items():
            if allocation.allocated_at < cutoff_time or not self._is_port_available(allocation.port):
                stale_services.append(service_name)
        
        for service_name in stale_services:
            del self.allocations[service_name]
            logger.info(f"Cleaned up stale allocation for {service_name}")
        
        if stale_services:
            self._save_allocations()
        
        return len(stale_services)
    
    def get_status(self) -> Dict[str, any]:
        """Get status of all port allocations"""
        status = {
            'base_port': self.base_port,
            'port_range': self.port_range,
            'active_allocations': len([a for a in self.allocations.values() if a.is_active]),
            'total_allocations': len(self.allocations),
            'allocations': {}
        }
        
        for service_name, allocation in self.allocations.items():
            status['allocations'][service_name] = {
                'port': allocation.port,
                'allocated_at': allocation.allocated_at,
                'is_active': allocation.is_active,
                'port_available': self._is_port_available(allocation.port)
            }
        
        return status
    
    def _find_available_port(self) -> Optional[int]:
        """Find an available port in the configured range"""
        for port in range(self.base_port, self.base_port + self.port_range):
            if self._is_port_available(port):
                return port
        return None
    
    def _is_port_available(self, port: int) -> bool:
        """Check if a port is available"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                result = sock.bind(('localhost', port))
                return True
        except OSError:
            return False
    
    def _load_allocations(self):
        """Load port allocations from file"""
        try:
            if self.allocation_file.exists():
                with open(self.allocation_file, 'r') as f:
                    data = json.load(f)
                    
                for service_name, alloc_data in data.items():
                    allocation = PortAllocation(
                        port=alloc_data['port'],
                        service=alloc_data['service'],
                        allocated_at=alloc_data['allocated_at'],
                        process_id=alloc_data.get('process_id'),
                        is_active=alloc_data.get('is_active', True)
                    )
                    self.allocations[service_name] = allocation
                    
                logger.info(f"Loaded {len(self.allocations)} port allocations")
        except Exception as e:
            logger.warning(f"Failed to load port allocations: {e}")
            self.allocations = {}
    
    def _save_allocations(self):
        """Save port allocations to file"""
        try:
            data = {}
            for service_name, allocation in self.allocations.items():
                data[service_name] = {
                    'port': allocation.port,
                    'service': allocation.service,
                    'allocated_at': allocation.allocated_at,
                    'process_id': allocation.process_id,
                    'is_active': allocation.is_active
                }
            
            with open(self.allocation_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save port allocations: {e}")

# Global port manager instance
_port_manager = None

def get_port_manager() -> PortManager:
    """Get the global port manager instance"""
    global _port_manager
    if _port_manager is None:
        _port_manager = PortManager()
    return _port_manager

def allocate_service_port(service_name: str, preferred_port: Optional[int] = None) -> int:
    """Convenience function to allocate a port for a service"""
    return get_port_manager().allocate_port(service_name, preferred_port)

def release_service_port(service_name: str) -> bool:
    """Convenience function to release a service port"""
    return get_port_manager().release_port(service_name)

def get_service_port(service_name: str) -> Optional[int]:
    """Convenience function to get a service port"""
    return get_port_manager().get_port(service_name) 