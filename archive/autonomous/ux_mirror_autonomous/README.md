# 🤖 UX-MIRROR Autonomous Testing Mode

## Phase 1: Infrastructure Setup ✅ Complete

This directory contains the autonomous testing infrastructure for UX-MIRROR, designed to provide automated UX testing capabilities without disrupting the host system.

### Current Status: Phase 1 Complete

- [x] **VM Configuration**: Pop!_OS 22.04 LTS setup with optimal settings
- [x] **Directory Structure**: Organized testing framework layout
- [x] **Windows Compatibility**: Full Windows 10/11 support with PowerShell/CMD
- [x] **Python Dependencies**: Core packages installed and configured
- [x] **Management Scripts**: VM lifecycle and test execution tools
- [x] **Documentation**: Comprehensive setup and usage instructions

### Architecture Overview

```
Host System (Windows)
├── UX-MIRROR Launcher
│   ├── 🚀 Integrated Mode
│   ├── 🎮 Game Only Mode  
│   ├── 🔍 Analysis Only Mode
│   └── 🤖 Autonomous Testing Mode ← NEW!
└── Pop!_OS VM Environment
    ├── Target Game/Application
    ├── PyAutoGUI Input Controller
    ├── Screen Analysis Tools
    └── Test Execution Framework
```

## Quick Start Guide

### Prerequisites

1. **Windows 10/11** with virtualization support
2. **Python 3.8+** installed and in PATH
3. **VirtualBox** or **VMware** installed
4. **4GB+ available RAM** for VM
5. **60GB+ disk space** for VM

### Step 1: Verify Setup

```bash
# Check if Phase 1 setup is complete
python run_tests.py
```

### Step 2: Download Pop!_OS ISO

- **URL**: https://pop-iso.sfo2.cdn.digitaloceanspaces.com/22.04/amd64/intel/30/pop-os_22.04_amd64_intel_30.iso
- **Size**: ~2.5GB
- **Save to**: `downloads/pop-os_22.04_amd64_intel_30.iso`

### Step 3: Create Virtual Machine

```bash
# Get VM creation instructions
python manage_vm.py create
```

**Manual VM Setup (VirtualBox):**
1. Open VirtualBox Manager
2. Click "New" → Create VM
3. Configure:
   - **Name**: ux-mirror-autonomous  
   - **Type**: Linux
   - **Version**: Ubuntu (64-bit)
   - **Memory**: 4096 MB (4GB)
   - **Storage**: 60 GB (dynamically allocated)
4. Mount the Pop!_OS ISO
5. Start VM and install Pop!_OS

### Step 4: VM Post-Installation

1. Install Guest Additions (VirtualBox) or VMware Tools
2. Configure shared folders
3. Set up network (NAT recommended)
4. Copy `vm_setup.sh` to VM and run it

### Step 5: Configure Autonomous Testing

Inside the VM, the setup script will:
- Install Python testing frameworks
- Configure PyAutoGUI for input automation
- Set up screen capture tools
- Create test result directories
- Configure safety mechanisms

## Directory Structure

```
ux_mirror_autonomous/
├── config/
│   └── vm_config.yaml           # VM settings and configuration
├── core/                        # Core testing framework (Phase 2)
├── scenarios/                   # Test scenarios (Phase 2+)
├── utils/                       # Utility scripts and helpers
├── test_results/
│   ├── screenshots/             # Captured screenshots
│   ├── videos/                  # Recorded test sessions
│   └── reports/                 # Generated test reports
├── downloads/
│   └── pop-os_*.iso            # Pop!_OS installation ISO
├── manage_vm.py                 # VM lifecycle management
├── run_tests.py                 # Test execution and status
└── README.md                    # This file
```

## Configuration

### VM Settings (`config/vm_config.yaml`)

```yaml
vm_settings:
  name: "ux-mirror-autonomous"
  os: "pop-os-22.04"
  cpu_cores: 4
  memory_gb: 4                   # Configurable via launcher (2-8GB)
  storage_gb: 60
  graphics: "virtio-gpu"

network:
  type: "NAT"
  port_forwards:
    - host: 8080, guest: 8080    # UX-MIRROR communication
    - host: 5900, guest: 5900    # VNC access
```

