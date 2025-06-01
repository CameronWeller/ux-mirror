#!/usr/bin/env python3
"""
VM Orchestrator Test Suite
=========================

Comprehensive tests for the UX-MIRROR VM Orchestrator system.

Author: UX-MIRROR System
Version: 1.0.0
"""

import asyncio
import unittest
import tempfile
import shutil
import json
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, MagicMock, patch, AsyncMock

from vm_orchestrator import (
    VMOrchestrator, VMConfiguration, VMInfo, VMState, VMTaskType,
    VirtualBoxManager, VMScreenCapture, VMRemoteControl
)
from vm_template_manager import VMTemplateManager, VMTemplate


class TestVMConfiguration(unittest.TestCase):
    """Test VM configuration dataclass"""
    
    def test_default_configuration(self):
        """Test default VM configuration values"""
        config = VMConfiguration(name="test-vm")
        
        self.assertEqual(config.name, "test-vm")
        self.assertEqual(config.memory_mb, 4096)
        self.assertEqual(config.disk_size_gb, 50)
        self.assertEqual(config.cpu_cores, 2)
        self.assertEqual(config.os_type, "Windows11_64")
        self.assertTrue(config.enable_3d)
        self.assertTrue(config.enable_clipboard)
        self.assertTrue(config.rdp_enabled)
    
    def test_custom_configuration(self):
        """Test custom VM configuration"""
        config = VMConfiguration(
            name="custom-vm",
            memory_mb=8192,
            disk_size_gb=100,
            cpu_cores=4,
            os_type="Windows10_64",
            enable_3d=False
        )
        
        self.assertEqual(config.name, "custom-vm")
        self.assertEqual(config.memory_mb, 8192)
        self.assertEqual(config.disk_size_gb, 100)
        self.assertEqual(config.cpu_cores, 4)
        self.assertEqual(config.os_type, "Windows10_64")
        self.assertFalse(config.enable_3d)


class TestVirtualBoxManager(unittest.TestCase):
    """Test VirtualBox manager functionality"""
    
    @patch('vboxapi.VirtualBoxManager')
    def setUp(self, mock_vbox_manager):
        """Set up test fixtures"""
        self.mock_vbox = MagicMock()
        self.mock_vbox_manager = mock_vbox_manager
        self.mock_vbox_manager.return_value.vbox = self.mock_vbox
        
        self.vbox_manager = VirtualBoxManager()
    
    def test_initialization(self):
        """Test VirtualBox manager initialization"""
        self.assertIsNotNone(self.vbox_manager.vbox)
        self.assertIsNone(self.vbox_manager.session)
    
    @patch('vboxapi.VirtualBoxManager')
    def test_create_vm(self, mock_vbox_manager):
        """Test VM creation"""
        # Mock VM creation
        mock_vm = MagicMock()
        mock_vm.id = "test-vm-uuid"
        self.mock_vbox.createMachine.return_value = mock_vm
        
        config = VMConfiguration(name="test-vm")
        vm_id = self.vbox_manager.create_vm(config)
        
        self.assertEqual(vm_id, "test-vm-uuid")
        self.mock_vbox.createMachine.assert_called_once()
        self.mock_vbox.registerMachine.assert_called_once_with(mock_vm)
    
    def test_get_vm_info(self):
        """Test getting VM information"""
        # Mock VM
        mock_vm = MagicMock()
        mock_vm.name = "test-vm"
        mock_vm.id = "test-vm-uuid"
        mock_vm.state = 1  # Running
        mock_vm.memorySize = 4096
        mock_vm.CPUCount = 2
        mock_vm.VRAMSize = 128
        mock_vm.OSTypeId = "Windows11_64"
        mock_vm.snapshots = []
        
        self.mock_vbox.findMachine.return_value = mock_vm
        
        info = self.vbox_manager.get_vm_info("test-vm")
        
        self.assertIsNotNone(info)
        self.assertEqual(info["name"], "test-vm")
        self.assertEqual(info["uuid"], "test-vm-uuid")
        self.assertEqual(info["memory_mb"], 4096)
        self.assertEqual(info["cpu_count"], 2)


