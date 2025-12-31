"""
Task Store - In-memory task management for async operations.
Tracks task status, progress, and results without external infrastructure.
100% local - no Redis or external services required.
"""
import threading
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional, Dict
import logging

from config import TASK_RESULT_TTL, TASK_CLEANUP_INTERVAL

logger = logging.getLogger(__name__)


class TaskStatus(str, Enum):
    """Task execution states."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Task:
    """Represents a background task with its state and results."""
    id: str
    task_type: str
    status: TaskStatus = TaskStatus.PENDING
    progress: int = 0  # 0-100
    message: str = ""
    result: Optional[Any] = None
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        """Convert task to dictionary for API response."""
        return {
            "id": self.id,
            "task_type": self.task_type,
            "status": self.status.value,
            "progress": self.progress,
            "message": self.message,
            "error": self.error,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "has_result": self.result is not None,
        }


class TaskStore:
    """
    Thread-safe in-memory task storage.
    Manages task lifecycle without external dependencies.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Singleton pattern for shared task store."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._tasks: Dict[str, Task] = {}
        self._task_lock = threading.Lock()
        self._initialized = True
        
        # Start cleanup thread
        self._start_cleanup_thread()
        logger.info("TaskStore initialized (in-memory, local-only)")
    
    def _start_cleanup_thread(self):
        """Start background thread to clean up old tasks."""
        def cleanup_loop():
            while True:
                time.sleep(TASK_CLEANUP_INTERVAL)
                self._cleanup_old_tasks()
        
        cleanup_thread = threading.Thread(target=cleanup_loop, daemon=True)
        cleanup_thread.start()
    
    def _cleanup_old_tasks(self):
        """Remove completed tasks older than TTL."""
        now = datetime.now()
        with self._task_lock:
            tasks_to_remove = []
            for task_id, task in self._tasks.items():
                if task.status in (TaskStatus.COMPLETED, TaskStatus.FAILED):
                    if task.completed_at:
                        age_seconds = (now - task.completed_at).total_seconds()
                        if age_seconds > TASK_RESULT_TTL:
                            tasks_to_remove.append(task_id)
            
            for task_id in tasks_to_remove:
                del self._tasks[task_id]
            
            if tasks_to_remove:
                logger.info(f"Cleaned up {len(tasks_to_remove)} old tasks")
    
    def create_task(self, task_type: str) -> Task:
        """Create a new task and return it."""
        task_id = str(uuid.uuid4())
        task = Task(id=task_id, task_type=task_type)
        
        with self._task_lock:
            self._tasks[task_id] = task
        
        logger.info(f"Created task {task_id} of type {task_type}")
        return task
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID."""
        with self._task_lock:
            return self._tasks.get(task_id)
    
    def update_progress(self, task_id: str, progress: int, message: str = ""):
        """Update task progress (0-100)."""
        with self._task_lock:
            task = self._tasks.get(task_id)
            if task:
                task.status = TaskStatus.IN_PROGRESS
                task.progress = min(100, max(0, progress))
                task.message = message
                task.updated_at = datetime.now()
    
    def complete_task(self, task_id: str, result: Any):
        """Mark task as completed with result."""
        with self._task_lock:
            task = self._tasks.get(task_id)
            if task:
                task.status = TaskStatus.COMPLETED
                task.progress = 100
                task.message = "Completed"
                task.result = result
                task.updated_at = datetime.now()
                task.completed_at = datetime.now()
                logger.info(f"Task {task_id} completed successfully")
    
    def fail_task(self, task_id: str, error: str):
        """Mark task as failed with error message."""
        with self._task_lock:
            task = self._tasks.get(task_id)
            if task:
                task.status = TaskStatus.FAILED
                task.error = error
                task.message = f"Failed: {error}"
                task.updated_at = datetime.now()
                task.completed_at = datetime.now()
                logger.error(f"Task {task_id} failed: {error}")
    
    def get_task_result(self, task_id: str) -> Optional[Any]:
        """Get the result of a completed task."""
        with self._task_lock:
            task = self._tasks.get(task_id)
            if task and task.status == TaskStatus.COMPLETED:
                return task.result
        return None
    
    def list_tasks(self, limit: int = 50) -> list[dict]:
        """List recent tasks."""
        with self._task_lock:
            tasks = sorted(
                self._tasks.values(), 
                key=lambda t: t.created_at, 
                reverse=True
            )[:limit]
            return [t.to_dict() for t in tasks]
    
    def get_active_task_count(self) -> int:
        """Get count of pending/in_progress tasks."""
        with self._task_lock:
            return sum(
                1 for t in self._tasks.values() 
                if t.status in (TaskStatus.PENDING, TaskStatus.IN_PROGRESS)
            )


# Global singleton instance
task_store = TaskStore()

