"""Error recovery system for E2sc Agent - Retry and fallback mechanisms."""

import time
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

from e2sc.utils import get_logger

logger = get_logger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RecoveryStrategy(Enum):
    """Recovery strategies."""
    RETRY = "retry"
    FALLBACK = "fallback"
    SKIP = "skip"
    ABORT = "abort"


class ErrorRecovery:
    """Error recovery manager with retry and fallback mechanisms."""
    
    def __init__(self, max_retries: int = 3, retry_delay: float = 1.0):
        """Initialize error recovery."""
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.error_history: List[Dict[str, Any]] = []
        self.recovery_stats = {
            "total_errors": 0,
            "recovered_errors": 0,
            "failed_recoveries": 0
        }
    
    def execute_with_retry(
        self,
        func: Callable,
        *args,
        max_retries: Optional[int] = None,
        fallback_func: Optional[Callable] = None,
        error_context: Optional[str] = None,
        **kwargs
    ) -> Tuple[bool, Any, Optional[str]]:
        """Execute function with retry mechanism."""
        max_attempts = max_retries or self.max_retries
        context = error_context or func.__name__
        
        for attempt in range(max_attempts):
            try:
                result = func(*args, **kwargs)
                
                if attempt > 0:
                    logger.info(f"[OK] Recovered after {attempt} retries: {context}")
                    self.recovery_stats["recovered_errors"] += 1
                
                return True, result, None
                
            except Exception as e:
                last_error = str(e)  # save before Python clears 'e' at block exit
                self.error_history.append({
                    "context": context,
                    "attempt": attempt + 1,
                    "error": last_error,
                    "timestamp": time.time()
                })
                
                self.recovery_stats["total_errors"] += 1
                
                if attempt < max_attempts - 1:
                    logger.warning(f"[FAIL] Attempt {attempt + 1}/{max_attempts} failed: {context} - {last_error}")
                    time.sleep(self.retry_delay * (attempt + 1))
                else:
                    logger.error(f"[FAIL] All {max_attempts} attempts failed: {context}")
        
        # Try fallback
        if fallback_func:
            try:
                logger.info(f"-> Trying fallback: {context}")
                result = fallback_func(*args, **kwargs)
                self.recovery_stats["recovered_errors"] += 1
                return True, result, None
            except Exception as fe:
                logger.error(f"[FAIL] Fallback failed: {context} - {fe}")
                last_error = str(fe)
        
        self.recovery_stats["failed_recoveries"] += 1
        return False, None, last_error
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get error statistics."""
        return {
            "stats": self.recovery_stats,
            "recovery_rate": self.recovery_stats["recovered_errors"] / 
                           max(1, self.recovery_stats["total_errors"]),
            "recent_errors": self.error_history[-10:]
        }


def get_error_recovery() -> ErrorRecovery:
    """Get global error recovery instance."""
    global _error_recovery
    if "_error_recovery" not in globals():
        _error_recovery = ErrorRecovery()
    return _error_recovery
