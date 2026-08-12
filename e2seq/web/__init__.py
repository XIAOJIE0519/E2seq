"""Web interface initialization."""

from pathlib import Path

__version__ = "1.0.0"

# Get paths
WEB_DIR = Path(__file__).parent
STATIC_DIR = WEB_DIR / "static"
TEMPLATES_DIR = WEB_DIR / "templates"

__all__ = ["WEB_DIR", "STATIC_DIR", "TEMPLATES_DIR"]
