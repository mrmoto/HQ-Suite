#!/usr/bin/env python3
"""
DigiDoc File Watcher Service
Separate service that watches for ready_*.png files and calls DigiDoc API.
Uses macOS FSEvents for file system monitoring.
"""

import os
import sys
import time
import requests
import socket
import logging
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

# Import configuration
sys.path.insert(0, os.path.dirname(__file__))
from config import (
    QUEUE_DIRECTORY,
    DIGIDOC_API_BASE,
    CALLING_APP_ID,
    WATCHED_EXTENSIONS,
    LOG_FILE,
    validate_config,
    get_config_summary
)

# Processing state
processed_files = set()
processing_lock = {}

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('digidoc_filewatcher')


class ReadyFileHandler(FileSystemEventHandler):
    """Handle file system events for ready_*.png files."""
    
    def __init__(self):
        self.digidoc_api_base = DIGIDOC_API_BASE
        self.calling_app_id = CALLING_APP_ID
    
    def on_created(self, event: FileSystemEvent):
        """Called when a new file is created."""
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        
        # Only process files starting with "ready_"
        if not file_path.name.startswith('ready_'):
            return
        
        # Only process image/PDF files
        if file_path.suffix.lower() not in WATCHED_EXTENSIONS:
            return
        
        # Wait a moment for file to be fully written
        time.sleep(1)
        
        # Process the file
        self.process_ready_file(file_path)
    
    def process_ready_file(self, file_path: Path):
        """Process a ready_*.png file by calling OCR app API."""
        if file_path.name in processed_files:
            print(f"Skipping already processed: {file_path.name}")
            return
        
        if file_path.name in processing_lock:
            print(f"File already being processed: {file_path.name}")
            return
        
        # Lock file
        processing_lock[file_path.name] = True
        
        try:
            print(f"\n{'='*60}")
            print(f"Processing ready file: {file_path.name}")
            print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*60}")
            
            # Verify file exists and is readable
            if not file_path.exists():
                print(f"File does not exist: {file_path}")
                return
            
            # Call DigiDoc API
            result = self.call_digidoc_service(str(file_path))
            
            if result:
                processed_files.add(file_path.name)
                print(f"✓ Successfully processed: {file_path.name}")
            else:
                print(f"✗ Failed to process: {file_path.name}")
                
        except Exception as e:
            print(f"Error processing {file_path.name}: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # Release lock
            processing_lock.pop(file_path.name, None)
    
    def call_digidoc_service(self, file_path: str) -> bool:
        """
        Call DigiDoc API to process document.
        
        Args:
            file_path: Path to ready file
            
        Returns:
            True if successful
        """
        try:
            url = f"{self.digidoc_api_base}/process"
            
            # Prepare request data
            data = {
                'calling_app_id': self.calling_app_id,
                'context': {
                    'document_type': None,  # Unknown - will be determined
                    'vendor': None,  # Unknown - will be determined
                    'format_name': None,  # Unknown - will be determined
                }
            }
            
            # For file_path, we can send it as JSON
            data['file_path'] = file_path
            
            logger.info(f"Calling DigiDoc service: {url}")
            response = requests.post(
                url,
                json=data,
                timeout=120  # 2 minute timeout for DigiDoc processing
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✓ DigiDoc processing completed")
                logger.info(f"  Document type: {result.get('document_type', 'unknown')}")
                logger.info(f"  Requires review: {result.get('requires_review', False)}")
                logger.info(f"  Review type: {result.get('review_type', 'none')}")
                return True
            else:
                logger.error(f"✗ DigiDoc service error: {response.status_code}")
                logger.error(f"  Response: {response.text}")
                return False
                
        except requests.exceptions.ConnectionError:
            logger.error(f"Cannot connect to DigiDoc service at {self.digidoc_api_base}")
            logger.error("Is the DigiDoc service running?")
            return False
        except Exception as e:
            logger.error(f"Error calling DigiDoc service: {e}")
            return False


def scan_directory_for_errors():
    """
    Periodically scan directory for errors, omissions, and edge cases.
    """
    queue_path = Path(QUEUE_DIRECTORY)
    
    if not queue_path.exists():
        logger.warning(f"Queue directory does not exist: {QUEUE_DIRECTORY}")
        return
    
    # Find files that should have been processed
    ready_files = list(queue_path.glob('ready_*'))
    orphaned_files = []
    stale_files = []
    
    for file_path in ready_files:
        # Check if file is orphaned (not in processed list but old)
        if file_path.name not in processed_files:
            file_age = time.time() - file_path.stat().st_mtime
            if file_age > 3600:  # Older than 1 hour
                stale_files.append(file_path)
            elif file_age > 300:  # Older than 5 minutes
                orphaned_files.append(file_path)
    
    if orphaned_files:
        logger.warning(f"\n⚠ Found {len(orphaned_files)} orphaned ready files:")
        for file_path in orphaned_files:
            logger.warning(f"  - {file_path.name}")
    
    if stale_files:
        logger.warning(f"\n⚠ Found {len(stale_files)} stale ready files (>1 hour old):")
        for file_path in stale_files:
            logger.warning(f"  - {file_path.name}")
            # Could auto-retry or move to error folder


def check_digidoc_service_health() -> bool:
    """Check if DigiDoc service is accessible."""
    try:
        response = requests.get(f"{DIGIDOC_API_BASE}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def main():
    """Main watcher loop."""
    # Validate and setup configuration
    validate_config()
    config = get_config_summary()
    
    logger.info("="*60)
    logger.info("DigiDoc File Watcher Service")
    logger.info("="*60)
    logger.info(f"Hostname: {socket.gethostname()}")
    logger.info(f"Queue Directory: {config['queue_directory']}")
    logger.info(f"DigiDoc Service URL: {config['digidoc_service_url']}")
    logger.info(f"DigiDoc API Base: {config['digidoc_api_base']}")
    logger.info(f"Calling App ID: {config['calling_app_id']}")
    logger.info("="*60)
    
    # Check DigiDoc service health
    if not check_digidoc_service_health():
        logger.warning(f"DigiDoc service not accessible at {config['digidoc_api_base']}")
        logger.warning("Make sure DigiDoc service is running")
        logger.warning("Continuing anyway...")
    else:
        logger.info("✓ DigiDoc service is accessible")
    
    # Ensure queue directory exists
    queue_path = Path(QUEUE_DIRECTORY)
    queue_path.mkdir(parents=True, exist_ok=True)
    
    # Set up file watcher
    event_handler = ReadyFileHandler()
    observer = Observer()
    observer.schedule(event_handler, str(queue_path), recursive=False)
    observer.start()
    
    logger.info(f"\n👀 Watching: {config['queue_directory']}")
    logger.info("Looking for files starting with 'ready_'")
    logger.info("Press Ctrl+C to stop\n")
    
    try:
        last_scan = time.time()
        while True:
            time.sleep(1)
            
            # Periodic directory scan (every 5 minutes)
            if time.time() - last_scan > 300:
                scan_directory_for_errors()
                last_scan = time.time()
                
    except KeyboardInterrupt:
        logger.info("\n\nStopping watcher...")
        observer.stop()
    
    observer.join()
    logger.info("Watcher stopped.")


if __name__ == "__main__":
    main()
