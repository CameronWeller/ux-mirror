#!/usr/bin/env python3
"""
UX-MIRROR VM Orchestrator
========================

Advanced VM management system for autonomous Windows VM operations.
Integrates with the core UX-MIRROR agent system for intelligent automation.

Author: UX-MIRROR System
Version: 1.0.0
"""

import asyncio
import logging
import json
import time
import uuid
import subprocess
import psutil
import os
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path

import vboxapi
import paramiko
import vncdotool.api
from mss import mss
import cv2
import numpy as np
from PIL import Image

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class VMState(Enum):
    """VM operational states"""
    POWERED_OFF = "PoweredOff"
    STARTING = "Starting"
    RUNNING = "Running"
    PAUSED = "Paused"
    SAVING = "Saving"
    STOPPING = "Stopping"
    ERROR = "Error"

class VMTaskType(Enum):
    """Types of VM tasks"""
    CREATE = "create_vm"
    START = "start_vm"
    STOP = "stop_vm"
    SNAPSHOT = "snapshot_vm"
    RESTORE = "restore_vm"
    CLONE = "clone_vm"
    DELETE = "delete_vm"
    SCREEN_CAPTURE = "screen_capture"
    REMOTE_COMMAND = "remote_command"
    FILE_TRANSFER = "file_transfer"

@dataclass
class VMConfiguration:
    """VM configuration parameters"""
    name: str
    memory_mb: int = 4096
    disk_size_gb: int = 50
    cpu_cores: int = 2
    os_type: str = "Windows11_64"
    iso_path: Optional[str] = None
    network_adapter: str = "NAT"
    enable_3d: bool = True
    enable_clipboard: bool = True
    rdp_enabled: bool = True
    rdp_port: int = 3389

@dataclass
class VMInfo:
    """Information about a managed VM"""
    vm_id: str
    name: str
    state: VMState
    configuration: VMConfiguration
    uuid: str
    session_id: Optional[str]
    vnc_port: Optional[int]
    rdp_port: Optional[int]
    ssh_port: Optional[int]
    ip_address: Optional[str]
    creation_time: datetime
    last_activity: datetime
    snapshots: List[str]
    performance_metrics: Dict[str, Any]

