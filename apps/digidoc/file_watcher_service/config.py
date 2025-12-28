"""
DigiDoc File Watcher Configuration
Configuration management for the file watcher service.
"""

import os
from pathlib import Path

# Base paths - all use ~/Dropbox/cloud_storage
CLOUD_STORAGE_BASE = os.path.expanduser('~/Dropbox/cloud_storage')
DIGIDOC_BASE = os.path.join(CLOUD_STORAGE_BASE, 'DigiDoc')

# Queue and data directories
QUEUE_DIRECTORY = os.environ.get(
    'DOCUMENT_QUEUE_PATH',
    os.path.expanduser('~/Dropbox/Application Data/DigiDoc/queue')
)
PROCESSING_DIRECTORY = os.path.join(DIGIDOC_BASE, 'Data', 'processing')
TENANT_LOGS_DIR = os.path.join(DIGIDOC_BASE, 'logs', 'tenants')

# DigiDoc service configuration
DIGIDOC_SERVICE_URL = os.environ.get('DIGIDOC_SERVICE_URL', 'http://127.0.0.1:5000')
DIGIDOC_API_BASE = f"{DIGIDOC_SERVICE_URL}/digidoc"  # All API endpoints use /digidoc/ prefix
CALLING_APP_ID = os.environ.get('CALLING_APP_ID', 'construction_suite')

# File extensions to watch
WATCHED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.pdf'}

# Logging configuration
LOG_DIR = os.path.join(DIGIDOC_BASE, 'logs')
LOG_FILE = os.path.join(LOG_DIR, 'file_watcher_digidoc.log')

# Health check configuration
HEALTH_CHECK_INTERVAL = 300  # 5 minutes
STALE_FILE_THRESHOLD = 3600  # 1 hour


def validate_config():
    """Validate configuration and create necessary directories."""
    directories = [
        QUEUE_DIRECTORY,
        PROCESSING_DIRECTORY,
        TENANT_LOGS_DIR,
        LOG_DIR,
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    return True


def get_config_summary():
    """Get configuration summary for logging."""
    return {
        'queue_directory': QUEUE_DIRECTORY,
        'digidoc_service_url': DIGIDOC_SERVICE_URL,
        'digidoc_api_base': DIGIDOC_API_BASE,
        'calling_app_id': CALLING_APP_ID,
        'log_file': LOG_FILE,
    }
