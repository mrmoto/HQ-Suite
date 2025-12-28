"""
Queue Abstraction Layer

Public API for queue operations. Provides unified interface for RQ (MVP) and Celery (production).
"""

from .queue_adapter import get_queue_adapter, QueueAdapter, TaskResult

__all__ = ['get_queue_adapter', 'QueueAdapter', 'TaskResult', 'enqueue_ocr_task']


def enqueue_ocr_task(task_name: str, *args, **kwargs):
    """
    Enqueue an OCR task using the configured queue adapter.
    
    This is the main public API for enqueueing tasks.
    
    Args:
        task_name: Name of the task function to execute
        *args: Positional arguments for the task
        **kwargs: Keyword arguments for the task
        
    Returns:
        TaskResult: Result object with task_id and status information
        
    Example:
        result = enqueue_ocr_task('process_document_task', file_path, queue_item_id, calling_app_id)
        print(f"Task enqueued with ID: {result.task_id}")
    """
    adapter = get_queue_adapter()
    return adapter.enqueue(task_name, *args, **kwargs)

