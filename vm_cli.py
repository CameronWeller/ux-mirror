#!/usr/bin/env python3
"""
UX-MIRROR VM CLI
===============

Command-line interface for managing VMs in the UX-MIRROR system.

Usage:
    python vm_cli.py create --name test-vm --memory 4096 --disk 50
    python vm_cli.py start --name test-vm
    python vm_cli.py stop --name test-vm
    python vm_cli.py status --name test-vm
    python vm_cli.py list
    python vm_cli.py screenshot --name test-vm
    python vm_cli.py exec --name test-vm --command "dir"

Author: UX-MIRROR System
Version: 1.0.0
"""

import asyncio
import argparse
import json
import sys
import time
from datetime import datetime
from typing import Dict, Any

from vm_orchestrator import VMOrchestrator, VMConfiguration, VMTaskType

class VMCLI:
    """Command-line interface for VM management"""
    
    def __init__(self):
        self.orchestrator = VMOrchestrator()
        
    async def initialize(self):
        """Initialize the CLI and orchestrator"""
        print("🚀 Initializing UX-MIRROR VM CLI...")
        await self.orchestrator._load_configuration()
        await self.orchestrator._discover_existing_vms()
        print("✅ VM CLI ready")
    
    async def create_vm(self, args):
        """Create a new VM"""
        try:
            print(f"🔨 Creating VM '{args.name}'...")
            
            config = VMConfiguration(
                name=args.name,
                memory_mb=args.memory,
                disk_size_gb=args.disk,
                cpu_cores=args.cpu_cores,
                os_type=args.os_type
            )
            
            vm_uuid = await self.orchestrator.create_vm(args.name, config)
            
            print(f"✅ VM '{args.name}' created successfully!")
            print(f"   UUID: {vm_uuid}")
            print(f"   Memory: {args.memory} MB")
            print(f"   Disk: {args.disk} GB")
            print(f"   CPU Cores: {args.cpu_cores}")
            
        except Exception as e:
            print(f"❌ Failed to create VM '{args.name}': {e}")
            sys.exit(1)
    
    async def start_vm(self, args):
        """Start a VM"""
        try:
            print(f"▶️  Starting VM '{args.name}'...")
            
            # Add start task
            task_id = await self.orchestrator.add_task(
                VMTaskType.START, 
                {"vm_name": args.name}
            )
            
            # Wait for task completion
            await self._wait_for_task_completion(task_id)
            
            print(f"✅ VM '{args.name}' started successfully!")
            print("🔗 Services available:")
            
            vm_status = self.orchestrator.get_vm_status(args.name)
            if vm_status:
                vm_info = self.orchestrator.managed_vms[args.name]
                if vm_info.vnc_port:
                    print(f"   VNC: localhost:{vm_info.vnc_port}")
                if vm_info.rdp_port:
                    print(f"   RDP: localhost:{vm_info.rdp_port}")
                if vm_info.ssh_port:
                    print(f"   SSH: localhost:{vm_info.ssh_port}")
            
        except Exception as e:
            print(f"❌ Failed to start VM '{args.name}': {e}")
            sys.exit(1)
    
    async def stop_vm(self, args):
        """Stop a VM"""
        try:
            print(f"⏹️  Stopping VM '{args.name}'...")
            
            # Add stop task
            task_id = await self.orchestrator.add_task(
                VMTaskType.STOP, 
                {"vm_name": args.name, "force": args.force}
            )
            
            # Wait for task completion
            await self._wait_for_task_completion(task_id)
            
            print(f"✅ VM '{args.name}' stopped successfully!")
            
        except Exception as e:
            print(f"❌ Failed to stop VM '{args.name}': {e}")
            sys.exit(1)
    
    async def vm_status(self, args):
        """Show VM status"""
        try:
            status = self.orchestrator.get_vm_status(args.name)
            
            if not status:
                print(f"❌ VM '{args.name}' not found")
                sys.exit(1)
            
            print(f"📊 Status for VM '{args.name}':")
            print(f"   State: {status['state']}")
            print(f"   UUID: {status['uuid']}")
            print(f"   Created: {status['creation_time']}")
            print(f"   Last Activity: {status['last_activity']}")
            
            config = status['configuration']
            print(f"   Configuration:")
            print(f"     Memory: {config['memory_mb']} MB")
            print(f"     Disk: {config['disk_size_gb']} GB")
            print(f"     CPU Cores: {config['cpu_cores']}")
            print(f"     OS Type: {config['os_type']}")
            
            if status['snapshots']:
                print(f"   Snapshots: {', '.join(status['snapshots'])}")
            
            if status['performance_metrics']:
                print(f"   Performance Metrics:")
                for key, value in status['performance_metrics'].items():
                    print(f"     {key}: {value}")
            
        except Exception as e:
            print(f"❌ Failed to get VM status: {e}")
            sys.exit(1)
    
    async def list_vms(self, args):
        """List all VMs"""
        try:
            system_status = self.orchestrator.get_system_status()
            
            print("📋 VM List:")
            print(f"   Total VMs: {system_status['total_managed_vms']}")
            print(f"   Running VMs: {system_status['running_vms']}")
            print("")
            
            if not self.orchestrator.managed_vms:
                print("   No VMs found")
                return
            
            print("   VM Name               State           Memory    CPU   Created")
            print("   " + "-" * 70)
            
            for vm_name, vm_info in self.orchestrator.managed_vms.items():
                created_date = vm_info.creation_time.strftime("%Y-%m-%d")
                print(f"   {vm_name:<20} {vm_info.state.value:<15} "
                      f"{vm_info.configuration.memory_mb:<8} "
                      f"{vm_info.configuration.cpu_cores:<5} {created_date}")
            
        except Exception as e:
            print(f"❌ Failed to list VMs: {e}")
            sys.exit(1)
    
    async def create_snapshot(self, args):
        """Create a VM snapshot"""
        try:
            print(f"📸 Creating snapshot '{args.snapshot_name}' for VM '{args.name}'...")
            
            # Add snapshot task
            task_id = await self.orchestrator.add_task(
                VMTaskType.SNAPSHOT, 
                {
                    "vm_name": args.name,
                    "snapshot_name": args.snapshot_name,
                    "description": args.description
                }
            )
            
            # Wait for task completion
            await self._wait_for_task_completion(task_id)
            
            print(f"✅ Snapshot '{args.snapshot_name}' created successfully!")
            
        except Exception as e:
            print(f"❌ Failed to create snapshot: {e}")
            sys.exit(1)
    
    async def take_screenshot(self, args):
        """Take a screenshot of VM"""
        try:
            print(f"📷 Taking screenshot of VM '{args.name}'...")
            
            # Add screen capture task
            task_id = await self.orchestrator.add_task(
                VMTaskType.SCREEN_CAPTURE, 
                {"vm_name": args.name}
            )
            
            # Wait for task completion
            result = await self._wait_for_task_completion(task_id, return_result=True)
            
            if result and result.get("status") == "captured":
                ui_elements = result.get("ui_elements", [])
                screenshot_shape = result.get("screenshot_shape")
                
                print(f"✅ Screenshot captured successfully!")
                print(f"   Resolution: {screenshot_shape[1]}x{screenshot_shape[0]}")
                print(f"   UI Elements Detected: {len(ui_elements)}")
                
                if args.analyze and ui_elements:
                    print("🔍 Detected UI Elements:")
                    for i, element in enumerate(ui_elements[:10]):  # Show first 10
                        bounds = element["bounds"]
                        print(f"   {i+1}. {element['type']} at ({bounds['x']}, {bounds['y']}) "
                              f"size {bounds['width']}x{bounds['height']}")
            else:
                print(f"❌ Failed to capture screenshot: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Failed to take screenshot: {e}")
            sys.exit(1)
    
    async def execute_command(self, args):
        """Execute command in VM"""
        try:
            print(f"⚡ Executing command in VM '{args.name}': {args.command}")
            
            # Add remote command task
            task_id = await self.orchestrator.add_task(
                VMTaskType.REMOTE_COMMAND, 
                {
                    "vm_name": args.name,
                    "command": args.command,
                    "username": args.username,
                    "password": args.password
                }
            )
            
            # Wait for task completion
            result = await self._wait_for_task_completion(task_id, return_result=True)
            
            if result and result.get("status") == "executed":
                stdout = result.get("stdout", "")
                stderr = result.get("stderr", "")
                exit_code = result.get("exit_code", 0)
                
                print(f"✅ Command executed (exit code: {exit_code})")
                
                if stdout:
                    print("📤 Output:")
                    print(stdout)
                
                if stderr:
                    print("⚠️  Errors:")
                    print(stderr)
            else:
                print(f"❌ Failed to execute command: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Failed to execute command: {e}")
            sys.exit(1)
    
    async def system_status(self, args):
        """Show system status"""
        try:
            status = self.orchestrator.get_system_status()
            
            print("🖥️  UX-MIRROR VM System Status:")
            print(f"   Total Managed VMs: {status['total_managed_vms']}")
            print(f"   Running VMs: {status['running_vms']}")
            print(f"   Pending Tasks: {status['pending_tasks']}")
            print(f"   Active Tasks: {status['active_tasks']}")
            
            metrics = status['performance_metrics']
            print(f"   Performance Metrics:")
            print(f"     Total VMs Created: {metrics['total_vms_created']}")
            print(f"     Total Tasks Completed: {metrics['total_tasks_completed']}")
            print(f"     Average Task Time: {metrics['average_task_time']:.2f}s")
            print(f"     System Load: {metrics['system_load']:.1f}%")
            
            if 'memory_usage' in metrics:
                print(f"     Memory Usage: {metrics['memory_usage']:.1f}%")
            if 'disk_usage' in metrics:
                print(f"     Disk Usage: {metrics['disk_usage']:.1f}%")
            
        except Exception as e:
            print(f"❌ Failed to get system status: {e}")
            sys.exit(1)
    
    async def _wait_for_task_completion(self, task_id: str, timeout: int = 300, return_result: bool = False):
        """Wait for a task to complete"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if task_id in self.orchestrator.active_tasks:
                task = self.orchestrator.active_tasks[task_id]
                if task.get("result") is not None:
                    result = task["result"]
                    if return_result:
                        return result
                    return
            
            print(".", end="", flush=True)
            await asyncio.sleep(1)
        
        print("")
        raise Exception(f"Task {task_id} timed out after {timeout} seconds")

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="UX-MIRROR VM Management CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Create a VM:     python vm_cli.py create --name test-vm --memory 4096 --disk 50
  Start a VM:      python vm_cli.py start --name test-vm
  Stop a VM:       python vm_cli.py stop --name test-vm
  List VMs:        python vm_cli.py list
  VM Status:       python vm_cli.py status --name test-vm
  Take Screenshot: python vm_cli.py screenshot --name test-vm --analyze
  Execute Command: python vm_cli.py exec --name test-vm --command "dir" --username admin --password pass
  System Status:   python vm_cli.py system-status
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Create VM command
    create_parser = subparsers.add_parser('create', help='Create a new VM')
    create_parser.add_argument('--name', required=True, help='VM name')
    create_parser.add_argument('--memory', type=int, default=4096, help='Memory in MB (default: 4096)')
    create_parser.add_argument('--disk', type=int, default=50, help='Disk size in GB (default: 50)')
    create_parser.add_argument('--cpu-cores', type=int, default=2, help='Number of CPU cores (default: 2)')
    create_parser.add_argument('--os-type', default='Windows11_64', help='OS type (default: Windows11_64)')
    
    # Start VM command
    start_parser = subparsers.add_parser('start', help='Start a VM')
    start_parser.add_argument('--name', required=True, help='VM name')
    
    # Stop VM command
    stop_parser = subparsers.add_parser('stop', help='Stop a VM')
    stop_parser.add_argument('--name', required=True, help='VM name')
    stop_parser.add_argument('--force', action='store_true', help='Force stop (power off)')
    
    # VM status command
    status_parser = subparsers.add_parser('status', help='Show VM status')
    status_parser.add_argument('--name', required=True, help='VM name')
    
    # List VMs command
    list_parser = subparsers.add_parser('list', help='List all VMs')
    
    # Create snapshot command
    snapshot_parser = subparsers.add_parser('snapshot', help='Create a VM snapshot')
    snapshot_parser.add_argument('--name', required=True, help='VM name')
    snapshot_parser.add_argument('--snapshot-name', required=True, help='Snapshot name')
    snapshot_parser.add_argument('--description', default='', help='Snapshot description')
    
    # Screenshot command
    screenshot_parser = subparsers.add_parser('screenshot', help='Take VM screenshot')
    screenshot_parser.add_argument('--name', required=True, help='VM name')
    screenshot_parser.add_argument('--analyze', action='store_true', help='Analyze UI elements')
    
    # Execute command
    exec_parser = subparsers.add_parser('exec', help='Execute command in VM')
    exec_parser.add_argument('--name', required=True, help='VM name')
    exec_parser.add_argument('--command', required=True, help='Command to execute')
    exec_parser.add_argument('--username', required=True, help='SSH username')
    exec_parser.add_argument('--password', required=True, help='SSH password')
    
    # System status command
    system_parser = subparsers.add_parser('system-status', help='Show system status')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Run the appropriate command
    cli = VMCLI()
    
    async def run_command():
        await cli.initialize()
        
        if args.command == 'create':
            await cli.create_vm(args)
        elif args.command == 'start':
            await cli.start_vm(args)
        elif args.command == 'stop':
            await cli.stop_vm(args)
        elif args.command == 'status':
            await cli.vm_status(args)
        elif args.command == 'list':
            await cli.list_vms(args)
        elif args.command == 'snapshot':
            await cli.create_snapshot(args)
        elif args.command == 'screenshot':
            await cli.take_screenshot(args)
        elif args.command == 'exec':
            await cli.execute_command(args)
        elif args.command == 'system-status':
            await cli.system_status(args)
        else:
            print(f"❌ Unknown command: {args.command}")
            parser.print_help()
            sys.exit(1)
    
    try:
        asyncio.run(run_command())
    except KeyboardInterrupt:
        print("\n🛑 Operation cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 