class TestVMScreenCapture(unittest.TestCase):
    """Test VM screen capture and input automation"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.vm_info = VMInfo(
            vm_id="test-vm-id",
            name="test-vm",
            state=VMState.RUNNING,
            configuration=VMConfiguration(name="test-vm"),
            uuid="test-vm-uuid",
            session_id=None,
            vnc_port=5900,
            rdp_port=3389,
            ssh_port=2222,
            ip_address="192.168.1.100",
            creation_time=datetime.now(),
            last_activity=datetime.now(),
            snapshots=[],
            performance_metrics={}
        )
        
        self.screen_capture = VMScreenCapture(self.vm_info)
    
    @patch('vncdotool.api.connect')
    async def test_connect_vnc(self, mock_vnc_connect):
        """Test VNC connection"""
        mock_vnc_client = MagicMock()
        mock_vnc_connect.return_value = mock_vnc_client
        
        result = await self.screen_capture.connect_vnc()
        
        self.assertTrue(result)
        self.assertEqual(self.screen_capture.vnc_client, mock_vnc_client)
        mock_vnc_connect.assert_called_once_with("localhost::5900")
    
    async def test_move_mouse(self):
        """Test mouse movement"""
        self.screen_capture.vnc_client = MagicMock()
        
        result = await self.screen_capture.move_mouse(100, 200)
        
        self.assertTrue(result)
        self.screen_capture.vnc_client.move.assert_called_once_with(100, 200)
    
    async def test_click(self):
        """Test mouse click"""
        self.screen_capture.vnc_client = MagicMock()
        
        result = await self.screen_capture.click(100, 200, "left")
        
        self.assertTrue(result)
        self.screen_capture.vnc_client.move.assert_called_once_with(100, 200)
        self.screen_capture.vnc_client.click.assert_called_once()
    
    async def test_type_text(self):
        """Test text typing"""
        self.screen_capture.vnc_client = MagicMock()
        
        result = await self.screen_capture.type_text("Hello World", delay=0)
        
        self.assertTrue(result)
        self.assertEqual(self.screen_capture.vnc_client.type.call_count, 11)
    
    async def test_send_key(self):
        """Test sending special keys"""
        self.screen_capture.vnc_client = MagicMock()
        
        result = await self.screen_capture.send_key("enter")
        
        self.assertTrue(result)
        self.screen_capture.vnc_client.keyPress.assert_called_once_with("Return")


class TestVMOrchestrator(unittest.TestCase):
    """Test VM Orchestrator functionality"""
    
    @patch('vm_orchestrator.VirtualBoxManager')
    def setUp(self, mock_vbox_manager):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "config" / "vm_orchestrator.json"
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.orchestrator = VMOrchestrator(str(self.config_path))
        self.orchestrator.vbox_manager = mock_vbox_manager()
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir)
    
    async def test_initialize(self):
        """Test orchestrator initialization"""
        # Mock the background tasks
        with patch.object(self.orchestrator, '_process_vm_tasks', new_callable=AsyncMock):
            with patch.object(self.orchestrator, '_monitor_vm_health', new_callable=AsyncMock):
                with patch.object(self.orchestrator, '_update_performance_metrics', new_callable=AsyncMock):
                    with patch.object(self.orchestrator, '_cleanup_inactive_vms', new_callable=AsyncMock):
                        # Initialize should not hang
                        task = asyncio.create_task(self.orchestrator.initialize())
                        await asyncio.sleep(0.1)
                        task.cancel()
                        
                        # Check that configuration was loaded
                        self.assertIsNotNone(self.orchestrator.config)
                        self.assertTrue(self.config_path.exists())
    
    async def test_create_vm(self):
        """Test VM creation through orchestrator"""
        self.orchestrator.vbox_manager.create_vm.return_value = "test-vm-uuid"
        
        config = VMConfiguration(name="test-vm")
        vm_uuid = await self.orchestrator.create_vm("test-vm", config)
        
        self.assertEqual(vm_uuid, "test-vm-uuid")
        self.assertIn("test-vm", self.orchestrator.managed_vms)
        self.assertEqual(self.orchestrator.performance_metrics["total_vms_created"], 1)
    
    async def test_add_task(self):
        """Test adding tasks to the queue"""
        task_id = await self.orchestrator.add_task(
            VMTaskType.SCREEN_CAPTURE,
            {"vm_name": "test-vm"}
        )
        
        self.assertIsNotNone(task_id)
        self.assertEqual(self.orchestrator.pending_tasks.qsize(), 1)
        self.assertIn(task_id, self.orchestrator.active_tasks)
    
    def test_get_system_status(self):
        """Test getting system status"""
        status = self.orchestrator.get_system_status()
        
        self.assertIn("total_managed_vms", status)
        self.assertIn("running_vms", status)
        self.assertIn("pending_tasks", status)
        self.assertIn("performance_metrics", status)
        self.assertIn("configuration", status)
    
    async def test_input_automation_tasks(self):
        """Test input automation task handlers"""
        # Mock VM
        vm_info = VMInfo(
            vm_id="test-vm-id",
            name="test-vm",
            state=VMState.RUNNING,
            configuration=VMConfiguration(name="test-vm"),
            uuid="test-vm-uuid",
            session_id=None,
            vnc_port=5900,
            rdp_port=3389,
            ssh_port=2222,
            ip_address=None,
            creation_time=datetime.now(),
            last_activity=datetime.now(),
            snapshots=[],
            performance_metrics={}
        )
        self.orchestrator.managed_vms["test-vm"] = vm_info
        
        # Test mouse click task
        task = {
            "task_id": "test-task-1",
            "task_type": VMTaskType.MOUSE_CLICK.value,
            "data": {
                "vm_name": "test-vm",
                "x": 100,
                "y": 200,
                "button": "left"
            }
        }
        
        with patch('vm_orchestrator.VMScreenCapture') as mock_screen_capture:
            mock_instance = mock_screen_capture.return_value
            mock_instance.connect_vnc = AsyncMock(return_value=True)
            mock_instance.click = AsyncMock(return_value=True)
            
            await self.orchestrator._handle_mouse_click_task(task)
            
            self.assertEqual(task["result"]["status"], "clicked")
            mock_instance.click.assert_called_once_with(100, 200, "left")


class TestVMTemplateManager(unittest.TestCase):
    """Test VM template management"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.template_manager = VMTemplateManager(self.temp_dir)
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir)
    
    def test_create_template(self):
        """Test template creation"""
        config = VMConfiguration(name="template-vm")
        
        template = self.template_manager.create_template(
            name="Test Template",
            description="A test template",
            base_config=config,
            tags=["test", "windows"]
        )
        
        self.assertIsNotNone(template)
        self.assertEqual(template.name, "Test Template")
        self.assertEqual(template.description, "A test template")
        self.assertIn("test", template.tags)
        
        # Check that template was saved
        template_file = Path(self.temp_dir) / f"{template.template_id}.json"
        self.assertTrue(template_file.exists())
    
    def test_list_templates(self):
        """Test listing templates"""
        # Create multiple templates
        config = VMConfiguration(name="template-vm")
        
        self.template_manager.create_template(
            name="Template 1",
            description="First template",
            base_config=config,
            tags=["windows", "development"]
        )
        
        self.template_manager.create_template(
            name="Template 2",
            description="Second template",
            base_config=config,
            tags=["windows", "testing"]
        )
        
        # List all templates
        templates = self.template_manager.list_templates()
        self.assertEqual(len(templates), 2)
        
        # List filtered templates
        dev_templates = self.template_manager.list_templates(tags=["development"])
        self.assertEqual(len(dev_templates), 1)
        self.assertEqual(dev_templates[0].name, "Template 1")
    
    def test_update_template(self):
        """Test template update"""
        config = VMConfiguration(name="template-vm")
        
        template = self.template_manager.create_template(
            name="Original Name",
            description="Original description",
            base_config=config
        )
        
        # Update template
        success = self.template_manager.update_template(
            template.template_id,
            description="Updated description",
            tags=["updated", "test"]
        )
        
        self.assertTrue(success)
        
        # Verify update
        updated_template = self.template_manager.get_template(template.template_id)
        self.assertEqual(updated_template.description, "Updated description")
        self.assertIn("updated", updated_template.tags)
    
    def test_delete_template(self):
        """Test template deletion"""
        config = VMConfiguration(name="template-vm")
        
        template = self.template_manager.create_template(
            name="To Delete",
            description="Will be deleted",
            base_config=config
        )
        
        template_id = template.template_id
        template_file = Path(self.temp_dir) / f"{template_id}.json"
        
        # Verify template exists
        self.assertTrue(template_file.exists())
        self.assertIsNotNone(self.template_manager.get_template(template_id))
        
        # Delete template
        success = self.template_manager.delete_template(template_id)
        self.assertTrue(success)
        
        # Verify deletion
        self.assertFalse(template_file.exists())
        self.assertIsNone(self.template_manager.get_template(template_id))


