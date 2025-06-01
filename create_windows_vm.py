#!/usr/bin/env python3
"""
UX-MIRROR Windows VM Creator
===========================

Specialized script for creating and configuring Windows VMs optimized
for the UX-MIRROR system with automated setup and configuration.

Author: UX-MIRROR System
Version: 1.0.0
"""

import asyncio
import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional

from vm_orchestrator import VMOrchestrator, VMConfiguration, VMTaskType

class WindowsVMCreator:
    """Creates and configures Windows VMs for UX-MIRROR"""
    
    def __init__(self):
        self.orchestrator = VMOrchestrator()
        
    async def initialize(self):
        """Initialize the VM creator"""
        print("🔧 Initializing Windows VM Creator...")
        await self.orchestrator._load_configuration()
        await self.orchestrator._discover_existing_vms()
        print("✅ VM Creator ready")
    
    async def create_windows_vm(self, args) -> str:
        """Create a new Windows VM with optimized settings"""
        
        vm_name = args.name
        print(f"🔨 Creating Windows VM: {vm_name}")
        
        # Windows-optimized configuration
        config = VMConfiguration(
            name=vm_name,
            memory_mb=args.memory,
            disk_size_gb=args.disk,
            cpu_cores=args.cpu_cores,
            os_type=self._get_windows_os_type(args.windows_version),
            network_adapter="NAT",
            enable_3d=True,
            enable_clipboard=True,
            rdp_enabled=True,
            rdp_port=self._get_available_port("rdp")
        )
        
        print(f"   OS Type: {config.os_type}")
        print(f"   Memory: {config.memory_mb} MB")
        print(f"   Disk: {config.disk_size_gb} GB")
        print(f"   CPU Cores: {config.cpu_cores}")
        print(f"   RDP Port: {config.rdp_port}")
        
        # Create the VM
        try:
            vm_uuid = await self.orchestrator.create_vm(vm_name, config)
            print(f"✅ VM '{vm_name}' created successfully")
            print(f"   UUID: {vm_uuid}")
            
            # Configure additional Windows-specific settings
            await self._configure_windows_settings(vm_name, args)
            
            # Attach Windows ISO if provided
            if args.iso_path:
                await self._attach_windows_iso(vm_name, args.iso_path)
            
            return vm_uuid
            
        except Exception as e:
            print(f"❌ Failed to create VM: {e}")
            raise
    
    def _get_windows_os_type(self, version: str) -> str:
        """Get VirtualBox OS type for Windows version"""
        os_types = {
            "11": "Windows11_64",
            "10": "Windows10_64",
            "2022": "Windows2022_64",
            "2019": "Windows2019_64",
            "2016": "Windows2016_64"
        }
        
        return os_types.get(version, "Windows11_64")
    
    def _get_available_port(self, port_type: str) -> int:
        """Get an available port for VM services"""
        config = self.orchestrator.config
        port_range = config["networking"][f"{port_type}_port_range"]
        
        for port in range(port_range[0], port_range[1] + 1):
            # Check if port is in use
            in_use = False
            for vm_info in self.orchestrator.managed_vms.values():
                if getattr(vm_info, f"{port_type}_port") == port:
                    in_use = True
                    break
            
            if not in_use:
                return port
        
        return port_range[0]  # Fallback
    
    async def _configure_windows_settings(self, vm_name: str, args):
        """Configure Windows-specific VM settings"""
        print("🔧 Configuring Windows-specific settings...")
        
        try:
            # Enable features for Windows automation
            vbox_settings = [
                # Hardware acceleration
                ("--hwvirtex", "on"),
                ("--nestedpaging", "on"),
                ("--vtxvpid", "on"),
                ("--vtxux", "on"),
                
                # Graphics
                ("--graphicscontroller", "vmsvga"),
                ("--vram", "128"),
                ("--accelerate3d", "on" if args.enable_3d else "off"),
                
                # Audio (for complete Windows experience)
                ("--audio", "dsound" if os.name == "nt" else "pulse"),
                ("--audiocontroller", "hda"),
                
                # USB
                ("--usbehci", "on"),
                ("--usbxhci", "on"),
                
                # Network
                ("--nic1", "nat"),
                ("--natpf1", f"rdp,tcp,,{self._get_available_port('rdp')},,3389"),
                
                # Boot order
                ("--boot1", "dvd"),
                ("--boot2", "disk"),
                ("--boot3", "none"),
                ("--boot4", "none"),
                
                # Performance
                ("--ioapic", "on"),
                ("--rtcuseutc", "on"),
                ("--biosbootmenu", "disabled")
            ]
            
            # Apply VirtualBox settings
            import subprocess
            for setting, value in vbox_settings:
                try:
                    result = subprocess.run(
                        ["VBoxManage", "modifyvm", vm_name, setting, value],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    
                    if result.returncode != 0:
                        print(f"   ⚠️  Warning: Failed to set {setting}: {result.stderr}")
                
                except subprocess.TimeoutExpired:
                    print(f"   ⚠️  Warning: Timeout setting {setting}")
                
            print("   ✅ Windows settings configured")
            
        except Exception as e:
            print(f"   ⚠️  Warning: Some Windows settings failed: {e}")
    
    async def _attach_windows_iso(self, vm_name: str, iso_path: str):
        """Attach Windows ISO to VM"""
        print(f"💿 Attaching Windows ISO: {iso_path}")
        
        if not os.path.exists(iso_path):
            print(f"   ❌ ISO file not found: {iso_path}")
            return
        
        try:
            import subprocess
            
            # Attach ISO to IDE controller
            result = subprocess.run([
                "VBoxManage", "storageattach", vm_name,
                "--storagectl", "IDE Controller",
                "--port", "0",
                "--device", "0", 
                "--type", "dvddrive",
                "--medium", iso_path
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("   ✅ Windows ISO attached successfully")
            else:
                print(f"   ❌ Failed to attach ISO: {result.stderr}")
                
        except Exception as e:
            print(f"   ❌ Error attaching ISO: {e}")
    
    async def start_and_setup_vm(self, vm_name: str, args):
        """Start VM and perform initial setup"""
        print(f"▶️  Starting Windows VM: {vm_name}")
        
        try:
            # Start the VM
            success = await self.orchestrator.start_vm(vm_name)
            
            if not success:
                print(f"❌ Failed to start VM: {vm_name}")
                return False
            
            print(f"✅ VM '{vm_name}' started successfully")
            
            # Display connection information
            await self._display_connection_info(vm_name)
            
            # Wait for Windows installation if ISO was attached
            if args.iso_path:
                await self._guide_windows_installation(vm_name, args)
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to start VM: {e}")
            return False
    
    async def _display_connection_info(self, vm_name: str):
        """Display VM connection information"""
        vm_info = self.orchestrator.managed_vms.get(vm_name)
        
        if vm_info:
            print("🔗 VM Connection Information:")
            
            if vm_info.rdp_port:
                print(f"   RDP: localhost:{vm_info.rdp_port}")
                print("   Use Remote Desktop to connect")
            
            if vm_info.vnc_port:
                print(f"   VNC: localhost:{vm_info.vnc_port}")
                print("   Use VNC viewer to connect")
            
            print("\n📋 Next Steps:")
            print("1. Connect via RDP or VNC")
            print("2. Install Windows (if using ISO)")
            print("3. Enable SSH server for automation")
            print("4. Install automation tools")
    
    async def _guide_windows_installation(self, vm_name: str, args):
        """Guide user through Windows installation"""
        print("\n🚀 Windows Installation Guide:")
        print("=" * 50)
        print("1. Connect to the VM via RDP or VNC")
        print("2. Follow Windows installation wizard")
        print("3. Recommended settings for UX-MIRROR:")
        print("   - Enable Remote Desktop")
        print("   - Install OpenSSH Server")
        print("   - Disable Windows Defender (for automation)")
        print("   - Set power plan to 'Never sleep'")
        print("   - Install automation-friendly software")
        print("4. Create automation user account:")
        print("   - Username: uxmirror")
        print("   - Enable auto-login")
        print("   - Add to Administrators group")
        print("=" * 50)
        
        if args.wait_for_installation:
            print("\n⏳ Waiting for Windows installation...")
            print("Press Ctrl+C when installation is complete")
            
            try:
                while True:
                    await asyncio.sleep(30)
                    print(".", end="", flush=True)
                    
            except KeyboardInterrupt:
                print("\n✅ Windows installation completed!")
                await self._post_installation_setup(vm_name, args)
    
    async def _post_installation_setup(self, vm_name: str, args):
        """Perform post-installation setup"""
        print("\n🔧 Post-Installation Setup:")
        
        # Create snapshot after installation
        snapshot_name = f"windows-{args.windows_version}-clean"
        print(f"📸 Creating clean installation snapshot: {snapshot_name}")
        
        task_id = await self.orchestrator.add_task(
            VMTaskType.SNAPSHOT,
            {
                "vm_name": vm_name,
                "snapshot_name": snapshot_name,
                "description": "Clean Windows installation"
            }
        )
        
        # Wait for snapshot completion
        await self._wait_for_task(task_id)
        print("✅ Clean installation snapshot created")
        
        # Display automation setup instructions
        print("\n🤖 Automation Setup:")
        print("To enable full UX-MIRROR automation:")
        print("1. Test SSH connection:")
        print(f"   python vm_cli.py exec --name {vm_name} --command 'echo test' --username uxmirror --password yourpassword")
        print("2. Install automation tools:")
        print("   - Python 3.11+")
        print("   - Browser automation drivers")
        print("   - Screen capture tools")
        print("3. Configure for headless operation")
    
    async def _wait_for_task(self, task_id: str, timeout: int = 300):
        """Wait for a task to complete"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if task_id in self.orchestrator.active_tasks:
                task = self.orchestrator.active_tasks[task_id]
                if task.get("result") is not None:
                    return
            
            await asyncio.sleep(1)
        
        raise Exception(f"Task {task_id} timed out")

async def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Create Windows VMs optimized for UX-MIRROR",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Create Windows 11 VM:
    python create_windows_vm.py --name win11-test --windows-version 11 --memory 8192 --disk 100

  Create with Windows ISO:
    python create_windows_vm.py --name win11-auto --iso-path ./iso/Windows11.iso --auto-start

  Create Server 2022:
    python create_windows_vm.py --name server2022 --windows-version 2022 --memory 16384 --cpu-cores 4
        """
    )
    
    parser.add_argument("--name", required=True, help="VM name")
    parser.add_argument("--windows-version", choices=["11", "10", "2022", "2019", "2016"], 
                       default="11", help="Windows version (default: 11)")
    parser.add_argument("--memory", type=int, default=8192, 
                       help="Memory in MB (default: 8192)")
    parser.add_argument("--disk", type=int, default=100, 
                       help="Disk size in GB (default: 100)")
    parser.add_argument("--cpu-cores", type=int, default=4, 
                       help="Number of CPU cores (default: 4)")
    parser.add_argument("--iso-path", help="Path to Windows ISO file")
    parser.add_argument("--auto-start", action="store_true", 
                       help="Automatically start VM after creation")
    parser.add_argument("--enable-3d", action="store_true", default=True,
                       help="Enable 3D acceleration (default: enabled)")
    parser.add_argument("--wait-for-installation", action="store_true",
                       help="Wait for manual Windows installation")
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.memory < 4096:
        print("❌ Error: Windows VMs require at least 4GB RAM")
        sys.exit(1)
    
    if args.disk < 50:
        print("❌ Error: Windows VMs require at least 50GB disk space")
        sys.exit(1)
    
    if args.iso_path and not os.path.exists(args.iso_path):
        print(f"❌ Error: ISO file not found: {args.iso_path}")
        sys.exit(1)
    
    # Create and configure VM
    creator = WindowsVMCreator()
    
    try:
        await creator.initialize()
        
        # Create VM
        vm_uuid = await creator.create_windows_vm(args)
        
        # Start VM if requested
        if args.auto_start:
            await creator.start_and_setup_vm(args.name, args)
        else:
            print(f"\n✅ Windows VM '{args.name}' created successfully!")
            print(f"To start the VM, run:")
            print(f"   python vm_cli.py start --name {args.name}")
            print(f"Or:")
            print(f"   python create_windows_vm.py --name {args.name} --auto-start")
        
    except KeyboardInterrupt:
        print("\n🛑 Operation cancelled by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 