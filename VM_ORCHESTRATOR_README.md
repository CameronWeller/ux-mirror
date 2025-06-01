# UX-MIRROR VM Orchestrator

## 🚀 Quick Start Guide

The VM Orchestrator is the core component for managing Windows virtual machines in the UX-MIRROR system. It provides automated VM lifecycle management, intelligent monitoring, and seamless integration with AI agents.

### Prerequisites

- **Host System**: Windows 10/11 with 16GB+ RAM
- **VirtualBox**: Version 7.0+ installed and in PATH
- **Python**: 3.11+ with pip
- **Hardware**: VT-x/AMD-V enabled in BIOS
- **Disk Space**: 100GB+ free space

### Installation

1. **Clone and Setup**
```bash
git clone https://github.com/your-org/ux-mirror.git
cd ux-mirror

# Run automated setup
python setup_vm_environment.py
```

2. **Install Dependencies**
```bash
# Install core dependencies (most reliable)
pip install -r requirements-vm-core.txt

# Or install full feature set
pip install -r requirements-vm.txt
```

3. **Verify Installation**
```bash
python vm_cli.py system-status
```

## 📖 Usage Guide

### Creating Your First VM

**Option 1: Using the CLI**
```bash
# Create a basic Windows 11 VM
python vm_cli.py create --name my-first-vm --memory 8192 --disk 100

# Start the VM
python vm_cli.py start --name my-first-vm

# Check status
python vm_cli.py status --name my-first-vm
```

**Option 2: Using the Windows VM Creator**
```bash
# Create optimized Windows VM with ISO
python create_windows_vm.py --name win11-vm --windows-version 11 --memory 8192 --disk 100 --iso-path ./iso/Windows11.iso --auto-start
```

### Basic VM Operations

```bash
# List all VMs
python vm_cli.py list

# Start a VM
python vm_cli.py start --name vm-name

# Stop a VM (graceful)
python vm_cli.py stop --name vm-name

# Force stop a VM
python vm_cli.py stop --name vm-name --force

# Create snapshot
python vm_cli.py snapshot --name vm-name --snapshot-name "clean-state"

# Take screenshot and analyze UI
python vm_cli.py screenshot --name vm-name --analyze
```

### Remote VM Control

```bash
# Execute commands via SSH (requires SSH server in VM)
python vm_cli.py exec --name vm-name --command "dir" --username admin --password password

# View system status
python vm_cli.py system-status
```

## 🏗️ Architecture Overview

### Core Components

1. **VMOrchestrator**: Main coordination engine
2. **VirtualBoxManager**: VirtualBox API interface
3. **VMScreenCapture**: Computer vision and screenshot analysis
4. **VMRemoteControl**: SSH and remote command execution
5. **VM CLI**: Command-line interface
6. **WindowsVMCreator**: Specialized Windows VM creation

### VM Lifecycle

```
Create → Configure → Start → Monitor → Snapshot → Stop → Cleanup
   ↓         ↓         ↓        ↓          ↓        ↓       ↓
Storage   Settings   Boot   Health    Backup   Shutdown Destroy
```

### Task Processing

- Asynchronous task queue system
- Priority-based scheduling (Critical → High → Medium → Low)
- Automatic retry with exponential backoff
- Real-time status monitoring

## 🔧 Configuration

### VM Orchestrator Configuration (`config/vm_orchestrator.json`)

```json
{
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
  "networking": {
    "vnc_port_range": [5900, 5950],
    "rdp_port_range": [3389, 3400],
    "ssh_port_range": [2222, 2232]
  }
}
```

### Customizing VM Settings

```python
from vm_orchestrator import VMConfiguration

config = VMConfiguration(
    name="custom-vm",
    memory_mb=16384,        # 16GB RAM
    disk_size_gb=200,       # 200GB disk
    cpu_cores=8,            # 8 CPU cores
    os_type="Windows11_64", # OS type
    enable_3d=True,         # 3D acceleration
    rdp_enabled=True        # Enable RDP
)
```

## 🖥️ VM Management Examples

### Programmatic VM Control

```python
import asyncio
from vm_orchestrator import VMOrchestrator, VMConfiguration

async def create_and_manage_vm():
    orchestrator = VMOrchestrator()
    await orchestrator.initialize()
    
    # Create VM
    config = VMConfiguration(name="test-vm", memory_mb=8192)
    vm_uuid = await orchestrator.create_vm("test-vm", config)
    
    # Start VM
    await orchestrator.start_vm("test-vm")
    
    # Take screenshot
    task_id = await orchestrator.add_task(
        VMTaskType.SCREEN_CAPTURE,
        {"vm_name": "test-vm"}
    )
    
    # Get status
    status = orchestrator.get_vm_status("test-vm")
    print(f"VM State: {status['state']}")

asyncio.run(create_and_manage_vm())
```

### Batch VM Operations

```bash
# Create multiple VMs
for i in {1..3}; do
    python vm_cli.py create --name "test-vm-$i" --memory 4096
done

# Start all test VMs
python vm_cli.py list | grep "test-vm" | awk '{print $1}' | xargs -I {} python vm_cli.py start --name {}
```

## 🔍 Monitoring and Troubleshooting

### System Status

```bash
# Check overall system health
python vm_cli.py system-status

# Monitor specific VM
python vm_cli.py status --name vm-name

# View logs
tail -f logs/vm_orchestrator.log
```

