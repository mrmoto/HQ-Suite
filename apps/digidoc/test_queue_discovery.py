#!/usr/bin/env python3
"""
Test script to trigger queue discovery and generate debug logs.

This script calls list_queue_items() to see what files are found in the queue directory.
"""

import sys
import os
from pathlib import Path

# Add ocr_service to path
digidoc_root = Path(__file__).parent
sys.path.insert(0, str(digidoc_root))

from ocr_service.gui.utils.queue_utils import list_queue_items
from ocr_service.config import get_config

def main():
    print("=" * 80)
    print("Testing Queue Discovery")
    print("=" * 80)
    
    # Get config
    config = get_config()
    queue_dir = config.paths.queue_directory
    
    print(f"\nQueue Directory: {queue_dir}")
    print(f"Exists: {os.path.exists(queue_dir)}")
    
    if os.path.exists(queue_dir):
        all_items = os.listdir(queue_dir)
        dirs = [item for item in all_items if os.path.isdir(os.path.join(queue_dir, item))]
        files = [item for item in all_items if os.path.isfile(os.path.join(queue_dir, item))]
        
        print(f"\nDirectory Contents:")
        print(f"  Total items: {len(all_items)}")
        print(f"  Directories: {len(dirs)}")
        print(f"  Files: {len(files)}")
        
        if files:
            print(f"\n  Sample files (first 5):")
            for f in files[:5]:
                print(f"    - {f}")
    
    print("\n" + "=" * 80)
    print("Calling list_queue_items()...")
    print("=" * 80)
    
    # This will trigger the instrumented code
    queue_items = list_queue_items()
    
    print(f"\nFound {len(queue_items)} queue items")
    
    if queue_items:
        print("\nQueue Items:")
        for item in queue_items[:5]:  # Show first 5
            print(f"  - {item.get('queue_item_id', 'unknown')}: {item.get('status', 'unknown')}")
    else:
        print("\n⚠️  No queue items found!")
        print("   This suggests the code is only looking for subdirectories,")
        print("   but your images are loose files in the queue directory.")
    
    print("\n" + "=" * 80)
    print("Check debug.log for detailed instrumentation logs")
    print("=" * 80)

if __name__ == '__main__':
    main()

