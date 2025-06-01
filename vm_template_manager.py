#!/usr/bin/env python3
"""
VM Template Manager
==================

Manages VM templates for quick deployment of pre-configured virtual machines.
Supports saving VM states, configurations, and automated setup scripts.

Author: UX-MIRROR System
Version: 1.0.0
"""

import json
import os
import shutil
import logging
import hashlib
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

from vm_orchestrator import VMConfiguration, VMOrchestrator, VMTaskType

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class VMTemplate:
    """VM template definition"""
    template_id: str
    name: str
    description: str
    base_config: VMConfiguration
    post_install_scripts: List[Dict[str, Any]]
    applications: List[str]
    settings: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    tags: List[str]
    version: str = "1.0"
    

class VMTemplateManager:
    """Manages VM templates for quick deployment"""
    
    def __init__(self, template_dir: str = "vm_templates"):
        self.template_dir = Path(template_dir)
        self.template_dir.mkdir(exist_ok=True)
        self.templates: Dict[str, VMTemplate] = {}
        self._load_templates()
        
    def _load_templates(self):
        """Load all templates from disk"""
        try:
            for template_file in self.template_dir.glob("*.json"):
                with open(template_file, 'r') as f:
                    data = json.load(f)
                    
                    # Convert config dict back to VMConfiguration
                    config_data = data['base_config']
                    config = VMConfiguration(**config_data)
                    
                    # Create template object
                    template = VMTemplate(
                        template_id=data['template_id'],
                        name=data['name'],
                        description=data['description'],
                        base_config=config,
                        post_install_scripts=data['post_install_scripts'],
                        applications=data['applications'],
                        settings=data['settings'],
                        created_at=datetime.fromisoformat(data['created_at']),
                        updated_at=datetime.fromisoformat(data['updated_at']),
                        tags=data['tags'],
                        version=data.get('version', '1.0')
                    )
                    
                    self.templates[template.template_id] = template
                    
            logger.info(f"Loaded {len(self.templates)} VM templates")
            
        except Exception as e:
            logger.error(f"Error loading templates: {e}")
    
    def create_template(self, name: str, description: str, 
                       base_config: VMConfiguration,
                       post_install_scripts: Optional[List[Dict[str, Any]]] = None,
                       applications: Optional[List[str]] = None,
                       settings: Optional[Dict[str, Any]] = None,
                       tags: Optional[List[str]] = None) -> VMTemplate:
        """Create a new VM template"""
        try:
            # Generate template ID
            template_id = hashlib.md5(f"{name}{datetime.now()}".encode()).hexdigest()[:12]
            
            template = VMTemplate(
                template_id=template_id,
                name=name,
                description=description,
                base_config=base_config,
                post_install_scripts=post_install_scripts or [],
                applications=applications or [],
                settings=settings or {},
                created_at=datetime.now(),
                updated_at=datetime.now(),
                tags=tags or []
            )
            
            # Save template
            self._save_template(template)
            self.templates[template_id] = template
            
            logger.info(f"Created VM template: {name} ({template_id})")
            return template
            
        except Exception as e:
            logger.error(f"Error creating template: {e}")
            raise
    
    def _save_template(self, template: VMTemplate):
        """Save template to disk"""
        try:
            template_file = self.template_dir / f"{template.template_id}.json"
            
            # Convert to dict for JSON serialization
            data = {
                'template_id': template.template_id,
                'name': template.name,
                'description': template.description,
                'base_config': asdict(template.base_config),
                'post_install_scripts': template.post_install_scripts,
                'applications': template.applications,
                'settings': template.settings,
                'created_at': template.created_at.isoformat(),
                'updated_at': template.updated_at.isoformat(),
                'tags': template.tags,
                'version': template.version
            }
            
            with open(template_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving template: {e}")
            raise
    
    def get_template(self, template_id: str) -> Optional[VMTemplate]:
        """Get a template by ID"""
        return self.templates.get(template_id)
    
    def list_templates(self, tags: Optional[List[str]] = None) -> List[VMTemplate]:
        """List all templates, optionally filtered by tags"""
        templates = list(self.templates.values())
        
        if tags:
            templates = [t for t in templates if any(tag in t.tags for tag in tags)]
            
        return templates
    
    def update_template(self, template_id: str, **kwargs) -> bool:
        """Update an existing template"""
        try:
            if template_id not in self.templates:
                logger.error(f"Template {template_id} not found")
                return False
            
            template = self.templates[template_id]
            
            # Update fields
            for key, value in kwargs.items():
                if hasattr(template, key):
                    setattr(template, key, value)
            
            template.updated_at = datetime.now()
            
            # Save updated template
            self._save_template(template)
            
            logger.info(f"Updated template: {template.name} ({template_id})")
            return True
            
        except Exception as e:
            logger.error(f"Error updating template: {e}")
            return False
    
    def delete_template(self, template_id: str) -> bool:
        """Delete a template"""
        try:
            if template_id not in self.templates:
                logger.error(f"Template {template_id} not found")
                return False
            
            # Remove from memory
            template = self.templates.pop(template_id)
            
            # Remove from disk
            template_file = self.template_dir / f"{template_id}.json"
            if template_file.exists():
                template_file.unlink()
            
            logger.info(f"Deleted template: {template.name} ({template_id})")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting template: {e}")
            return False
    
    async def deploy_from_template(self, template_id: str, vm_name: str,
                                  orchestrator: VMOrchestrator,
                                  custom_config: Optional[Dict[str, Any]] = None) -> str:
        """Deploy a new VM from a template"""
        try:
            template = self.get_template(template_id)
            if not template:
                raise Exception(f"Template {template_id} not found")
            
            # Create VM configuration from template
            config = VMConfiguration(
                name=vm_name,
                memory_mb=template.base_config.memory_mb,
                disk_size_gb=template.base_config.disk_size_gb,
                cpu_cores=template.base_config.cpu_cores,
                os_type=template.base_config.os_type,
                iso_path=template.base_config.iso_path,
                network_adapter=template.base_config.network_adapter,
                enable_3d=template.base_config.enable_3d,
                enable_clipboard=template.base_config.enable_clipboard,
                rdp_enabled=template.base_config.rdp_enabled,
                rdp_port=template.base_config.rdp_port
            )
            
            # Apply custom configuration if provided
            if custom_config:
                for key, value in custom_config.items():
                    if hasattr(config, key):
                        setattr(config, key, value)
            
            # Create VM
            vm_uuid = await orchestrator.create_vm(vm_name, config)
            
            # Start VM
            await orchestrator.start_vm(vm_name)
            
            # Execute post-install scripts
            if template.post_install_scripts:
                await self._execute_post_install_scripts(
                    vm_name, template.post_install_scripts, orchestrator
                )
            
            logger.info(f"Deployed VM '{vm_name}' from template '{template.name}'")
            return vm_uuid
            
        except Exception as e:
            logger.error(f"Error deploying from template: {e}")
            raise
    
    async def _execute_post_install_scripts(self, vm_name: str, 
                                          scripts: List[Dict[str, Any]],
                                          orchestrator: VMOrchestrator):
        """Execute post-installation scripts on the VM"""
        try:
            for script in scripts:
                script_type = script.get('type', 'sequence')
                
                if script_type == 'sequence':
                    # Execute automation sequence
                    task_id = await orchestrator.add_task(
                        VMTaskType.AUTOMATE_SEQUENCE,
                        {
                            'vm_name': vm_name,
                            'sequence': script['actions']
                        }
                    )
                    logger.info(f"Executing automation sequence on VM '{vm_name}'")
                    
                elif script_type == 'command':
                    # Execute remote command
                    task_id = await orchestrator.add_task(
                        VMTaskType.REMOTE_COMMAND,
                        {
                            'vm_name': vm_name,
                            'command': script['command'],
                            'username': script.get('username', 'Administrator'),
                            'password': script.get('password', '')
                        }
                    )
                    logger.info(f"Executing command on VM '{vm_name}': {script['command']}")
                    
                # Add delay between scripts
                import asyncio
                await asyncio.sleep(script.get('delay', 5))
                
        except Exception as e:
            logger.error(f"Error executing post-install scripts: {e}")
            raise


# Pre-defined templates
def create_default_templates(manager: VMTemplateManager):
    """Create default VM templates"""
    
    # Windows 11 Development Template
    win11_dev_config = VMConfiguration(
        name="win11_dev_template",
        memory_mb=8192,
        disk_size_gb=100,
        cpu_cores=4,
        os_type="Windows11_64",
        enable_3d=True,
        enable_clipboard=True,
        rdp_enabled=True
    )
    
    win11_dev_scripts = [
        {
            'type': 'sequence',
            'actions': [
                {'type': 'click', 'x': 100, 'y': 100, 'button': 'left'},
                {'type': 'send_key', 'key': 'win'},
                {'type': 'type_text', 'text': 'powershell', 'delay': 0.1},
                {'type': 'send_key', 'key': 'enter'}
            ],
            'delay': 10
        }
    ]
    
    manager.create_template(
        name="Windows 11 Developer",
        description="Windows 11 VM optimized for development with Visual Studio, VS Code, and dev tools",
        base_config=win11_dev_config,
        post_install_scripts=win11_dev_scripts,
        applications=["Visual Studio 2022", "VS Code", "Git", "Python", "Node.js"],
        settings={
            "enable_wsl": True,
            "enable_hyper_v": False,
            "enable_developer_mode": True
        },
        tags=["windows", "development", "programming"]
    )
    
    # Windows 11 Testing Template
    win11_test_config = VMConfiguration(
        name="win11_test_template",
        memory_mb=4096,
        disk_size_gb=50,
        cpu_cores=2,
        os_type="Windows11_64",
        enable_3d=False,
        enable_clipboard=True,
        rdp_enabled=True
    )
    
    manager.create_template(
        name="Windows 11 Testing",
        description="Lightweight Windows 11 VM for testing and QA purposes",
        base_config=win11_test_config,
        applications=["Chrome", "Firefox", "Edge"],
        settings={
            "disable_updates": True,
            "disable_defender": True,
            "restore_point_on_boot": True
        },
        tags=["windows", "testing", "qa"]
    )
    
    # Windows 10 Legacy Template
    win10_legacy_config = VMConfiguration(
        name="win10_legacy_template",
        memory_mb=4096,
        disk_size_gb=60,
        cpu_cores=2,
        os_type="Windows10_64",
        enable_3d=False,
        enable_clipboard=True,
        rdp_enabled=True
    )
    
    manager.create_template(
        name="Windows 10 Legacy",
        description="Windows 10 VM for legacy application compatibility",
        base_config=win10_legacy_config,
        applications=[".NET Framework 3.5", "Visual C++ Redistributables"],
        settings={
            "compatibility_mode": True,
            "disable_cortana": True
        },
        tags=["windows", "legacy", "compatibility"]
    )


def main():
    """Example usage of VM Template Manager"""
    import asyncio
    
    # Create template manager
    manager = VMTemplateManager()
    
    # Create default templates
    create_default_templates(manager)
    
    # List templates
    print("\nAvailable VM Templates:")
    print("-" * 60)
    for template in manager.list_templates():
        print(f"ID: {template.template_id}")
        print(f"Name: {template.name}")
        print(f"Description: {template.description}")
        print(f"Tags: {', '.join(template.tags)}")
        print(f"Created: {template.created_at}")
        print("-" * 60)
    
    # Example: Deploy from template
    async def deploy_example():
        orchestrator = VMOrchestrator()
        await orchestrator.initialize()
        
        # Find development template
        dev_templates = manager.list_templates(tags=["development"])
        if dev_templates:
            template = dev_templates[0]
            
            # Deploy VM from template
            vm_uuid = await manager.deploy_from_template(
                template.template_id,
                "my-dev-vm",
                orchestrator,
                custom_config={"memory_mb": 16384}  # Override memory
            )
            
            print(f"Deployed VM: {vm_uuid}")
    
    # Uncomment to run deployment example
    # asyncio.run(deploy_example())


if __name__ == "__main__":
    main() 