#!/usr/bin/env python3
"""
RQ Worker Startup Script

Configures multiprocessing for macOS compatibility before starting RQ worker.
This prevents fork crashes when Objective-C runtime is initialized.

Usage:
    python3 -m ocr_service.queue.start_rq_worker
    # Or with queue name:
    python3 -m ocr_service.queue.start_rq_worker default
"""

# CRITICAL: Set environment variables BEFORE importing ANYTHING
# This must be the very first thing in the script
import os
import sys

# macOS fork safety: Allow forking when Objective-C runtime is initialized
# WARNING: This is a development workaround. For production, consider using Celery or a different queue system.
# Must be set before any imports that might trigger Objective-C runtime initialization
os.environ['OBJC_DISABLE_INITIALIZE_FORK_SAFETY'] = 'YES'

# Verify it's set
if os.environ.get('OBJC_DISABLE_INITIALIZE_FORK_SAFETY') != 'YES':
    print("ERROR: Failed to set OBJC_DISABLE_INITIALIZE_FORK_SAFETY", file=sys.stderr)
    sys.exit(1)

# Configure multiprocessing to use 'spawn' instead of 'fork' on macOS
# This prevents crashes when RQ worker forks processes with Objective-C runtime initialized
os.environ['MP_START_METHOD'] = 'spawn'

# Prevent PyArrow from initializing curl during fork (macOS security restriction)
os.environ.setdefault('ARROW_DISABLE_CURL', '1')

# Also set multiprocessing start method programmatically as backup
import multiprocessing
if hasattr(multiprocessing, 'set_start_method'):
    try:
        multiprocessing.set_start_method('spawn', force=True)
    except RuntimeError:
        # Already set, ignore
        pass

# Now import RQ components
from rq import Worker, Queue
from redis import Redis
from ..config import get_config

if __name__ == '__main__':
    # Get configuration
    config = get_config()
    redis_url = os.getenv('REDIS_URL') or os.getenv('DIGIDOC_QUEUE_REDIS_URL') or config.queue.redis_url
    
    # Create Redis connection
    conn = Redis.from_url(redis_url)
    
    # Get queue name from command line or use default
    queue_names = sys.argv[1:] if len(sys.argv) > 1 else ['default']
    
    # Create queues with connection
    queues = [Queue(name, connection=conn) for name in queue_names]
    
    # Create and start worker with connection
    print(f"Starting RQ worker on queues: {', '.join(queue_names)}")
    print(f"Redis URL: {redis_url}")
    print(f"OBJC_DISABLE_INITIALIZE_FORK_SAFETY: {os.environ.get('OBJC_DISABLE_INITIALIZE_FORK_SAFETY', 'NOT SET')}")
    print("Press Ctrl+C to stop\n")
    
    try:
        worker = Worker(queues, connection=conn)
        worker.work()
    except Exception as e:
        print(f"Worker error: {e}", file=sys.stderr)
        raise

