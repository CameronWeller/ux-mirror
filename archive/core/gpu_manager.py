#!/usr/bin/env python3
"""
UX-MIRROR GPU Manager
====================

Centralized GPU/CUDA resource management with intelligent fallback strategies.
Provides a unified interface for GPU operations across all modules.

Author: UX-MIRROR System
Version: 1.0.0
"""

import logging
import threading
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass
from enum import Enum
import psutil

# Try importing GPU libraries
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    torch = None
    TORCH_AVAILABLE = False

try:
    import pynvml
    NVML_AVAILABLE = True
except ImportError:
    pynvml = None
    NVML_AVAILABLE = False

logger = logging.getLogger(__name__)


class ComputeBackend(Enum):
    """Available compute backends"""
    CUDA = "cuda"
    ROCM = "rocm"
    MPS = "mps"  # Apple Silicon
    CPU = "cpu"
    UNKNOWN = "unknown"


@dataclass
class GPUInfo:
    """GPU device information"""
    device_id: int
    name: str
    memory_total: int  # bytes
    memory_free: int  # bytes
    memory_used: int  # bytes
    utilization: float  # percentage
    temperature: Optional[float] = None
    power_draw: Optional[float] = None
    compute_capability: Optional[Tuple[int, int]] = None


@dataclass
class ComputeDevice:
    """Compute device abstraction"""
    backend: ComputeBackend
    device_id: int
    device: Optional[Any] = None  # torch.device or similar
    info: Optional[GPUInfo] = None


