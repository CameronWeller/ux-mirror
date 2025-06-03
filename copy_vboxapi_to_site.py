import shutil
import site
import os
from pathlib import Path

src = Path('sdk/installer/vboxapi')
dst = Path(site.getsitepackages()[0]) / 'vboxapi'

if dst.exists():
    shutil.rmtree(dst)
shutil.copytree(src, dst)
print(f"Copied {src} to {dst}") 