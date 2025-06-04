"""
Performance metrics and timing measurements for UX testing.

This module provides performance tracking and analysis capabilities.
"""
import time
import psutil
import threading
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)


class PerformanceMetrics:
    """
    Tracks and analyzes performance metrics during UX testing.
    
    Provides timing measurements, system resource monitoring, and
    performance analysis capabilities.
    """
    
    def __init__(self, response_time_threshold: float = 500.0):
        """
        Initialize performance metrics tracking.
        
        Args:
            response_time_threshold: Threshold for response time warnings (ms)
        """
        self.response_time_threshold = response_time_threshold
        self.measurements: List[Dict[str, Any]] = []
        self.current_operation: Optional[Dict[str, Any]] = None
        self.system_monitoring = False
        self.system_stats: List[Dict[str, Any]] = []
        
    def start_operation(self, operation_name: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Start timing an operation.
        
        Args:
            operation_name: Name of the operation being timed
            metadata: Optional metadata about the operation
            
        Returns:
            Operation ID for tracking
        """
        operation_id = f"{operation_name}_{int(time.time() * 1000)}"
        
        self.current_operation = {
            'id': operation_id,
            'name': operation_name,
            'start_time': time.time(),
            'start_timestamp': datetime.now().isoformat(),
            'metadata': metadata or {},
            'system_stats_start': self._get_system_stats()
        }
        
        logger.debug(f"Started operation: {operation_name} (ID: {operation_id})")
        return operation_id
    
    def end_operation(self, operation_id: Optional[str] = None) -> Dict[str, Any]:
        """
        End timing an operation and record metrics.
        
        Args:
            operation_id: Operation ID (optional, uses current operation if not provided)
            
        Returns:
            Performance metrics for the operation
        """
        if not self.current_operation:
            logger.warning("No operation currently being tracked")
            return {}
        
        if operation_id and operation_id != self.current_operation['id']:
            logger.warning(f"Operation ID mismatch: expected {self.current_operation['id']}, got {operation_id}")
        
        end_time = time.time()
        end_timestamp = datetime.now().isoformat()
        duration_ms = (end_time - self.current_operation['start_time']) * 1000
        
        metrics = {
            'id': self.current_operation['id'],
            'name': self.current_operation['name'],
            'start_time': self.current_operation['start_timestamp'],
            'end_time': end_timestamp,
            'duration_ms': duration_ms,
            'metadata': self.current_operation['metadata'],
            'system_stats': {
                'start': self.current_operation['system_stats_start'],
                'end': self._get_system_stats()
            },
            'performance_assessment': self._assess_performance(duration_ms)
        }
        
        self.measurements.append(metrics)
        self.current_operation = None
        
        logger.info(f"Operation completed: {metrics['name']} in {duration_ms:.1f}ms")
        return metrics
    
    def measure_response_time(self, before_timestamp: str, after_timestamp: str) -> Dict[str, Any]:
        """
        Measure response time between two timestamps.
        
        Args:
            before_timestamp: Timestamp before interaction
            after_timestamp: Timestamp after interaction
            
        Returns:
            Response time metrics
        """
        try:
            # Parse timestamps from filenames (format: YYYYMMDD_HHMMSS_fff)
            before_time = datetime.strptime(before_timestamp, "%Y%m%d_%H%M%S_%f")
            after_time = datetime.strptime(after_timestamp, "%Y%m%d_%H%M%S_%f")
            
            response_time_ms = (after_time - before_time).total_seconds() * 1000
            
            metrics = {
                'before_timestamp': before_timestamp,
                'after_timestamp': after_timestamp,
                'response_time_ms': response_time_ms,
                'assessment': self._assess_response_time(response_time_ms),
                'meets_threshold': response_time_ms <= self.response_time_threshold
            }
            
            logger.debug(f"Response time measured: {response_time_ms:.1f}ms")
            return metrics
            
        except ValueError as e:
            logger.error(f"Failed to parse timestamps: {e}")
            return {
                'error': f"Invalid timestamp format: {e}",
                'response_time_ms': 0,
                'assessment': 'error'
            }
    
    def start_system_monitoring(self, interval: float = 1.0) -> None:
        """
        Start monitoring system resources.
        
        Args:
            interval: Monitoring interval in seconds
        """
        if self.system_monitoring:
            logger.warning("System monitoring already running")
            return
        
        self.system_monitoring = True
        self.system_stats = []
        
        def monitor():
            while self.system_monitoring:
                stats = self._get_system_stats()
                self.system_stats.append(stats)
                time.sleep(interval)
        
        self.monitor_thread = threading.Thread(target=monitor, daemon=True)
        self.monitor_thread.start()
        
        logger.info(f"Started system monitoring (interval: {interval}s)")
    
    def stop_system_monitoring(self) -> List[Dict[str, Any]]:
        """
        Stop monitoring system resources.
        
        Returns:
            List of collected system statistics
        """
        if not self.system_monitoring:
            logger.warning("System monitoring not running")
            return []
        
        self.system_monitoring = False
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.join(timeout=2.0)
        
        logger.info(f"Stopped system monitoring ({len(self.system_stats)} measurements)")
        return self.system_stats.copy()
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary of all performance measurements.
        
        Returns:
            Performance summary statistics
        """
        if not self.measurements:
            return {
                'total_operations': 0,
                'message': 'No performance measurements recorded'
            }
        
        durations = [m['duration_ms'] for m in self.measurements]
        
        summary = {
            'total_operations': len(self.measurements),
            'duration_stats': {
                'min_ms': min(durations),
                'max_ms': max(durations),
                'avg_ms': sum(durations) / len(durations),
                'total_ms': sum(durations)
            },
            'performance_distribution': self._get_performance_distribution(),
            'system_resource_usage': self._get_system_resource_summary(),
            'measurements': self.measurements
        }
        
        return summary
    
    def export_metrics(self, output_path: Path) -> None:
        """
        Export performance metrics to JSON file.
        
        Args:
            output_path: Path to save metrics file
        """
        try:
            summary = self.get_summary()
            summary['export_timestamp'] = datetime.now().isoformat()
            summary['system_stats'] = self.system_stats
            
            with open(output_path, 'w') as f:
                json.dump(summary, f, indent=2, default=str)
            
            logger.info(f"Performance metrics exported to: {output_path}")
            
        except Exception as e:
            logger.error(f"Failed to export metrics: {e}")
    
    def _get_system_stats(self) -> Dict[str, Any]:
        """Get current system resource statistics."""
        try:
            return {
                'timestamp': datetime.now().isoformat(),
                'cpu_percent': psutil.cpu_percent(interval=None),
                'memory_percent': psutil.virtual_memory().percent,
                'memory_available_mb': psutil.virtual_memory().available / (1024 * 1024),
                'disk_usage_percent': psutil.disk_usage('/').percent if hasattr(psutil, 'disk_usage') else 0
            }
        except Exception as e:
            logger.warning(f"Failed to get system stats: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def _assess_performance(self, duration_ms: float) -> Dict[str, Any]:
        """Assess performance based on duration."""
        if duration_ms < 100:
            rating = 'excellent'
            color = 'green'
        elif duration_ms < 300:
            rating = 'good'
            color = 'lightgreen'
        elif duration_ms < 500:
            rating = 'acceptable'
            color = 'yellow'
        elif duration_ms < 1000:
            rating = 'slow'
            color = 'orange'
        else:
            rating = 'very_slow'
            color = 'red'
        
        return {
            'rating': rating,
            'color': color,
            'meets_threshold': duration_ms <= self.response_time_threshold,
            'description': f"{rating.replace('_', ' ').title()} ({duration_ms:.1f}ms)"
        }
    
    def _assess_response_time(self, response_time_ms: float) -> Dict[str, Any]:
        """Assess response time quality."""
        if response_time_ms < 100:
            return {
                'rating': 'excellent',
                'description': 'Instant response',
                'user_perception': 'No noticeable delay'
            }
        elif response_time_ms < 300:
            return {
                'rating': 'good',
                'description': 'Fast response',
                'user_perception': 'Slight delay but feels immediate'
            }
        elif response_time_ms < 500:
            return {
                'rating': 'acceptable',
                'description': 'Acceptable response',
                'user_perception': 'Noticeable but acceptable delay'
            }
        elif response_time_ms < 1000:
            return {
                'rating': 'slow',
                'description': 'Slow response',
                'user_perception': 'Users will notice the delay'
            }
        else:
            return {
                'rating': 'very_slow',
                'description': 'Very slow response',
                'user_perception': 'Frustrating delay for users'
            }
    
    def _get_performance_distribution(self) -> Dict[str, int]:
        """Get distribution of performance ratings."""
        distribution = {
            'excellent': 0,
            'good': 0,
            'acceptable': 0,
            'slow': 0,
            'very_slow': 0
        }
        
        for measurement in self.measurements:
            rating = measurement.get('performance_assessment', {}).get('rating', 'unknown')
            if rating in distribution:
                distribution[rating] += 1
        
        return distribution
    
    def _get_system_resource_summary(self) -> Dict[str, Any]:
        """Get summary of system resource usage."""
        if not self.system_stats:
            return {'message': 'No system monitoring data available'}
        
        cpu_values = [s.get('cpu_percent', 0) for s in self.system_stats if 'cpu_percent' in s]
        memory_values = [s.get('memory_percent', 0) for s in self.system_stats if 'memory_percent' in s]
        
        if not cpu_values or not memory_values:
            return {'message': 'Insufficient system monitoring data'}
        
        return {
            'cpu_usage': {
                'min_percent': min(cpu_values),
                'max_percent': max(cpu_values),
                'avg_percent': sum(cpu_values) / len(cpu_values)
            },
            'memory_usage': {
                'min_percent': min(memory_values),
                'max_percent': max(memory_values),
                'avg_percent': sum(memory_values) / len(memory_values)
            },
            'monitoring_duration_seconds': len(self.system_stats)
        } 