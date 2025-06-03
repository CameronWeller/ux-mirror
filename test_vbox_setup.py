import sys
import os

# Add VirtualBox SDK to Python path if needed
vbox_sdk_path = r"C:\Program Files\Oracle\VirtualBox\sdk\bindings\python"
if os.path.exists(vbox_sdk_path):
    sys.path.append(vbox_sdk_path)

try:
    import vboxapi
    mgr = vboxapi.VirtualBoxManager(None, None)
    vbox = mgr.getVirtualBox()
    print("VirtualBox SDK initialized successfully!")
    print(f"VirtualBox version: {vbox.version}")
    print("\nAvailable VMs:")
    for machine in vbox.machines:
        print(f"- {machine.name} ({machine.state})")
except Exception as e:
    print(f"Error initializing VirtualBox SDK: {e}") 