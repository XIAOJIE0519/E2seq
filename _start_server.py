"""Backward-compatible restart entry point.

The old helper killed every process listening on a fixed port.  It now uses
the safe guided launcher and never terminates unrelated processes.
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
