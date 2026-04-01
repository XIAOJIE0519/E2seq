"""Logging utilities for E2sc."""

import logging
import sys
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.logging import RichHandler


class E2scLogger:
    """Custom logger for E2sc with Rich formatting."""
    
    def __init__(self, name: str = "e2sc", level: str = "INFO"):
        """Initialize logger.
        
        Args:
            name: Logger name
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.name = name
        # Force UTF-8 on Windows to avoid GBK UnicodeEncodeError with Rich
        try:
            _con_file = open(sys.stderr.fileno(), mode='w', encoding='utf-8', errors='replace', closefd=False)
        except Exception:
            _con_file = sys.stderr
        self.console = Console(file=_con_file, highlight=False)
        self.level = level
        
        # Setup logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # Remove existing handlers
        self.logger.handlers.clear()
        
        # Add Rich console handler
        console_handler = RichHandler(
            console=self.console,
            rich_tracebacks=True,
            tracebacks_show_locals=True,
        )
        console_handler.setLevel(getattr(logging, level.upper()))
        self.logger.addHandler(console_handler)
    
    def debug(self, message: str, **kwargs) -> None:
        """Log debug message."""
        self.logger.debug(message, **kwargs)
    
    def info(self, message: str, **kwargs) -> None:
        """Log info message."""
        self.logger.info(message, **kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """Log warning message."""
        self.logger.warning(message, **kwargs)
    
    def error(self, message: str, **kwargs) -> None:
        """Log error message."""
        self.logger.error(message, **kwargs)
    
    def critical(self, message: str, **kwargs) -> None:
        """Log critical message."""
        self.logger.critical(message, **kwargs)


_logger: Optional[E2scLogger] = None


def get_logger(name: str = "e2sc") -> E2scLogger:
    """Get global logger instance."""
    global _logger
    if _logger is None:
        _logger = E2scLogger(name)
    return _logger
