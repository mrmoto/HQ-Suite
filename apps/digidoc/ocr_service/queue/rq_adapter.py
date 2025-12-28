"""
RQ (Redis Queue) Adapter Implementation

MVP queue adapter using RQ for async task processing.
"""

import os
from typing import Dict, Any, Optional
from redis import Redis
from rq import Queue
from rq.job import Job, JobStatus

from .queue_adapter import QueueAdapter, TaskResult
from ..config import get_config


class RQAdapter(QueueAdapter):
    """RQ (Redis Queue) implementation of QueueAdapter."""
    
    def __init__(self):
        """Initialize RQ adapter with Redis connection."""
        config = get_config()
        
        # Get Redis URL from environment or config
        redis_url = os.getenv('REDIS_URL') or os.getenv('DIGIDOC_QUEUE_REDIS_URL')
        if not redis_url:
            redis_url = config.queue.redis_url
        
        # Parse Redis URL and create connection
        self.redis_conn = Redis.from_url(redis_url)
        
        # Create default queue
        self.queue = Queue(connection=self.redis_conn)
        
        # Get job timeout from config
        self.job_timeout = config.queue.job_timeout
    
    def enqueue(self, task_name: str, *args, **kwargs) -> TaskResult:
        """
        Enqueue a task using RQ.
        
        Args:
            task_name: Name of the task function (must be importable)
            *args: Positional arguments for the task
            **kwargs: Keyword arguments for the task
            
        Returns:
            TaskResult: Result object with task_id and status
        """
        # Import task function dynamically
        # Task functions should be in ocr_service.tasks module
        from importlib import import_module
        
        # Parse task_name (e.g., 'process_document_task' or 'tasks.document_tasks.process_document_task')
        if '.' in task_name:
            module_path, func_name = task_name.rsplit('.', 1)
        else:
            # Default to tasks.document_tasks module
            module_path = 'ocr_service.tasks.document_tasks'
            func_name = task_name
        
        try:
            # Import the module (no reload - reload causes crashes with circular imports)
            module = import_module(module_path)
            task_func = getattr(module, func_name)
            
            # #region agent log
            import json
            from datetime import datetime
            log_data = {
                "sessionId": "debug-session",
                "runId": "run3",
                "hypothesisId": "C",
                "location": "rq_adapter.py:64",
                "message": "function imported",
                "data": {
                    "task_name": task_name,
                    "module_path": module_path,
                    "func_name": func_name,
                    "func_module": task_func.__module__,
                    "func_qualname": task_func.__qualname__,
                    "func_name_attr": task_func.__name__
                },
                "timestamp": int(datetime.now().timestamp() * 1000)
            }
            try:
                with open("/Users/scottroberts/Library/CloudStorage/Dropbox/app_development/Construction_Suite/.cursor/debug.log", "a") as f:
                    f.write(json.dumps(log_data) + "\n")
            except: pass
            # #endregion
            
        except (ImportError, AttributeError) as e:
            raise ValueError(f"Could not import task function '{task_name}': {e}")
        
        # #region agent log
        log_data = {
            "sessionId": "debug-session",
            "runId": "run3",
            "hypothesisId": "C",
            "location": "rq_adapter.py:85",
            "message": "about to enqueue",
            "data": {
                "func_module": task_func.__module__,
                "func_name": task_func.__name__,
                "func_qualname": task_func.__qualname__
            },
            "timestamp": int(datetime.now().timestamp() * 1000)
        }
        try:
            with open("/Users/scottroberts/Library/CloudStorage/Dropbox/app_development/Construction_Suite/.cursor/debug.log", "a") as f:
                f.write(json.dumps(log_data) + "\n")
        except: pass
        # #endregion
        
        # Enqueue the task - RQ will serialize using function's __module__ and __qualname__
        # We import fresh each time to avoid cached references
        job = self.queue.enqueue(
            task_func,
            *args,
            **kwargs,
            job_timeout=self.job_timeout
        )
        
        # #region agent log
        log_data = {
            "sessionId": "debug-session",
            "runId": "run3",
            "hypothesisId": "C",
            "location": "rq_adapter.py:95",
            "message": "job enqueued",
            "data": {
                "job_id": job.id,
                "job_func_name": job.func_name if hasattr(job, 'func_name') else None
            },
            "timestamp": int(datetime.now().timestamp() * 1000)
        }
        try:
            with open("/Users/scottroberts/Library/CloudStorage/Dropbox/app_development/Construction_Suite/.cursor/debug.log", "a") as f:
                f.write(json.dumps(log_data) + "\n")
        except: pass
        # #endregion
        
        return TaskResult(
            task_id=job.id,
            status='queued',
            message=f"Task '{task_name}' enqueued successfully",
            metadata={'queue_name': self.queue.name}
        )
    
    def enqueue_delayed(self, task_name: str, delay_seconds: int, *args, **kwargs) -> TaskResult:
        """
        Enqueue a task with a delay using RQ.
        
        Args:
            task_name: Name of the task function
            delay_seconds: Number of seconds to delay execution
            *args: Positional arguments for the task
            **kwargs: Keyword arguments for the task
            
        Returns:
            TaskResult: Result object with task_id and status
        """
        # Import task function dynamically
        from importlib import import_module
        
        if '.' in task_name:
            module_path, func_name = task_name.rsplit('.', 1)
        else:
            module_path = 'ocr_service.tasks.document_tasks'
            func_name = task_name
        
        try:
            module = import_module(module_path)
            task_func = getattr(module, func_name)
        except (ImportError, AttributeError) as e:
            raise ValueError(f"Could not import task function '{task_name}': {e}")
        
        # Enqueue with delay using function path string
        func_path = f"{module_path}.{func_name}"
        job = self.queue.enqueue_in(
            delay_seconds,
            func_path,
            *args,
            **kwargs,
            job_timeout=self.job_timeout
        )
        
        return TaskResult(
            task_id=job.id,
            status='scheduled',
            message=f"Task '{task_name}' scheduled for {delay_seconds} seconds",
            metadata={'queue_name': self.queue.name, 'delay_seconds': delay_seconds}
        )
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Get the status of an RQ task.
        
        Args:
            task_id: RQ job ID
            
        Returns:
            Dict with status information
        """
        try:
            job = Job.fetch(task_id, connection=self.redis_conn)
            
            # Map RQ job status to our status format
            status_map = {
                JobStatus.QUEUED: 'queued',
                JobStatus.STARTED: 'started',
                JobStatus.FINISHED: 'completed',
                JobStatus.FAILED: 'failed',
                JobStatus.DEFERRED: 'deferred',
                JobStatus.SCHEDULED: 'scheduled',
            }
            
            status = status_map.get(job.get_status(), 'unknown')
            
            result = {
                'task_id': task_id,
                'status': status,
                'created_at': job.created_at.isoformat() if job.created_at else None,
                'started_at': job.started_at.isoformat() if job.started_at else None,
                'ended_at': job.ended_at.isoformat() if job.ended_at else None,
            }
            
            # Add result if completed
            if status == 'completed':
                result['result'] = job.result
            elif status == 'failed':
                result['error'] = str(job.exc_info) if job.exc_info else 'Unknown error'
            
            return result
            
        except Exception as e:
            return {
                'task_id': task_id,
                'status': 'error',
                'error': str(e)
            }

