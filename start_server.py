#!/usr/bin/env python3
"""Launcher: starts uvicorn in-process (no subprocess/reload) so it stays alive."""
import os, sys
os.chdir(r"f:\1a-sc-agent")
sys.path.insert(0, r"f:\1a-sc-agent")

import uvicorn
uvicorn.run(
    "e2sc.api.server:app",
    host="0.0.0.0",
    port=8000,
    reload=False,
    log_level="info",
    access_log=False,
)
