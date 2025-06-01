# UX-MIRROR VM Orchestrator - Quick Start Guide

This guide demonstrates the new features added to the VM Orchestrator, including input automation and template management.

## 🎯 New Features Overview

### 1. **Input Automation**
- Mouse movements, clicks, and drags
- Keyboard input and special keys
- Automated UI interaction sequences
- OCR-based element finding

### 2. **VM Templates**  
- Pre-configured VM setups
- Quick deployment from templates
- Customizable post-installation scripts

### 3. **Enhanced Testing**
- Comprehensive test suite
- Mocked VirtualBox API for testing
- Integration tests

## 🚀 Quick Start Examples

### Basic VM Operations

```bash
# Create a VM
python vm_cli.py create --name test-vm --memory 8192 --disk 100

# Start the VM
python vm_cli.py start --name test-vm

# Check status
python vm_cli.py status --name test-vm
```

### Input Automation

#### Click at Coordinates
```bash
python vm_cli.py click-vm --name test-vm --x 100 --y 200
```

#### Type Text
```bash
python vm_cli.py type-text --name test-vm --text "Hello World"
```

#### Send Special Keys
```bash
python vm_cli.py send-key --name test-vm --key enter
python vm_cli.py send-key --name test-vm --key "ctrl-s"
```

#### Run Automation Sequence
```bash
# Using the provided example
python vm_cli.py automate --name test-vm --sequence-file examples/automation_sequences/open_notepad.json
```

### Template Management

#### Create a Template
```bash
python vm_cli.py template create \
  --name "Windows Dev" \
  --description "Development environment with VS Code" \
  --memory 8192 \
  --disk 100 \
  --cpus 4 \
  --tags development windows
```

#### List Templates
```bash
# List all templates
python vm_cli.py template list

# Filter by tags
python vm_cli.py template list --tags development
```

#### Deploy from Template
```bash
python vm_cli.py template deploy \
  --template-id <template-id> \
  --vm-name my-dev-vm \
  --memory 16384  # Override memory
```

## 📝 Creating Automation Sequences

Automation sequences are JSON files that define a series of actions. Here's the structure:

```json
[
  {
    "type": "click",
    "x": 100,
    "y": 200,
    "button": "left",
    "comment": "Click on button"
  },
  {
    "type": "type_text",
    "text": "Hello",
    "delay": 0.05,
    "comment": "Type greeting"
  },
  {
    "type": "send_key",
    "key": "enter",
    "comment": "Press Enter"
  },
  {
    "type": "delay",
    "seconds": 2,
    "comment": "Wait 2 seconds"
  },
  {
    "type": "drag",
    "start_x": 100,
    "start_y": 100,
    "end_x": 300,
    "end_y": 300,
    "comment": "Drag element"
  },
  {
    "type": "scroll",
    "x": 400,
    "y": 300,
    "direction": "down",
    "amount": 5,
    "comment": "Scroll down"
  }
]
```

### Action Types:
- **click**: Mouse click at coordinates
- **type_text**: Type text with optional delay
- **send_key**: Send special keys (enter, tab, ctrl-c, etc.)
- **delay**: Wait for specified seconds
- **drag**: Drag from one point to another
- **scroll**: Scroll at position

## 🧪 Running Tests

Run the comprehensive test suite:

```bash
python vm_cli.py test
```

Or run tests directly:

```bash
python test_vm_orchestrator.py
```

## 💡 Advanced Examples

### 1. Automated Software Installation

Create a sequence to install software:

```json
[
  {
    "type": "send_key",
    "key": "win-r",
    "comment": "Open Run dialog"
  },
  {
    "type": "type_text",
    "text": "https://code.visualstudio.com/download",
    "delay": 0.05
  },
  {
    "type": "send_key",
    "key": "enter"
  }
]
```

### 2. Web Testing Automation

Test a web application:

```json
[
  {
    "type": "click",
    "x": 500,
    "y": 100,
    "comment": "Click address bar"
  },
  {
    "type": "type_text",
    "text": "http://localhost:3000"
  },
  {
    "type": "send_key",
    "key": "enter"
  },
  {
    "type": "delay",
    "seconds": 3
  },
  {
    "type": "click",
    "x": 600,
    "y": 300,
    "comment": "Click login button"
  }
]
```

### 3. Using Templates for Different Environments

```bash
# Create templates for different use cases
python vm_cli.py template create --name "QA Testing" --memory 4096 --tags testing qa
python vm_cli.py template create --name "Production Sim" --memory 16384 --cpus 8 --tags production

# Deploy multiple instances
python vm_cli.py template deploy --template-id <qa-id> --vm-name qa-test-1
python vm_cli.py template deploy --template-id <qa-id> --vm-name qa-test-2
```

## 🔍 Monitoring and Debugging

### Check System Status
```bash
python vm_cli.py system-status
```

### View VM Logs
Monitor the orchestrator logs in real-time:
```bash
tail -f logs/vm_orchestrator.log
```

### Screenshot Analysis
```bash
python vm_cli.py screenshot --name test-vm --analyze
```

## 🛠️ Troubleshooting

### Common Issues

1. **VNC Connection Failed**
   - Ensure VM is running
   - Check VNC port allocation
   - Verify VirtualBox Extension Pack is installed

2. **Input Automation Not Working**
   - Confirm VNC connection is established
   - Check coordinates are within screen bounds
   - Add delays between actions if needed

3. **Template Deployment Fails**
   - Verify template exists: `python vm_cli.py template list`
   - Check resource availability
   - Review orchestrator logs

## 📚 Next Steps

1. **Explore Examples**: Check `examples/automation_sequences/` for more examples
2. **Create Custom Templates**: Build templates for your specific needs
3. **Integrate with CI/CD**: Use the orchestrator in your testing pipeline
4. **Contribute**: Add new automation capabilities or improve existing ones

For full documentation, see [VM_ORCHESTRATOR_README.md](VM_ORCHESTRATOR_README.md) 