class TestIntegration(unittest.TestCase):
    """Integration tests for the VM orchestrator system"""
    
    @patch('vm_orchestrator.VirtualBoxManager')
    async def test_full_vm_lifecycle(self, mock_vbox_manager):
        """Test complete VM lifecycle from creation to deletion"""
        # Setup
        temp_dir = tempfile.mkdtemp()
        config_path = Path(temp_dir) / "config" / "vm_orchestrator.json"
        
        try:
            orchestrator = VMOrchestrator(str(config_path))
            orchestrator.vbox_manager = mock_vbox_manager()
            orchestrator.vbox_manager.create_vm.return_value = "test-vm-uuid"
            orchestrator.vbox_manager.start_vm.return_value = True
            orchestrator.vbox_manager.stop_vm.return_value = True
            
            # Create VM
            config = VMConfiguration(name="lifecycle-vm", memory_mb=8192)
            vm_uuid = await orchestrator.create_vm("lifecycle-vm", config)
            self.assertEqual(vm_uuid, "test-vm-uuid")
            
            # Start VM
            success = await orchestrator.start_vm("lifecycle-vm")
            self.assertTrue(success)
            
            # Add automation task
            task_id = await orchestrator.add_task(
                VMTaskType.AUTOMATE_SEQUENCE,
                {
                    "vm_name": "lifecycle-vm",
                    "sequence": [
                        {"type": "click", "x": 100, "y": 100, "button": "left"},
                        {"type": "type_text", "text": "Hello VM", "delay": 0.1},
                        {"type": "send_key", "key": "enter"}
                    ]
                }
            )
            self.assertIsNotNone(task_id)
            
            # Get VM status
            status = orchestrator.get_vm_status("lifecycle-vm")
            self.assertIsNotNone(status)
            self.assertEqual(status["name"], "lifecycle-vm")
            self.assertEqual(status["state"], VMState.RUNNING.value)
            
        finally:
            shutil.rmtree(temp_dir)


def run_async_test(coro):
    """Helper to run async tests"""
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coro)


if __name__ == "__main__":
    unittest.main() 