### Launcher Integration

The autonomous testing mode is integrated into the main UX-MIRROR launcher:

```python
# In launch_ux_mirror.py - new mode added:
🤖 Autonomous Testing Mode
    • VM environment with automated testing
    • Best for: Continuous integration, overnight testing
```

## Commands

### VM Management

```bash
# Check system status
python manage_vm.py status

# Get VM creation instructions  
python manage_vm.py create

# Get ISO download info
python manage_vm.py download
```

### Test Execution

```bash
# Show current status and next steps
python run_tests.py

# Phase 2+ will add:
# python run_tests.py --scenario game_of_life
# python run_tests.py --mode continuous
```

## Implementation Phases

### ✅ Phase 1: Infrastructure Setup (Complete)
- VM configuration and management
- Directory structure and dependencies
- Windows compatibility layer
- Basic management scripts

### ⏳ Phase 2: Input Automation System (Next)
- PyAutoGUI integration
- Human-like input simulation
- Screenshot and recording capabilities
- Basic test scenarios

### ⏳ Phase 3: UX-MIRROR Integration
- Real-time metrics collection
- Test orchestration
- Communication with host UX-MIRROR
- Result synchronization

### ⏳ Phase 4: Metrics & Reporting
- Comprehensive UX metrics
- Automated report generation
- Performance analysis
- Regression detection

### ⏳ Phase 5: Advanced Features
- Computer vision for UI element detection
- Machine learning for test optimization
- Adaptive testing patterns
- Continuous improvement

### ⏳ Phase 6: Production Deployment
- CI/CD integration
- Scheduled testing
- Remote execution
- Enterprise features

## Troubleshooting

### Common Issues

**VM Creation Failed:**
- Ensure virtualization is enabled in BIOS
- Check available disk space (60GB+ required)
- Verify ISO file integrity

**Poor VM Performance:**
- Increase VM memory allocation
- Enable hardware acceleration
- Close unnecessary host applications
- Use SSD storage if available

**Network Issues:**
- Use NAT networking mode
- Check firewall settings
- Verify port forwarding configuration

**Shared Folder Problems:**
- Install Guest Additions first
- Check folder permissions
- Restart VM after configuration

### Getting Help

1. **Documentation**: See `docs/AUTONOMOUS_TESTING_PLAN.md`
2. **Issues**: Report problems via GitHub Issues
3. **Community**: Join the UX-MIRROR Discord/forums

## Windows-Specific Notes

- **PowerShell/CMD**: All scripts are Windows compatible
- **VirtualBox**: Recommended for best compatibility
- **VMware**: Also supported, requires VMware Tools
- **Hyper-V**: Provides better performance on Windows Pro
- **WSL2**: Alternative for Linux-native development

## Security & Safety

### Built-in Safety Features

- **PyAutoGUI Failsafe**: Move mouse to top-left corner to stop
- **Time Limits**: Maximum test execution time (1 hour)
- **Resource Monitoring**: CPU/memory usage limits
- **Error Recovery**: Automatic cleanup on failures
- **Isolation**: All testing contained within VM

### Best Practices

- Keep VM snapshots before testing
- Monitor resource usage during tests
- Use dedicated testing machines for production
- Regular backup of test results
- Review logs for security events

## Contributing

Interested in contributing to autonomous testing mode?

1. **Phase 2 Development**: Help implement input automation
2. **Test Scenarios**: Create test cases for 3D Game of Life
3. **Documentation**: Improve setup guides and tutorials
4. **Bug Reports**: Test on different Windows configurations
5. **Features**: Suggest improvements and enhancements

## License

Same as main UX-MIRROR project.

---

**🎯 Phase 1 Complete!** Ready for VM setup and Phase 2 development.

For detailed implementation plans, see: `docs/AUTONOMOUS_TESTING_PLAN.md` 