class GPUManager:
    """
    Singleton GPU Manager for centralized resource management.
    
    Features:
    - Automatic backend detection (CUDA, ROCm, MPS, CPU)
    - Memory monitoring and allocation tracking
    - Intelligent fallback strategies
    - Thread-safe operations
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._initialized = True
        self.backend = ComputeBackend.UNKNOWN
        self.devices: List[ComputeDevice] = []
        self.primary_device: Optional[ComputeDevice] = None
        self.allocation_tracker: Dict[str, Dict[str, Any]] = {}
        
        # Initialize GPU monitoring
        if NVML_AVAILABLE:
            try:
                pynvml.nvmlInit()
                self.nvml_initialized = True
            except Exception as e:
                logger.warning(f"Failed to initialize NVML: {e}")
                self.nvml_initialized = False
        else:
            self.nvml_initialized = False
        
        # Detect available backends
        self._detect_backends()
        
        logger.info(f"GPU Manager initialized with backend: {self.backend.value}")
        if self.primary_device:
            logger.info(f"Primary device: {self.primary_device.info.name if self.primary_device.info else 'Unknown'}")
    
    def _detect_backends(self):
        """Detect available compute backends"""
        # Check for CUDA
        if TORCH_AVAILABLE and torch.cuda.is_available():
            self.backend = ComputeBackend.CUDA
            self._initialize_cuda_devices()
        # Check for ROCm
        elif TORCH_AVAILABLE and hasattr(torch, 'hip') and torch.hip.is_available():
            self.backend = ComputeBackend.ROCM
            self._initialize_rocm_devices()
        # Check for Apple Silicon MPS
        elif TORCH_AVAILABLE and hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            self.backend = ComputeBackend.MPS
            self._initialize_mps_devices()
        # Fallback to CPU
        else:
            self.backend = ComputeBackend.CPU
            self._initialize_cpu_device()
    
    def _initialize_cuda_devices(self):
        """Initialize CUDA devices"""
        if not TORCH_AVAILABLE:
            return
            
        device_count = torch.cuda.device_count()
        for i in range(device_count):
            device = torch.device(f'cuda:{i}')
            info = self._get_cuda_device_info(i)
            compute_device = ComputeDevice(
                backend=ComputeBackend.CUDA,
                device_id=i,
                device=device,
                info=info
            )
            self.devices.append(compute_device)
        
        if self.devices:
            self.primary_device = self.devices[0]
    
    def _get_cuda_device_info(self, device_id: int) -> Optional[GPUInfo]:
        """Get CUDA device information"""
        if not TORCH_AVAILABLE:
            return None
            
        props = torch.cuda.get_device_properties(device_id)
        
        # Get memory info
        memory_total = props.total_memory
        memory_free = torch.cuda.memory_reserved(device_id) - torch.cuda.memory_allocated(device_id)
        memory_used = torch.cuda.memory_allocated(device_id)
        
        # Get utilization from NVML if available
        utilization = 0.0
        temperature = None
        power_draw = None
        
        if self.nvml_initialized:
            try:
                handle = pynvml.nvmlDeviceGetHandleByIndex(device_id)
                util = pynvml.nvmlDeviceGetUtilizationRates(handle)
                utilization = util.gpu
                
                try:
                    temperature = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
                except:
                    pass
                
                try:
                    power_draw = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000.0  # Convert to watts
                except:
                    pass
            except Exception as e:
                logger.debug(f"Failed to get NVML data for device {device_id}: {e}")
        
        return GPUInfo(
            device_id=device_id,
            name=props.name,
            memory_total=memory_total,
            memory_free=memory_free,
            memory_used=memory_used,
            utilization=utilization,
            temperature=temperature,
            power_draw=power_draw,
            compute_capability=(props.major, props.minor)
        )
    
    def _initialize_rocm_devices(self):
        """Initialize ROCm devices"""
        # Similar to CUDA but for AMD GPUs
        # TODO: Implement ROCm support
        logger.info("ROCm support not yet implemented, falling back to CPU")
        self._initialize_cpu_device()
    
    def _initialize_mps_devices(self):
        """Initialize Apple Silicon MPS devices"""
        if not TORCH_AVAILABLE:
            return
            
        device = torch.device('mps')
        # MPS doesn't provide detailed device info like CUDA
        info = GPUInfo(
            device_id=0,
            name="Apple Silicon GPU",
            memory_total=0,  # Not available through MPS
            memory_free=0,
            memory_used=0,
            utilization=0.0
        )
        
        compute_device = ComputeDevice(
            backend=ComputeBackend.MPS,
            device_id=0,
            device=device,
            info=info
        )
        self.devices.append(compute_device)
        self.primary_device = compute_device
    
    def _initialize_cpu_device(self):
        """Initialize CPU as fallback device"""
        cpu_info = psutil.virtual_memory()
        
        device = None
        if TORCH_AVAILABLE:
            device = torch.device('cpu')
        
        info = GPUInfo(
            device_id=0,
            name=f"CPU ({psutil.cpu_count()} cores)",
            memory_total=cpu_info.total,
            memory_free=cpu_info.available,
            memory_used=cpu_info.used,
            utilization=psutil.cpu_percent(interval=0.1)
        )
        
        compute_device = ComputeDevice(
            backend=ComputeBackend.CPU,
            device_id=0,
            device=device,
            info=info
        )
        self.devices.append(compute_device)
        self.primary_device = compute_device
    
    def get_device(self, preferred_device_id: Optional[int] = None) -> ComputeDevice:
        """
        Get a compute device for processing.
        
        Args:
            preferred_device_id: Preferred device ID (if available)
            
        Returns:
            ComputeDevice object
        """
        if preferred_device_id is not None and 0 <= preferred_device_id < len(self.devices):
            return self.devices[preferred_device_id]
        
        return self.primary_device or self.devices[0] if self.devices else None
    
    def allocate_memory(self, component_id: str, size_mb: float, device_id: Optional[int] = None) -> bool:
        """
        Track memory allocation for a component.
        
        Args:
            component_id: Unique identifier for the component
            size_mb: Memory size in megabytes
            device_id: Target device ID
            
        Returns:
            True if allocation is successful
        """
        device = self.get_device(device_id)
        if not device or not device.info:
            return False
        
        size_bytes = int(size_mb * 1024 * 1024)
        
        # Check if enough memory is available
        if device.info.memory_free < size_bytes:
            logger.warning(f"Not enough memory for {component_id}: requested {size_mb}MB, available {device.info.memory_free / 1024 / 1024:.1f}MB")
            return False
        
        # Track allocation
        self.allocation_tracker[component_id] = {
            'device_id': device.device_id,
            'size_bytes': size_bytes,
            'backend': device.backend.value
        }
        
        logger.debug(f"Allocated {size_mb}MB for {component_id} on device {device.device_id}")
        return True
    
    def release_memory(self, component_id: str):
        """Release tracked memory allocation"""
        if component_id in self.allocation_tracker:
            del self.allocation_tracker[component_id]
            logger.debug(f"Released memory allocation for {component_id}")
    
    def get_memory_usage(self, device_id: Optional[int] = None) -> Dict[str, float]:
        """
        Get current memory usage statistics.
        
        Returns:
            Dictionary with memory statistics in MB
        """
        device = self.get_device(device_id)
        if not device or not device.info:
            return {}
        
        # Update device info if CUDA
        if device.backend == ComputeBackend.CUDA and TORCH_AVAILABLE:
            device.info = self._get_cuda_device_info(device.device_id)
        
        return {
            'total_mb': device.info.memory_total / 1024 / 1024,
            'used_mb': device.info.memory_used / 1024 / 1024,
            'free_mb': device.info.memory_free / 1024 / 1024,
            'utilization_percent': device.info.utilization
        }
    
    def clear_cache(self, device_id: Optional[int] = None):
        """Clear GPU cache if supported"""
        device = self.get_device(device_id)
        if not device:
            return
        
        if device.backend == ComputeBackend.CUDA and TORCH_AVAILABLE:
            torch.cuda.empty_cache()
            logger.info(f"Cleared CUDA cache for device {device.device_id}")
        elif device.backend == ComputeBackend.MPS and TORCH_AVAILABLE:
            # MPS doesn't have explicit cache clearing
            pass
    
    def create_tensor(self, data, dtype=None, device_id: Optional[int] = None):
        """
        Create a tensor on the specified device with fallback support.
        
        Args:
            data: Input data
            dtype: Data type (torch dtype if available)
            device_id: Target device ID
            
        Returns:
            Tensor on appropriate device or numpy array as fallback
        """
        device = self.get_device(device_id)
        
        if not TORCH_AVAILABLE or not device or device.backend == ComputeBackend.CPU:
            # Fallback to numpy
            import numpy as np
            return np.array(data, dtype=dtype if dtype else np.float32)
        
        # Create torch tensor
        if dtype is None:
            dtype = torch.float32
        
        tensor = torch.tensor(data, dtype=dtype)
        if device.device:
            tensor = tensor.to(device.device)
        
        return tensor
    
    def move_to_device(self, data, device_id: Optional[int] = None):
        """Move data to specified device with fallback support"""
        device = self.get_device(device_id)
        
        if not device:
            return data
        
        if TORCH_AVAILABLE and hasattr(data, 'to') and device.device:
            return data.to(device.device)
        
        return data
    
    def get_backend_info(self) -> Dict[str, Any]:
        """Get information about the current backend"""
        return {
            'backend': self.backend.value,
            'device_count': len(self.devices),
            'torch_available': TORCH_AVAILABLE,
            'nvml_available': NVML_AVAILABLE,
            'primary_device': {
                'id': self.primary_device.device_id if self.primary_device else None,
                'name': self.primary_device.info.name if self.primary_device and self.primary_device.info else None
            },
            'allocations': {
                component: {
                    'size_mb': info['size_bytes'] / 1024 / 1024,
                    'device_id': info['device_id']
                }
                for component, info in self.allocation_tracker.items()
            }
        }
    
    def shutdown(self):
        """Cleanup GPU resources"""
        if self.nvml_initialized:
            try:
                pynvml.nvmlShutdown()
            except:
                pass
        
        self.allocation_tracker.clear()
        logger.info("GPU Manager shutdown complete")


# Singleton instance getter
def get_gpu_manager() -> GPUManager:
    """Get the singleton GPU Manager instance"""
    return GPUManager()