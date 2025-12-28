"""
Queue Adapter Abstract Base Class

Defines the interface for queue adapters (RQ, Celery, etc.)
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class TaskResult:
    """Unified task result object for all queue adapters."""
    task_id: str
    status: str
    message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class QueueAdapter(ABC):
    """Abstract base class for queue adapters."""
    
    @abstractmethod
    def enqueue(self, task_name: str, *args, **kwargs) -> TaskResult:
        """
        Enqueue a task for processing.
        
        Args:
            task_name: Name of the task function to execute
            *args: Positional arguments for the task
            **kwargs: Keyword arguments for the task
            
        Returns:
            TaskResult: Result object with task_id and status
        """
        pass
    
    @abstractmethod
    def enqueue_delayed(self, task_name: str, delay_seconds: int, *args, **kwargs) -> TaskResult:
        """
        Enqueue a task with a delay.
        
        Args:
            task_name: Name of the task function to execute
            delay_seconds: Number of seconds to delay execution
            *args: Positional arguments for the task
            **kwargs: Keyword arguments for the task
            
        Returns:
            TaskResult: Result object with task_id and status
        """
        pass
    
    @abstractmethod
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Get the status of a task.
        
        Args:
            task_id: ID of the task to check
            
        Returns:
            Dict with status information (status, result, error, etc.)
        """
        pass


def get_queue_adapter() -> QueueAdapter:
    """
    Factory function to get the configured queue adapter.
    
    Reads QUEUE_ADAPTER environment variable or config file to determine
    which adapter to use (rq or celery).
    
    Returns:
        QueueAdapter: Configured queue adapter instance
        
    Raises:
        ValueError: If adapter type is unknown
    """
    import os
    from ..config import get_config
    
    # Check environment variable first
    adapter_type = os.getenv('QUEUE_ADAPTER', '').lower()
    
    # If not in env, check config file
    if not adapter_type:
        config = get_config()
        adapter_type = config.queue.adapter.lower()
    
    # Default to RQ for MVP
    if not adapter_type:
        adapter_type = 'rq'
    
    # Import and return appropriate adapter
    if adapter_type == 'rq':
        from .rq_adapter import RQAdapter
        return RQAdapter()
    elif adapter_type == 'celery':
        from .celery_adapter import CeleryAdapter
        return CeleryAdapter()
    else:
        raise ValueError(f"Unknown queue adapter: {adapter_type}. Must be 'rq' or 'celery'")

