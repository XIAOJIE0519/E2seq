"""State management for E2sc Agent - Persistent state tracking."""

import json
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from e2sc.utils import get_config, get_logger

logger = get_logger(__name__)


def _sanitize_scope_id(scope_id: str) -> str:
    """Return a filesystem-safe identifier for one chat scope."""
    safe = "".join(c for c in str(scope_id) if c.isalnum() or c in "-_")
    return safe or "default"


class AgentState(Enum):
    """Agent execution states."""
    IDLE = "idle"
    PLANNING = "planning"
    EXECUTING = "executing"
    RETRIEVING = "retrieving"
    SYNTHESIZING = "synthesizing"
    ERROR = "error"
    COMPLETED = "completed"


class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class StateManager:
    """Manage agent execution state with persistence."""
    
    def __init__(self, session_id: Optional[str] = None):
        """Initialize state manager."""
        config = get_config()
        self.state_dir = Path(config.database.db_path).expanduser() / "state"
        self.session_id = session_id
        if session_id:
            self.state_dir = self.state_dir / _sanitize_scope_id(session_id)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        
        self.state_file = self.state_dir / "current_state.json"
        self.checkpoint_dir = self.state_dir / "checkpoints"
        self.checkpoint_dir.mkdir(exist_ok=True)
        
        # Current state
        self.current_state = AgentState.IDLE
        self.task_queue: List[Dict[str, Any]] = []
        self.completed_tasks: List[Dict[str, Any]] = []
        self.failed_tasks: List[Dict[str, Any]] = []
        self.execution_context: Dict[str, Any] = {}
        
        # Load previous state if exists
        self._load_state()
    
    def _load_state(self):
        """Load state from file."""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    state_data = json.load(f)
                
                self.current_state = AgentState(state_data.get("current_state", "idle"))
                self.task_queue = state_data.get("task_queue", [])
                self.completed_tasks = state_data.get("completed_tasks", [])
                self.failed_tasks = state_data.get("failed_tasks", [])
                self.execution_context = state_data.get("execution_context", {})
                
                logger.info(f"State loaded: {self.current_state.value}")
            except Exception as e:
                logger.error(f"Error loading state: {e}")
    
    def _save_state(self):
        """Save current state to file."""
        try:
            state_data = {
                "current_state": self.current_state.value,
                "task_queue": self.task_queue,
                "completed_tasks": self.completed_tasks,
                "failed_tasks": self.failed_tasks,
                "execution_context": self.execution_context,
                "timestamp": datetime.now().isoformat()
            }
            
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state_data, f, indent=2, ensure_ascii=False)
            
            logger.debug("State saved")
        except Exception as e:
            logger.error(f"Error saving state: {e}")
    
    def set_state(self, new_state: AgentState):
        """Set agent state.
        
        Args:
            new_state: New agent state
        """
        old_state = self.current_state
        self.current_state = new_state
        self._save_state()
        logger.info(f"State transition: {old_state.value} -> {new_state.value}")
    
    def add_task(self, task: Dict[str, Any]):
        """Add task to queue.
        
        Args:
            task: Task dictionary with action, params, etc.
        """
        task_with_status = {
            **task,
            "status": TaskStatus.PENDING.value,
            "added_at": datetime.now().isoformat(),
            "task_id": f"task_{len(self.task_queue) + 1}"
        }
        self.task_queue.append(task_with_status)
        self._save_state()
        logger.info(f"Task added: {task_with_status['task_id']}")
    
    def get_next_task(self) -> Optional[Dict[str, Any]]:
        """Get next pending task.
        
        Returns:
            Next task or None
        """
        for task in self.task_queue:
            if task["status"] == TaskStatus.PENDING.value:
                return task
        return None
    
    def update_task_status(self, task_id: str, status: TaskStatus, 
                          result: Optional[Any] = None, error: Optional[str] = None):
        """Update task status.
        
        Args:
            task_id: Task identifier
            status: New status
            result: Task result if completed
            error: Error message if failed
        """
        for task in self.task_queue:
            if task["task_id"] == task_id:
                task["status"] = status.value
                task["updated_at"] = datetime.now().isoformat()
                
                if result is not None:
                    task["result"] = result
                if error is not None:
                    task["error"] = error
                
                # Move to appropriate list
                if status == TaskStatus.COMPLETED:
                    self.completed_tasks.append(task)
                    logger.info(f"Task completed: {task_id}")
                elif status == TaskStatus.FAILED:
                    self.failed_tasks.append(task)
                    logger.warning(f"Task failed: {task_id} - {error}")
                
                self._save_state()
                break
    
    def create_checkpoint(self, checkpoint_name: Optional[str] = None):
        """Create state checkpoint for recovery.
        
        Args:
            checkpoint_name: Optional checkpoint name
        """
        if checkpoint_name is None:
            checkpoint_name = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        checkpoint_file = self.checkpoint_dir / f"{checkpoint_name}.json"
        
        try:
            checkpoint_data = {
                "checkpoint_name": checkpoint_name,
                "timestamp": datetime.now().isoformat(),
                "current_state": self.current_state.value,
                "task_queue": self.task_queue,
                "completed_tasks": self.completed_tasks,
                "failed_tasks": self.failed_tasks,
                "execution_context": self.execution_context
            }
            
            with open(checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(checkpoint_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Checkpoint created: {checkpoint_name}")
            return checkpoint_name
        except Exception as e:
            logger.error(f"Error creating checkpoint: {e}")
            return None
    
    def restore_checkpoint(self, checkpoint_name: str) -> bool:
        """Restore state from checkpoint.
        
        Args:
            checkpoint_name: Checkpoint name
            
        Returns:
            True if successful
        """
        checkpoint_file = self.checkpoint_dir / f"{checkpoint_name}.json"
        
        if not checkpoint_file.exists():
            logger.error(f"Checkpoint not found: {checkpoint_name}")
            return False
        
        try:
            with open(checkpoint_file, 'r', encoding='utf-8') as f:
                checkpoint_data = json.load(f)
            
            self.current_state = AgentState(checkpoint_data["current_state"])
            self.task_queue = checkpoint_data["task_queue"]
            self.completed_tasks = checkpoint_data["completed_tasks"]
            self.failed_tasks = checkpoint_data["failed_tasks"]
            self.execution_context = checkpoint_data["execution_context"]
            
            self._save_state()
            logger.info(f"Checkpoint restored: {checkpoint_name}")
            return True
        except Exception as e:
            logger.error(f"Error restoring checkpoint: {e}")
            return False
    
    def list_checkpoints(self) -> List[str]:
        """List available checkpoints.
        
        Returns:
            List of checkpoint names
        """
        checkpoints = []
        for file in self.checkpoint_dir.glob("*.json"):
            checkpoints.append(file.stem)
        return sorted(checkpoints, reverse=True)
    
    def update_context(self, updates: Dict[str, Any]):
        """Update execution context.
        
        Args:
            updates: Context updates
        """
        self.execution_context.update(updates)
        self._save_state()
        logger.debug(f"Context updated: {list(updates.keys())}")
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """Get execution summary.
        
        Returns:
            Summary dictionary
        """
        total_tasks = len(self.task_queue)
        pending = sum(1 for t in self.task_queue if t["status"] == TaskStatus.PENDING.value)
        in_progress = sum(1 for t in self.task_queue if t["status"] == TaskStatus.IN_PROGRESS.value)
        completed = len(self.completed_tasks)
        failed = len(self.failed_tasks)
        
        return {
            "current_state": self.current_state.value,
            "total_tasks": total_tasks,
            "pending_tasks": pending,
            "in_progress_tasks": in_progress,
            "completed_tasks": completed,
            "failed_tasks": failed,
            "success_rate": completed / max(1, completed + failed),
            "execution_context": self.execution_context
        }
    
    def clear_completed_tasks(self):
        """Clear completed tasks from queue."""
        self.task_queue = [t for t in self.task_queue 
                          if t["status"] not in [TaskStatus.COMPLETED.value, TaskStatus.FAILED.value]]
        self._save_state()
        logger.info("Completed tasks cleared from queue")
    
    def reset(self):
        """Reset state manager."""
        self.current_state = AgentState.IDLE
        self.task_queue = []
        self.completed_tasks = []
        self.failed_tasks = []
        self.execution_context = {}
        self._save_state()
        logger.info("State manager reset")


def get_state_manager() -> StateManager:
    """Get global state manager instance.
    
    Returns:
        StateManager instance
    """
    global _state_manager
    if "_state_manager" not in globals():
        _state_manager = StateManager()
    return _state_manager
