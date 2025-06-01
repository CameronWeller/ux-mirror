#!/usr/bin/env python3
"""
Example VM Automation Script
===========================

Demonstrates the enhanced VM orchestrator capabilities including
input automation and template management.

Author: UX-MIRROR System
"""

import asyncio
import json
from pathlib import Path

from vm_orchestrator import VMOrchestrator, VMConfiguration, VMTaskType
from vm_template_manager import VMTemplateManager


async def example_basic_vm_operations():
    """Example: Basic VM creation and management"""
    print("\n=== Basic VM Operations Example ===")
    
    orchestrator = VMOrchestrator()
    await orchestrator.initialize()
    
    # Create a VM
    config = VMConfiguration(
        name="demo-vm",
        memory_mb=4096,
        disk_size_gb=50,
        cpu_cores=2
    )
    
    print("Creating VM...")
    vm_uuid = await orchestrator.create_vm("demo-vm", config)
    print(f"VM Created: {vm_uuid}")
    
    # Start the VM
    print("Starting VM...")
    success = await orchestrator.start_vm("demo-vm")
    print(f"VM Started: {success}")
    
    # Get VM status
    status = orchestrator.get_vm_status("demo-vm")
    print(f"VM Status: {status['state']}")
    
    return orchestrator


async def example_input_automation(orchestrator: VMOrchestrator):
    """Example: VM input automation"""
    print("\n=== Input Automation Example ===")
    
    # Click at coordinates
    print("Clicking at (100, 100)...")
    task_id = await orchestrator.add_task(
        VMTaskType.MOUSE_CLICK,
        {
            "vm_name": "demo-vm",
            "x": 100,
            "y": 100,
            "button": "left"
        }
    )
    print(f"Click task created: {task_id}")
    
    # Type text
    print("Typing text...")
    task_id = await orchestrator.add_task(
        VMTaskType.TYPE_TEXT,
        {
            "vm_name": "demo-vm",
            "text": "Hello from VM Orchestrator!",
            "delay": 0.05
        }
    )
    print(f"Type text task created: {task_id}")
    
    # Send key
    print("Sending Enter key...")
    task_id = await orchestrator.add_task(
        VMTaskType.SEND_KEY,
        {
            "vm_name": "demo-vm",
            "key": "enter"
        }
    )
    print(f"Send key task created: {task_id}")


async def example_automation_sequence(orchestrator: VMOrchestrator):
    """Example: Running an automation sequence"""
    print("\n=== Automation Sequence Example ===")
    
    # Define a simple automation sequence
    sequence = [
        {
            "type": "click",
            "x": 50,
            "y": 1050,
            "button": "left",
            "comment": "Click Start button"
        },
        {
            "type": "delay",
            "seconds": 1
        },
        {
            "type": "type_text",
            "text": "notepad",
            "delay": 0.1
        },
        {
            "type": "send_key",
            "key": "enter"
        }
    ]
    
    print("Running automation sequence...")
    task_id = await orchestrator.add_task(
        VMTaskType.AUTOMATE_SEQUENCE,
        {
            "vm_name": "demo-vm",
            "sequence": sequence
        }
    )
    print(f"Automation sequence task created: {task_id}")


def example_template_management():
    """Example: VM template management"""
    print("\n=== Template Management Example ===")
    
    manager = VMTemplateManager()
    
    # Create a template
    config = VMConfiguration(
        name="template_base",
        memory_mb=8192,
        disk_size_gb=100,
        cpu_cores=4,
        os_type="Windows11_64"
    )
    
    print("Creating template...")
    template = manager.create_template(
        name="Development Template",
        description="Template for development VMs with enhanced resources",
        base_config=config,
        applications=["VS Code", "Git", "Python"],
        tags=["development", "windows", "ide"]
    )
    print(f"Template created: {template.name} (ID: {template.template_id})")
    
    # List templates
    print("\nAvailable templates:")
    templates = manager.list_templates()
    for tmpl in templates:
        print(f"  - {tmpl.name}: {tmpl.description}")
    
    return manager, template


async def example_deploy_from_template(manager: VMTemplateManager, 
                                     template, 
                                     orchestrator: VMOrchestrator):
    """Example: Deploy VM from template"""
    print("\n=== Deploy from Template Example ===")
    
    print(f"Deploying VM from template '{template.name}'...")
    vm_uuid = await manager.deploy_from_template(
        template.template_id,
        "dev-vm-from-template",
        orchestrator,
        custom_config={"memory_mb": 16384}  # Override memory
    )
    print(f"VM deployed: {vm_uuid}")


async def example_ocr_click(orchestrator: VMOrchestrator):
    """Example: Find and click element by text"""
    print("\n=== OCR-based Click Example ===")
    
    print("Finding and clicking 'Start' button...")
    task_id = await orchestrator.add_task(
        VMTaskType.FIND_AND_CLICK,
        {
            "vm_name": "demo-vm",
            "text": "Start"
        }
    )
    print(f"Find and click task created: {task_id}")


async def main():
    """Run all examples"""
    print("UX-MIRROR VM Orchestrator - Example Script")
    print("=" * 50)
    
    try:
        # Note: These examples assume VirtualBox is installed and configured
        # In a real environment, you would need actual VMs running
        
        # Basic operations
        orchestrator = await example_basic_vm_operations()
        
        # Wait a bit for VM to start (in real scenario)
        await asyncio.sleep(5)
        
        # Input automation
        await example_input_automation(orchestrator)
        
        # Automation sequence
        await example_automation_sequence(orchestrator)
        
        # Template management
        manager, template = example_template_management()
        
        # Deploy from template
        await example_deploy_from_template(manager, template, orchestrator)
        
        # OCR-based clicking
        await example_ocr_click(orchestrator)
        
        # Get system status
        print("\n=== System Status ===")
        status = orchestrator.get_system_status()
        print(f"Total VMs: {status['total_managed_vms']}")
        print(f"Running VMs: {status['running_vms']}")
        print(f"Pending tasks: {status['pending_tasks']}")
        
    except Exception as e:
        print(f"\nError: {e}")
        print("\nNote: This example requires VirtualBox to be installed and configured.")
        print("Some operations may fail in a test environment without actual VMs.")
    
    print("\n" + "=" * 50)
    print("Example completed!")


if __name__ == "__main__":
    # Run the examples
    asyncio.run(main()) 