### Performance Metrics

The orchestrator tracks:
- Total VMs created/running
- Task completion rates
- System resource usage
- Average task execution time
- Error rates and recovery

### Common Issues

**VM Creation Fails**
```bash
# Check VirtualBox installation
VBoxManage --version

# Verify hardware virtualization
python setup_vm_environment.py
```

**VM Won't Start**
```bash
# Check VM configuration
python vm_cli.py status --name vm-name

# Test VirtualBox directly
VBoxManage startvm vm-name --type headless
```

**Screen Capture Fails**
```bash
# Ensure VM is running
python vm_cli.py list

# Check VNC connection
# VM must be running and VNC enabled
```

## 🔧 Advanced Configuration

### Custom Storage Locations

```json
{
  "storage": {
    "vm_storage_path": "D:/VMs",
    "snapshots_path": "D:/Snapshots", 
    "iso_path": "D:/ISOs"
  }
}
```

### Network Configuration

```json
{
  "networking": {
    "vnc_port_range": [5900, 5950],
    "rdp_port_range": [3389, 3400],
    "enable_port_forwarding": true
  }
}
```

### Performance Tuning

```json
{
  "performance": {
    "enable_hardware_acceleration": true,
    "enable_nested_virtualization": true,
    "memory_ballooning": true,
    "cpu_priority": "high"
  }
}
```

## 🤖 Integration with UX Agents

### Automatic Agent Registration

```python
# VM automatically registers with UX-MIRROR agent system
await orchestrator.initialize()  # Discovers existing VMs
```

### Task Distribution

```python
# Create analysis task for VM
task_id = await orchestrator.add_task(
    VMTaskType.SCREEN_CAPTURE,
    {
        "vm_name": "target-vm",
        "analysis_type": "ui_elements"
    }
)
```

### Agent Communication

VMs communicate with agents via:
- WebSocket connections
- Task queue system  
- Shared state management
- Real-time metrics

## 📊 API Reference

### VMOrchestrator Class

```python
class VMOrchestrator:
    async def create_vm(name: str, config: VMConfiguration) -> str
    async def start_vm(vm_name: str) -> bool
    async def stop_vm(vm_name: str) -> bool
    async def add_task(task_type: VMTaskType, data: dict) -> str
    def get_vm_status(vm_name: str) -> dict
    def get_system_status() -> dict
```

### CLI Commands

| Command | Description | Example |
|---------|-------------|---------|
| `create` | Create new VM | `python vm_cli.py create --name vm1` |
| `start` | Start VM | `python vm_cli.py start --name vm1` |
| `stop` | Stop VM | `python vm_cli.py stop --name vm1` |
| `list` | List all VMs | `python vm_cli.py list` |
| `status` | Show VM status | `python vm_cli.py status --name vm1` |
| `screenshot` | Take screenshot | `python vm_cli.py screenshot --name vm1` |
| `exec` | Execute command | `python vm_cli.py exec --name vm1 --command "dir"` |

## 🔐 Security Considerations

### VM Isolation
- VMs run in isolated environments
- Network isolation via NAT
- Snapshot-based rollback capability
- Audit logging enabled

### Access Control
```json
{
  "security": {
    "require_authentication": false,
    "firewall_enabled": true,
    "audit_logging": true
  }
}
```

### Best Practices
1. Use snapshots before risky operations
2. Enable RDP only when needed
3. Use strong passwords for VM accounts
4. Monitor resource usage
5. Regular cleanup of old VMs

## 🛠️ Development Guide

### Extending the Orchestrator

```python
# Add custom VM task type
class CustomVMTask(VMTaskType):
    CUSTOM_ANALYSIS = "custom_analysis"

# Implement task handler
async def _handle_custom_task(self, task):
    # Custom task logic
    pass
```

### Adding New VM Types

```python
class LinuxVMCreator(WindowsVMCreator):
    def _get_os_type(self, distro: str) -> str:
        return f"Ubuntu_64"  # or other Linux variants
```

### Custom Monitoring

```python
# Add custom metrics
self.performance_metrics["custom_metric"] = value

# Custom health checks
async def _custom_health_check(self):
    # Custom monitoring logic
    pass
```

## 📈 Roadmap

### Phase 1: Foundation ✅
- [x] VM lifecycle management
- [x] Basic automation
- [x] CLI interface
- [x] Configuration system

### Phase 2: Intelligence 🚧
- [ ] Advanced UI analysis
- [ ] ML-based VM optimization
- [ ] Automated failure recovery
- [ ] Multi-VM coordination

### Phase 3: Scale 📋
- [ ] Cloud VM support
- [ ] Multi-hypervisor support
- [ ] Container integration
- [ ] Web dashboard

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Update documentation
5. Submit pull request

Focus areas:
- New hypervisor integrations
- Advanced computer vision
- Performance optimizations
- Cloud VM support

## 📞 Support

- **Documentation**: See README.md and inline code comments
- **Issues**: GitHub issue tracker
- **Examples**: `CLI_EXAMPLES.md` and `quick_start_example.py`
- **Setup**: Run `python setup_vm_environment.py` for environment validation

---

*UX-MIRROR VM Orchestrator: Intelligent automation meets virtual machine mastery.* 🚀 