class VirtualBoxManager:
    """VirtualBox hypervisor management"""
    
    def __init__(self):
        self.vbox = None
        self.session = None
        try:
            self.vbox_manager = vboxapi.VirtualBoxManager(None, None)
            self.vbox = self.vbox_manager.vbox
            logger.info("VirtualBox API initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize VirtualBox API: {e}")
            raise
    
    def create_vm(self, config: VMConfiguration) -> str:
        """Create a new VM with specified configuration"""
        try:
            # Create VM
            vm = self.vbox.createMachine(
                "", config.name, [], config.os_type, ""
            )
            
            # Configure memory
            vm.memorySize = config.memory_mb
            vm.CPUCount = config.cpu_cores
            
            # Enable hardware virtualization
            vm.setHWVirtProperty(self.vbox_manager.constants.HWVirtPropertyType_Enabled, True)
            vm.setHWVirtProperty(self.vbox_manager.constants.HWVirtPropertyType_NestedPaging, True)
            
            # Configure display
            vm.setVideoAdapter(self.vbox_manager.constants.VideoAdapter_VMSVGA)
            vm.setVRAMSize(128)  # 128MB VRAM
            if config.enable_3d:
                vm.setAccelerate3DEnabled(True)
            
            # Register VM
            self.vbox.registerMachine(vm)
            
            # Configure storage
            session = self.vbox_manager.getSessionObject(self.vbox)
            vm.lockMachine(session, self.vbox_manager.constants.LockType_Write)
            
            mutable_vm = session.machine
            
            # Create hard disk
            medium = self.vbox.createMedium("VDI", f"{config.name}.vdi", 
                                          self.vbox_manager.constants.AccessMode_ReadWrite,
                                          self.vbox_manager.constants.DeviceType_HardDisk)
            
            # Create storage controller
            controller = mutable_vm.addStorageController(
                "SATA Controller", 
                self.vbox_manager.constants.StorageBus_SATA
            )
            controller.setControllerType(self.vbox_manager.constants.StorageControllerType_IntelAhci)
            
            # Attach hard disk
            mutable_vm.attachDevice(
                "SATA Controller", 0, 0,
                self.vbox_manager.constants.DeviceType_HardDisk,
                medium
            )
            
            # Configure network
            network_adapter = mutable_vm.getNetworkAdapter(0)
            network_adapter.enabled = True
            network_adapter.attachmentType = self.vbox_manager.constants.NetworkAttachmentType_NAT
            
            # Enable RDP if requested
            if config.rdp_enabled:
                vrde_server = mutable_vm.VRDEServer
                vrde_server.enabled = True
                vrde_server.setVRDEProperty("TCP/Ports", str(config.rdp_port))
            
            mutable_vm.saveSettings()
            session.unlockMachine()
            
            logger.info(f"VM '{config.name}' created successfully")
            return vm.id
            
        except Exception as e:
            logger.error(f"Failed to create VM '{config.name}': {e}")
            raise
    
    def start_vm(self, vm_name: str) -> bool:
        """Start a VM"""
        try:
            vm = self.vbox.findMachine(vm_name)
            session = self.vbox_manager.getSessionObject(self.vbox)
            
            # Start VM in headless mode for automation
            progress = vm.launchVMProcess(session, "headless", [])
            progress.waitForCompletion(-1)
            
            if progress.resultCode == 0:
                logger.info(f"VM '{vm_name}' started successfully")
                return True
            else:
                logger.error(f"Failed to start VM '{vm_name}': {progress.errorInfo}")
                return False
                
        except Exception as e:
            logger.error(f"Error starting VM '{vm_name}': {e}")
            return False
    
    def stop_vm(self, vm_name: str, force: bool = False) -> bool:
        """Stop a VM"""
        try:
            vm = self.vbox.findMachine(vm_name)
            session = self.vbox_manager.getSessionObject(self.vbox)
            
            if vm.state == self.vbox_manager.constants.MachineState_Running:
                vm.lockMachine(session, self.vbox_manager.constants.LockType_Shared)
                
                if force:
                    session.console.powerDown()
                else:
                    session.console.saveState()
                
                session.unlockMachine()
                logger.info(f"VM '{vm_name}' stopped successfully")
                return True
            else:
                logger.warning(f"VM '{vm_name}' is not running")
                return True
                
        except Exception as e:
            logger.error(f"Error stopping VM '{vm_name}': {e}")
            return False
    
    def get_vm_info(self, vm_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed VM information"""
        try:
            vm = self.vbox.findMachine(vm_name)
            
            info = {
                "name": vm.name,
                "uuid": vm.id,
                "state": vm.state,
                "memory_mb": vm.memorySize,
                "cpu_count": vm.CPUCount,
                "vram_mb": vm.VRAMSize,
                "os_type": vm.OSTypeId,
                "snapshots": [snapshot.name for snapshot in vm.snapshots]
            }
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting VM info for '{vm_name}': {e}")
            return None
    
    def create_snapshot(self, vm_name: str, snapshot_name: str, description: str = "") -> bool:
        """Create a VM snapshot"""
        try:
            vm = self.vbox.findMachine(vm_name)
            session = self.vbox_manager.getSessionObject(self.vbox)
            
            vm.lockMachine(session, self.vbox_manager.constants.LockType_Shared)
            
            progress = session.console.takeSnapshot(snapshot_name, description)
            progress.waitForCompletion(-1)
            
            session.unlockMachine()
            
            if progress.resultCode == 0:
                logger.info(f"Snapshot '{snapshot_name}' created for VM '{vm_name}'")
                return True
            else:
                logger.error(f"Failed to create snapshot: {progress.errorInfo}")
                return False
                
        except Exception as e:
            logger.error(f"Error creating snapshot for VM '{vm_name}': {e}")
            return False

class VMScreenCapture:
    """VM screen capture and visual analysis"""
    
    def __init__(self, vm_info: VMInfo):
        self.vm_info = vm_info
        self.vnc_client = None
        self.last_screenshot = None
        
    async def connect_vnc(self) -> bool:
        """Connect to VM via VNC for screen capture"""
        try:
            if self.vm_info.vnc_port:
                self.vnc_client = vncdotool.api.connect(
                    f"localhost::{self.vm_info.vnc_port}"
                )
                logger.info(f"VNC connected to VM '{self.vm_info.name}' on port {self.vm_info.vnc_port}")
                return True
            else:
                logger.error(f"No VNC port configured for VM '{self.vm_info.name}'")
                return False
                
        except Exception as e:
            logger.error(f"Failed to connect VNC to VM '{self.vm_info.name}': {e}")
            return False
    
    async def capture_screenshot(self) -> Optional[np.ndarray]:
        """Capture screenshot from VM"""
        try:
            if self.vnc_client:
                # Capture via VNC
                screenshot = self.vnc_client.capture()
                screenshot_array = np.array(screenshot)
                self.last_screenshot = screenshot_array
                return screenshot_array
            else:
                logger.error(f"VNC not connected for VM '{self.vm_info.name}'")
                return None
                
        except Exception as e:
            logger.error(f"Failed to capture screenshot from VM '{self.vm_info.name}': {e}")
            return None
    
    def analyze_ui_elements(self, screenshot: np.ndarray) -> List[Dict[str, Any]]:
        """Analyze UI elements in screenshot using computer vision"""
        try:
            # Convert to grayscale for analysis
            gray = cv2.cvtColor(screenshot, cv2.COLOR_RGB2GRAY)
            
            # Detect edges for UI element boundaries
            edges = cv2.Canny(gray, 50, 150, apertureSize=3)
            
            # Find contours (potential UI elements)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            ui_elements = []
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                
                # Filter by size (ignore very small elements)
                if w > 10 and h > 10:
                    ui_elements.append({
                        "type": "ui_element",
                        "bounds": {"x": int(x), "y": int(y), "width": int(w), "height": int(h)},
                        "area": int(w * h),
                        "confidence": 0.7
                    })
            
            return ui_elements
            
        except Exception as e:
            logger.error(f"Error analyzing UI elements: {e}")
            return []

class VMRemoteControl:
    """VM remote control via SSH and other protocols"""
    
    def __init__(self, vm_info: VMInfo):
        self.vm_info = vm_info
        self.ssh_client = None
        
    async def connect_ssh(self, username: str, password: str) -> bool:
        """Connect to VM via SSH"""
        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            self.ssh_client.connect(
                hostname=self.vm_info.ip_address or "localhost",
                port=self.vm_info.ssh_port or 22,
                username=username,
                password=password,
                timeout=30
            )
            
            logger.info(f"SSH connected to VM '{self.vm_info.name}'")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect SSH to VM '{self.vm_info.name}': {e}")
            return False
    
    async def execute_command(self, command: str) -> Tuple[str, str, int]:
        """Execute command in VM via SSH"""
        try:
            if not self.ssh_client:
                raise Exception("SSH not connected")
            
            stdin, stdout, stderr = self.ssh_client.exec_command(command)
            
            stdout_data = stdout.read().decode('utf-8')
            stderr_data = stderr.read().decode('utf-8')
            exit_code = stdout.channel.recv_exit_status()
            
            logger.info(f"Command executed in VM '{self.vm_info.name}': {command}")
            return stdout_data, stderr_data, exit_code
            
        except Exception as e:
            logger.error(f"Failed to execute command in VM '{self.vm_info.name}': {e}")
            return "", str(e), -1
    
    async def transfer_file(self, local_path: str, remote_path: str, upload: bool = True) -> bool:
        """Transfer file to/from VM"""
        try:
            if not self.ssh_client:
                raise Exception("SSH not connected")
            
            sftp = self.ssh_client.open_sftp()
            
            if upload:
                sftp.put(local_path, remote_path)
                logger.info(f"File uploaded to VM '{self.vm_info.name}': {local_path} -> {remote_path}")
            else:
                sftp.get(remote_path, local_path)
                logger.info(f"File downloaded from VM '{self.vm_info.name}': {remote_path} -> {local_path}")
            
            sftp.close()
            return True
            
        except Exception as e:
            logger.error(f"Failed to transfer file with VM '{self.vm_info.name}': {e}")
            return False

class VMOrchestrator:
    """
    Main VM Orchestrator for UX-MIRROR system.
    
    Manages VM lifecycle, coordinates with agents, and provides intelligent automation.
    """
    
    def __init__(self, config_path: str = "config/vm_orchestrator.json"):
        self.config_path = config_path
        self.config = {}
        self.vbox_manager = VirtualBoxManager()
        
        # VM management
        self.managed_vms: Dict[str, VMInfo] = {}
        self.active_sessions: Dict[str, Any] = {}
        
        # Task management
        self.pending_tasks: asyncio.Queue = asyncio.Queue()
        self.active_tasks: Dict[str, Any] = {}
        
        # Performance monitoring
        self.performance_metrics = {
            "total_vms_created": 0,
            "total_vms_running": 0,
            "total_tasks_completed": 0,
            "average_task_time": 0.0,
            "system_load": 0.0
        }
        
        logger.info("VM Orchestrator initialized")
    
    async def initialize(self):
        """Initialize the VM orchestrator"""
        await self._load_configuration()
        await self._discover_existing_vms()
        
        # Start background tasks
        background_tasks = [
            self._process_vm_tasks(),
            self._monitor_vm_health(),
            self._update_performance_metrics(),
            self._cleanup_inactive_vms()
        ]
        
        await asyncio.gather(*background_tasks, return_exceptions=True)
    
    async def _load_configuration(self):
        """Load orchestrator configuration"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    self.config = json.load(f)
            else:
                # Default configuration
                self.config = {
                    "vm_defaults": {
                        "memory_mb": 4096,
                        "disk_size_gb": 50,
                        "cpu_cores": 2,
                        "os_type": "Windows11_64"
                    },
                    "resource_limits": {
                        "max_concurrent_vms": 5,
                        "max_memory_usage_percent": 80,
                        "max_cpu_usage_percent": 90
                    },
                    "automation": {
                        "auto_cleanup_hours": 24,
                        "health_check_interval": 300,
                        "snapshot_frequency_hours": 6
                    },
                    "networking": {
                        "vnc_port_range": [5900, 5950],
                        "rdp_port_range": [3389, 3400],
                        "ssh_port_range": [2222, 2232]
                    }
                }
                
                # Save default configuration
                os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
                with open(self.config_path, 'w') as f:
                    json.dump(self.config, f, indent=2)
            
            logger.info("VM Orchestrator configuration loaded")
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise
    
    async def _discover_existing_vms(self):
        """Discover and register existing VMs"""
        try:
            # Get list of VMs from VirtualBox
            for vm in self.vbox_manager.vbox.machines:
                vm_info = self.vbox_manager.get_vm_info(vm.name)
                if vm_info:
                    # Create VMInfo object
                    vm_config = VMConfiguration(
                        name=vm_info["name"],
                        memory_mb=vm_info["memory_mb"],
                        cpu_cores=vm_info["cpu_count"]
                    )
                    
                    managed_vm = VMInfo(
                        vm_id=vm_info["uuid"],
                        name=vm_info["name"],
                        state=VMState.POWERED_OFF,  # Will be updated in health check
                        configuration=vm_config,
                        uuid=vm_info["uuid"],
                        session_id=None,
                        vnc_port=None,
                        rdp_port=None,
                        ssh_port=None,
                        ip_address=None,
                        creation_time=datetime.now(),
                        last_activity=datetime.now(),
                        snapshots=vm_info["snapshots"],
                        performance_metrics={}
                    )
                    
                    self.managed_vms[vm_info["name"]] = managed_vm
                    
            logger.info(f"Discovered {len(self.managed_vms)} existing VMs")
            
        except Exception as e:
            logger.error(f"Failed to discover existing VMs: {e}")
    
    async def create_vm(self, name: str, config: Optional[VMConfiguration] = None) -> str:
        """Create a new VM with specified configuration"""
        try:
            if not config:
                # Use default configuration
                config = VMConfiguration(
                    name=name,
                    **self.config["vm_defaults"]
                )
            
            # Check resource limits
            if len(self.managed_vms) >= self.config["resource_limits"]["max_concurrent_vms"]:
                raise Exception("Maximum concurrent VMs limit reached")
            
            # Create VM using VirtualBox manager
            vm_uuid = self.vbox_manager.create_vm(config)
            
            # Create VMInfo object
            vm_info = VMInfo(
                vm_id=vm_uuid,
                name=name,
                state=VMState.POWERED_OFF,
                configuration=config,
                uuid=vm_uuid,
                session_id=None,
                vnc_port=self._allocate_port("vnc"),
                rdp_port=self._allocate_port("rdp"),
                ssh_port=self._allocate_port("ssh"),
                ip_address=None,
                creation_time=datetime.now(),
                last_activity=datetime.now(),
                snapshots=[],
                performance_metrics={}
            )
            
            self.managed_vms[name] = vm_info
            self.performance_metrics["total_vms_created"] += 1
            
            logger.info(f"VM '{name}' created successfully")
            return vm_uuid
            
        except Exception as e:
            logger.error(f"Failed to create VM '{name}': {e}")
            raise
    
    def _allocate_port(self, port_type: str) -> int:
        """Allocate an available port for VM services"""
        try:
            port_range = self.config["networking"][f"{port_type}_port_range"]
            
            for port in range(port_range[0], port_range[1] + 1):
                # Check if port is in use
                in_use = False
                for vm_info in self.managed_vms.values():
                    if (port_type == "vnc" and vm_info.vnc_port == port) or \
                       (port_type == "rdp" and vm_info.rdp_port == port) or \
                       (port_type == "ssh" and vm_info.ssh_port == port):
                        in_use = True
                        break
                
                if not in_use:
                    return port
            
            raise Exception(f"No available {port_type} ports")
            
        except Exception as e:
            logger.error(f"Failed to allocate {port_type} port: {e}")
            return port_range[0]  # Fallback to first port in range
    
    async def start_vm(self, vm_name: str) -> bool:
        """Start a VM and initialize services"""
        try:
            if vm_name not in self.managed_vms:
                raise Exception(f"VM '{vm_name}' not found")
            
            vm_info = self.managed_vms[vm_name]
            
            # Start VM
            if self.vbox_manager.start_vm(vm_name):
                vm_info.state = VMState.RUNNING
                vm_info.last_activity = datetime.now()
                self.performance_metrics["total_vms_running"] += 1
                
                # Initialize services
                await self._initialize_vm_services(vm_info)
                
                logger.info(f"VM '{vm_name}' started successfully")
                return True
            else:
                vm_info.state = VMState.ERROR
                return False
                
        except Exception as e:
            logger.error(f"Failed to start VM '{vm_name}': {e}")
            return False
    
    async def _initialize_vm_services(self, vm_info: VMInfo):
        """Initialize VM services (VNC, RDP, etc.)"""
        try:
            # Wait for VM to fully boot
            await asyncio.sleep(30)
            
            # Initialize screen capture
            screen_capture = VMScreenCapture(vm_info)
            if await screen_capture.connect_vnc():
                vm_info.performance_metrics["vnc_connected"] = True
            
            # Initialize remote control
            remote_control = VMRemoteControl(vm_info)
            # SSH connection will be established when needed
            
            logger.info(f"Services initialized for VM '{vm_info.name}'")
            
        except Exception as e:
            logger.error(f"Failed to initialize services for VM '{vm_info.name}': {e}")
    
    async def _process_vm_tasks(self):
        """Process VM tasks from the queue"""
        while True:
            try:
                # Get task from queue
                task = await self.pending_tasks.get()
                
                # Process task based on type
                task_id = task.get("task_id")
                task_type = task.get("task_type")
                
                logger.info(f"Processing VM task {task_id}: {task_type}")
                
                start_time = time.time()
                
                if task_type == VMTaskType.CREATE.value:
                    await self._handle_create_task(task)
                elif task_type == VMTaskType.START.value:
                    await self._handle_start_task(task)
                elif task_type == VMTaskType.STOP.value:
                    await self._handle_stop_task(task)
                elif task_type == VMTaskType.SNAPSHOT.value:
                    await self._handle_snapshot_task(task)
                elif task_type == VMTaskType.SCREEN_CAPTURE.value:
                    await self._handle_screen_capture_task(task)
                elif task_type == VMTaskType.REMOTE_COMMAND.value:
                    await self._handle_remote_command_task(task)
                else:
                    logger.warning(f"Unknown task type: {task_type}")
                
                # Update performance metrics
                task_time = time.time() - start_time
                self.performance_metrics["total_tasks_completed"] += 1
                
                current_avg = self.performance_metrics["average_task_time"]
                new_avg = (current_avg + task_time) / 2 if current_avg > 0 else task_time
                self.performance_metrics["average_task_time"] = new_avg
                
                self.pending_tasks.task_done()
                
            except Exception as e:
                logger.error(f"Error processing VM task: {e}")
                await asyncio.sleep(1)
    
    async def _handle_create_task(self, task: Dict[str, Any]):
        """Handle VM creation task"""
        try:
            vm_name = task["data"]["name"]
            config_data = task["data"].get("config", {})
            
            config = VMConfiguration(name=vm_name, **config_data)
            vm_uuid = await self.create_vm(vm_name, config)
            
            task["result"] = {"vm_uuid": vm_uuid, "status": "created"}
            
        except Exception as e:
            task["result"] = {"error": str(e), "status": "failed"}
    
    async def _handle_start_task(self, task: Dict[str, Any]):
        """Handle VM start task"""
        try:
            vm_name = task["data"]["vm_name"]
            success = await self.start_vm(vm_name)
            
            task["result"] = {"status": "started" if success else "failed"}
            
        except Exception as e:
            task["result"] = {"error": str(e), "status": "failed"}
    
    async def _handle_stop_task(self, task: Dict[str, Any]):
        """Handle VM stop task"""
        try:
            vm_name = task["data"]["vm_name"]
            force = task["data"].get("force", False)
            
            success = self.vbox_manager.stop_vm(vm_name, force)
            
            if success and vm_name in self.managed_vms:
                self.managed_vms[vm_name].state = VMState.POWERED_OFF
                self.performance_metrics["total_vms_running"] = max(0, 
                    self.performance_metrics["total_vms_running"] - 1)
            
            task["result"] = {"status": "stopped" if success else "failed"}
            
        except Exception as e:
            task["result"] = {"error": str(e), "status": "failed"}
    
    async def _handle_snapshot_task(self, task: Dict[str, Any]):
        """Handle VM snapshot task"""
        try:
            vm_name = task["data"]["vm_name"]
            snapshot_name = task["data"]["snapshot_name"]
            description = task["data"].get("description", "")
            
            success = self.vbox_manager.create_snapshot(vm_name, snapshot_name, description)
            
            if success and vm_name in self.managed_vms:
                self.managed_vms[vm_name].snapshots.append(snapshot_name)
            
            task["result"] = {"status": "snapshot_created" if success else "failed"}
            
        except Exception as e:
            task["result"] = {"error": str(e), "status": "failed"}
    
    async def _handle_screen_capture_task(self, task: Dict[str, Any]):
        """Handle VM screen capture task"""
        try:
            vm_name = task["data"]["vm_name"]
            
            if vm_name not in self.managed_vms:
                raise Exception(f"VM '{vm_name}' not found")
            
            vm_info = self.managed_vms[vm_name]
            screen_capture = VMScreenCapture(vm_info)
            
            if await screen_capture.connect_vnc():
                screenshot = await screen_capture.capture_screenshot()
                if screenshot is not None:
                    # Analyze UI elements
                    ui_elements = screen_capture.analyze_ui_elements(screenshot)
                    
                    task["result"] = {
                        "status": "captured",
                        "ui_elements": ui_elements,
                        "screenshot_shape": screenshot.shape
                    }
                else:
                    task["result"] = {"error": "Failed to capture screenshot", "status": "failed"}
            else:
                task["result"] = {"error": "Failed to connect VNC", "status": "failed"}
            
        except Exception as e:
            task["result"] = {"error": str(e), "status": "failed"}
    
    async def _handle_remote_command_task(self, task: Dict[str, Any]):
        """Handle remote command execution task"""
        try:
            vm_name = task["data"]["vm_name"]
            command = task["data"]["command"]
            username = task["data"]["username"]
            password = task["data"]["password"]
            
            if vm_name not in self.managed_vms:
                raise Exception(f"VM '{vm_name}' not found")
            
            vm_info = self.managed_vms[vm_name]
            remote_control = VMRemoteControl(vm_info)
            
            if await remote_control.connect_ssh(username, password):
                stdout, stderr, exit_code = await remote_control.execute_command(command)
                
                task["result"] = {
                    "status": "executed",
                    "stdout": stdout,
                    "stderr": stderr,
                    "exit_code": exit_code
                }
            else:
                task["result"] = {"error": "Failed to connect SSH", "status": "failed"}
            
        except Exception as e:
            task["result"] = {"error": str(e), "status": "failed"}
    
    async def _monitor_vm_health(self):
        """Monitor health of all managed VMs"""
        while True:
            try:
                for vm_name, vm_info in self.managed_vms.items():
                    # Get current VM state from VirtualBox
                    vbox_info = self.vbox_manager.get_vm_info(vm_name)
                    if vbox_info:
                        # Update VM state
                        vm_info.state = VMState(vbox_info["state"])
                        vm_info.last_activity = datetime.now()
                        
                        # Update performance metrics
                        vm_info.performance_metrics.update({
                            "memory_mb": vbox_info["memory_mb"],
                            "cpu_count": vbox_info["cpu_count"],
                            "last_health_check": datetime.now().isoformat()
                        })
                
                # Sleep until next health check
                await asyncio.sleep(self.config["automation"]["health_check_interval"])
                
            except Exception as e:
                logger.error(f"Error in VM health monitoring: {e}")
                await asyncio.sleep(60)
    
    async def _update_performance_metrics(self):
        """Update system performance metrics"""
        while True:
            try:
                # System resource usage
                self.performance_metrics["system_load"] = psutil.cpu_percent()
                self.performance_metrics["memory_usage"] = psutil.virtual_memory().percent
                self.performance_metrics["disk_usage"] = psutil.disk_usage('/').percent
                
                # VM statistics
                running_vms = sum(1 for vm in self.managed_vms.values() 
                                if vm.state == VMState.RUNNING)
                self.performance_metrics["total_vms_running"] = running_vms
                
                await asyncio.sleep(60)  # Update every minute
                
            except Exception as e:
                logger.error(f"Error updating performance metrics: {e}")
                await asyncio.sleep(60)
    
    async def _cleanup_inactive_vms(self):
        """Cleanup inactive VMs based on configuration"""
        while True:
            try:
                cleanup_hours = self.config["automation"]["auto_cleanup_hours"]
                cutoff_time = datetime.now() - timedelta(hours=cleanup_hours)
                
                vms_to_cleanup = []
                for vm_name, vm_info in self.managed_vms.items():
                    if (vm_info.state == VMState.POWERED_OFF and 
                        vm_info.last_activity < cutoff_time):
                        vms_to_cleanup.append(vm_name)
                
                for vm_name in vms_to_cleanup:
                    logger.info(f"Auto-cleaning up inactive VM: {vm_name}")
                    # Add cleanup task to queue
                    await self.add_task(VMTaskType.DELETE, {"vm_name": vm_name})
                
                # Sleep for 1 hour before next cleanup check
                await asyncio.sleep(3600)
                
            except Exception as e:
                logger.error(f"Error in VM cleanup: {e}")
                await asyncio.sleep(3600)
    
    async def add_task(self, task_type: VMTaskType, data: Dict[str, Any]) -> str:
        """Add a task to the processing queue"""
        task_id = str(uuid.uuid4())
        task = {
            "task_id": task_id,
            "task_type": task_type.value,
            "data": data,
            "created_at": datetime.now().isoformat(),
            "result": None
        }
        
        await self.pending_tasks.put(task)
        self.active_tasks[task_id] = task
        
        logger.info(f"Added VM task {task_id}: {task_type.value}")
        return task_id
    
    def get_vm_status(self, vm_name: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific VM"""
        if vm_name in self.managed_vms:
            vm_info = self.managed_vms[vm_name]
            return {
                "name": vm_info.name,
                "state": vm_info.state.value,
                "uuid": vm_info.uuid,
                "configuration": asdict(vm_info.configuration),
                "creation_time": vm_info.creation_time.isoformat(),
                "last_activity": vm_info.last_activity.isoformat(),
                "snapshots": vm_info.snapshots,
                "performance_metrics": vm_info.performance_metrics
            }
        return None
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        return {
            "total_managed_vms": len(self.managed_vms),
            "running_vms": sum(1 for vm in self.managed_vms.values() 
                             if vm.state == VMState.RUNNING),
            "pending_tasks": self.pending_tasks.qsize(),
            "active_tasks": len(self.active_tasks),
            "performance_metrics": self.performance_metrics,
            "configuration": self.config
        }

async def main():
    """Main entry point for VM Orchestrator"""
    orchestrator = VMOrchestrator()
    
    try:
        logger.info("Starting UX-MIRROR VM Orchestrator...")
        await orchestrator.initialize()
        
    except KeyboardInterrupt:
        logger.info("VM Orchestrator stopped by user")
    except Exception as e:
        logger.error(f"VM Orchestrator error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 