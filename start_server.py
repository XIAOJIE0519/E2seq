"""Portable compatibility launcher.

Use ``python start.py`` for the guided bilingual launcher.  This file remains
for older shortcuts and forwards all arguments without assuming a drive,
working directory, host, or port.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
os.chdir(PROJECT_ROOT)


if __name__ == "__main__":
    command = [sys.executable, str(PROJECT_ROOT / "start.py"), *sys.argv[1:]]
    raise SystemExit(subprocess.call(command, cwd=PROJECT_ROOT))
