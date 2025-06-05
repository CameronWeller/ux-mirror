"""
Unit tests for performance metrics functionality.
"""
import time
import json
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
import pytest

from src.ux_tester.metrics import PerformanceMetrics


class TestPerformanceMetrics:
    """Test cases for PerformanceMetrics class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.metrics = PerformanceMetrics(response_time_threshold=500.0)
    
    def test_init(self):
        """Test metrics initialization."""
        assert self.metrics.response_time_threshold == 500.0
        assert self.metrics.measurements == []
        assert self.metrics.current_operation is None
        assert self.metrics.system_monitoring is False
        assert self.metrics.system_stats == []
    
    @patch('src.ux_tester.metrics.time')
    @patch('src.ux_tester.metrics.datetime')
    def test_start_operation(self, mock_datetime, mock_time):
        """Test starting an operation."""
        mock_time.time.return_value = 1000.0
        mock_datetime.now.return_value.isoformat.return_value = "2024-01-01T12:00:00"
        
        with patch.object(self.metrics, '_get_system_stats', return_value={'cpu': 50}):
            operation_id = self.metrics.start_operation("test_operation", {"key": "value"})
        
        assert operation_id == "test_operation_1000000"
        assert self.metrics.current_operation is not None
        assert self.metrics.current_operation['name'] == "test_operation"
        assert self.metrics.current_operation['metadata'] == {"key": "value"}
    
    def test_start_operation_without_metadata(self):
        """Test starting an operation without metadata."""
        with patch.object(self.metrics, '_get_system_stats', return_value={}):
            with patch('src.ux_tester.metrics.time.time', return_value=1000.0):
                with patch('src.ux_tester.metrics.datetime'):
                    operation_id = self.metrics.start_operation("test_operation")
        
        assert self.metrics.current_operation['metadata'] == {}
    
    @patch('src.ux_tester.metrics.time')
    @patch('src.ux_tester.metrics.datetime')
    def test_end_operation_success(self, mock_datetime, mock_time):
        """Test ending an operation successfully."""
        # Start operation
        mock_time.time.return_value = 1000.0
        mock_datetime.now.return_value.isoformat.return_value = "2024-01-01T12:00:00"
        
        with patch.object(self.metrics, '_get_system_stats', return_value={'cpu': 50}):
            operation_id = self.metrics.start_operation("test_operation")
        
        # Reset time mock for end operation
        mock_time.time.return_value = 1000.5  # 500ms later
        mock_datetime.now.return_value.isoformat.return_value = "2024-01-01T12:00:00.500"
        
        with patch.object(self.metrics, '_assess_performance', return_value={'rating': 'good'}) as mock_assess:
            metrics = self.metrics.end_operation(operation_id)
        
        assert metrics['id'] == operation_id
        assert metrics['name'] == "test_operation"
        assert metrics['duration_ms'] == 500.0
        assert metrics['performance_assessment'] == {'rating': 'good'}
        assert len(self.metrics.measurements) == 1
        assert self.metrics.current_operation is None
        mock_assess.assert_called_once_with(500.0)
    
    def test_end_operation_no_current_operation(self):
        """Test ending operation when none is current."""
        metrics = self.metrics.end_operation()
        assert metrics == {}
    
    def test_end_operation_id_mismatch(self):
        """Test ending operation with wrong ID."""
        with patch.object(self.metrics, '_get_system_stats', return_value={}):
            with patch('src.ux_tester.metrics.time.time', return_value=1000.0):
                with patch('src.ux_tester.metrics.datetime'):
                    self.metrics.start_operation("test_operation")
        
        with patch('src.ux_tester.metrics.time.time', return_value=1000.5):
            with patch('src.ux_tester.metrics.datetime'):
                with patch.object(self.metrics, '_assess_performance', return_value={}):
                    metrics = self.metrics.end_operation("wrong_id")
        
        # Should still work but log warning
        assert metrics['name'] == "test_operation"
    
    @patch('src.ux_tester.metrics.datetime')
    def test_measure_response_time_success(self, mock_datetime):
        """Test successful response time measurement."""
        from datetime import datetime
        
        # Mock datetime parsing
        mock_datetime.strptime.side_effect = [
            datetime(2024, 1, 1, 12, 0, 0, 0),      # before
            datetime(2024, 1, 1, 12, 0, 0, 300000)  # after (300ms later)
        ]
        
        with patch.object(self.metrics, '_assess_response_time', return_value={'rating': 'good'}) as mock_assess:
            result = self.metrics.measure_response_time("20240101_120000_000", "20240101_120000_300")
        
        assert result['response_time_ms'] == 300.0
        assert result['meets_threshold'] is True
        assert result['assessment'] == {'rating': 'good'}
        mock_assess.assert_called_once_with(300.0)
    
    def test_measure_response_time_invalid_format(self):
        """Test response time measurement with invalid timestamp format."""
        result = self.metrics.measure_response_time("invalid_timestamp", "invalid_timestamp")
        
        assert 'error' in result
        assert result['response_time_ms'] == 0
        assert result['assessment'] == 'error'
    
    @patch('src.ux_tester.metrics.threading.Thread')
    def test_start_system_monitoring(self, mock_thread):
        """Test starting system monitoring."""
        mock_thread_instance = Mock()
        mock_thread.return_value = mock_thread_instance
        
        self.metrics.start_system_monitoring(interval=2.0)
        
        assert self.metrics.system_monitoring is True
        assert self.metrics.system_stats == []
        mock_thread.assert_called_once()
        mock_thread_instance.start.assert_called_once()
    
    def test_start_system_monitoring_already_running(self):
        """Test starting system monitoring when already running."""
        self.metrics.system_monitoring = True
        
        self.metrics.start_system_monitoring()
        
        # Should not start new monitoring
        assert self.metrics.system_monitoring is True
    
    def test_stop_system_monitoring(self):
        """Test stopping system monitoring."""
        # Set up monitoring state
        self.metrics.system_monitoring = True
        self.metrics.system_stats = [{'cpu': 50}, {'cpu': 60}]
        self.metrics.monitor_thread = Mock()
        
        result = self.metrics.stop_system_monitoring()
        
        assert self.metrics.system_monitoring is False
        assert result == [{'cpu': 50}, {'cpu': 60}]
        self.metrics.monitor_thread.join.assert_called_once_with(timeout=2.0)
    
    def test_stop_system_monitoring_not_running(self):
        """Test stopping system monitoring when not running."""
        result = self.metrics.stop_system_monitoring()
        
        assert result == []
    
    def test_get_summary_no_measurements(self):
        """Test getting summary with no measurements."""
        summary = self.metrics.get_summary()
        
        assert summary['total_operations'] == 0
        assert 'No performance measurements recorded' in summary['message']
    
    def test_get_summary_with_measurements(self):
        """Test getting summary with measurements."""
        # Add mock measurements
        self.metrics.measurements = [
            {'duration_ms': 100, 'performance_assessment': {'rating': 'excellent'}},
            {'duration_ms': 300, 'performance_assessment': {'rating': 'good'}},
            {'duration_ms': 600, 'performance_assessment': {'rating': 'slow'}}
        ]
        
        with patch.object(self.metrics, '_get_performance_distribution', return_value={'excellent': 1, 'good': 1, 'slow': 1}):
            with patch.object(self.metrics, '_get_system_resource_summary', return_value={'cpu': 'summary'}):
                summary = self.metrics.get_summary()
        
        assert summary['total_operations'] == 3
        assert summary['duration_stats']['min_ms'] == 100
        assert summary['duration_stats']['max_ms'] == 600
        assert abs(summary['duration_stats']['avg_ms'] - 333.333333) < 0.001  # Use tolerance for floating point
        assert summary['duration_stats']['total_ms'] == 1000
        assert summary['performance_distribution'] == {'excellent': 1, 'good': 1, 'slow': 1}
        assert summary['system_resource_usage'] == {'cpu': 'summary'}
    
    @patch('builtins.open')
    @patch('src.ux_tester.metrics.json.dump')
    @patch('src.ux_tester.metrics.datetime')
    def test_export_metrics_success(self, mock_datetime, mock_json_dump, mock_open):
        """Test successful metrics export."""
        mock_datetime.now.return_value.isoformat.return_value = "2024-01-01T12:00:00"
        
        with patch.object(self.metrics, 'get_summary', return_value={'test': 'data'}):
            self.metrics.export_metrics(Path("test_metrics.json"))
        
        mock_open.assert_called_once_with(Path("test_metrics.json"), 'w')
        mock_json_dump.assert_called_once()
    
    @patch('src.ux_tester.metrics.logger')
    def test_export_metrics_error(self, mock_logger):
        """Test metrics export error handling."""
        with patch.object(self.metrics, 'get_summary', side_effect=Exception("Export error")):
            self.metrics.export_metrics(Path("test_metrics.json"))
        
        mock_logger.error.assert_called()
    
    @patch('src.ux_tester.metrics.psutil')
    def test_get_system_stats_success(self, mock_psutil):
        """Test successful system stats collection."""
        mock_psutil.cpu_percent.return_value = 75.0
        mock_psutil.virtual_memory.return_value.percent = 60.0
        mock_psutil.virtual_memory.return_value.available = 1024 * 1024 * 1024  # 1GB
        mock_psutil.disk_usage.return_value.percent = 45.0
        
        with patch('src.ux_tester.metrics.datetime'):
            stats = self.metrics._get_system_stats()
        
        assert stats['cpu_percent'] == 75.0
        assert stats['memory_percent'] == 60.0
        assert stats['memory_available_mb'] == 1024.0
        assert stats['disk_usage_percent'] == 45.0
    
    @patch('src.ux_tester.metrics.psutil')
    def test_get_system_stats_error(self, mock_psutil):
        """Test system stats collection error handling."""
        mock_psutil.cpu_percent.side_effect = Exception("psutil error")
        
        with patch('src.ux_tester.metrics.datetime'):
            stats = self.metrics._get_system_stats()
        
        assert 'error' in stats
        assert stats['error'] == "psutil error"
    
    def test_assess_performance_excellent(self):
        """Test performance assessment for excellent performance."""
        assessment = self.metrics._assess_performance(50.0)
        
        assert assessment['rating'] == 'excellent'
        assert assessment['color'] == 'green'
        assert assessment['meets_threshold'] is True
        assert '50.0ms' in assessment['description']
    
    def test_assess_performance_good(self):
        """Test performance assessment for good performance."""
        assessment = self.metrics._assess_performance(200.0)
        
        assert assessment['rating'] == 'good'
        assert assessment['color'] == 'lightgreen'
        assert assessment['meets_threshold'] is True
    
    def test_assess_performance_acceptable(self):
        """Test performance assessment for acceptable performance."""
        assessment = self.metrics._assess_performance(400.0)
        
        assert assessment['rating'] == 'acceptable'
        assert assessment['color'] == 'yellow'
        assert assessment['meets_threshold'] is True
    
    def test_assess_performance_slow(self):
        """Test performance assessment for slow performance."""
        assessment = self.metrics._assess_performance(700.0)
        
        assert assessment['rating'] == 'slow'
        assert assessment['color'] == 'orange'
        assert assessment['meets_threshold'] is False
    
    def test_assess_performance_very_slow(self):
        """Test performance assessment for very slow performance."""
        assessment = self.metrics._assess_performance(1500.0)
        
        assert assessment['rating'] == 'very_slow'
        assert assessment['color'] == 'red'
        assert assessment['meets_threshold'] is False
    
    def test_assess_response_time_excellent(self):
        """Test response time assessment for excellent response."""
        assessment = self.metrics._assess_response_time(50.0)
        
        assert assessment['rating'] == 'excellent'
        assert assessment['description'] == 'Instant response'
        assert 'No noticeable delay' in assessment['user_perception']
    
    def test_assess_response_time_good(self):
        """Test response time assessment for good response."""
        assessment = self.metrics._assess_response_time(200.0)
        
        assert assessment['rating'] == 'good'
        assert assessment['description'] == 'Fast response'
    
    def test_assess_response_time_acceptable(self):
        """Test response time assessment for acceptable response."""
        assessment = self.metrics._assess_response_time(400.0)
        
        assert assessment['rating'] == 'acceptable'
        assert assessment['description'] == 'Acceptable response'
    
    def test_assess_response_time_slow(self):
        """Test response time assessment for slow response."""
        assessment = self.metrics._assess_response_time(700.0)
        
        assert assessment['rating'] == 'slow'
        assert assessment['description'] == 'Slow response'
        assert 'Users will notice' in assessment['user_perception']
    
    def test_assess_response_time_very_slow(self):
        """Test response time assessment for very slow response."""
        assessment = self.metrics._assess_response_time(1500.0)
        
        assert assessment['rating'] == 'very_slow'
        assert assessment['description'] == 'Very slow response'
        assert 'Frustrating delay' in assessment['user_perception']
    
    def test_get_performance_distribution(self):
        """Test performance distribution calculation."""
        self.metrics.measurements = [
            {'performance_assessment': {'rating': 'excellent'}},
            {'performance_assessment': {'rating': 'good'}},
            {'performance_assessment': {'rating': 'excellent'}},
            {'performance_assessment': {'rating': 'slow'}},
            {'performance_assessment': {'rating': 'unknown'}}  # Should be ignored
        ]
        
        distribution = self.metrics._get_performance_distribution()
        
        assert distribution['excellent'] == 2
        assert distribution['good'] == 1
        assert distribution['acceptable'] == 0
        assert distribution['slow'] == 1
        assert distribution['very_slow'] == 0
    
    def test_get_system_resource_summary_no_data(self):
        """Test system resource summary with no data."""
        summary = self.metrics._get_system_resource_summary()
        
        assert 'No system monitoring data available' in summary['message']
    
    def test_get_system_resource_summary_insufficient_data(self):
        """Test system resource summary with insufficient data."""
        self.metrics.system_stats = [{'invalid': 'data'}]
        
        summary = self.metrics._get_system_resource_summary()
        
        assert 'Insufficient system monitoring data' in summary['message']
    
    def test_get_system_resource_summary_with_data(self):
        """Test system resource summary with valid data."""
        self.metrics.system_stats = [
            {'cpu_percent': 50, 'memory_percent': 60},
            {'cpu_percent': 70, 'memory_percent': 80},
            {'cpu_percent': 60, 'memory_percent': 70}
        ]
        
        summary = self.metrics._get_system_resource_summary()
        
        assert summary['cpu_usage']['min_percent'] == 50
        assert summary['cpu_usage']['max_percent'] == 70
        assert summary['cpu_usage']['avg_percent'] == 60.0
        assert summary['memory_usage']['min_percent'] == 60
        assert summary['memory_usage']['max_percent'] == 80
        assert summary['memory_usage']['avg_percent'] == 70.0
        assert summary['monitoring_duration_seconds'] == 3 