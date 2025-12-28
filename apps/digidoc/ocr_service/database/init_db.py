#!/usr/bin/env python3
"""
Initialize OCR App Database
Creates database tables for template caching.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ocr_service.database.models import init_database

if __name__ == "__main__":
    print("Initializing OCR app database...")
    engine = init_database()
    print("✓ Database initialized successfully")
    print(f"Database location: {engine.url}")
