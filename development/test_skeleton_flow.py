#!/usr/bin/env python3
"""
Test Skeleton End-to-End Flow

Tests the complete skeleton workflow:
1. API endpoint to enqueue document
2. Queue processing
3. Status checking
4. Visual verification

Usage:
    python3 test_skeleton_flow.py <image_path>
"""

import sys
import os
import time
import requests
import json
from pathlib import Path

# Add ocr_service to path (from Construction_Suite/development/ to apps/digidoc/ocr_service)
digidoc_dir = Path(__file__).parent.parent / 'apps' / 'digidoc'
sys.path.insert(0, str(digidoc_dir / 'ocr_service'))

# Configuration
API_BASE_URL = os.getenv('DIGIDOC_API_URL', 'http://127.0.0.1:8001')
TEST_IMAGE = sys.argv[1] if len(sys.argv) > 1 else None
CALLING_APP_ID = 'test_app'


def check_redis():
    """Check if Redis is available."""
    try:
        import redis
        r = redis.Redis.from_url('redis://localhost:6379/0')
        r.ping()
        print("✓ Redis is running")
        return True
    except Exception as e:
        print(f"✗ Redis is not available: {e}")
        print("\nTo start Redis:")
        print("  brew services start redis")
        print("  OR")
        print("  redis-server")
        return False


def check_api_server():
    """Check if API server is running."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=2)
        if response.status_code == 200:
            print("✓ API server is running")
            return True
        else:
            print(f"✗ API server returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"✗ API server is not running at {API_BASE_URL}")
        print("\nTo start the API server:")
        print("  cd apps/digidoc")
        print("  python3 -m ocr_service.api_server")
        return False
    except Exception as e:
        print(f"✗ Error checking API server: {e}")
        return False


def test_enqueue(image_path: str):
    """Test enqueueing a document."""
    print("\n" + "=" * 60)
    print("Step 1: Enqueue Document")
    print("=" * 60)
    
    if not os.path.exists(image_path):
        print(f"✗ Image not found: {image_path}")
        return None
    
    print(f"Enqueueing: {image_path}")
    
    payload = {
        'file_path': image_path,
        'calling_app_id': CALLING_APP_ID
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/digidoc/queue",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 202:
            data = response.json()
            print(f"✓ Document enqueued successfully")
            print(f"  Task ID: {data.get('task_id')}")
            print(f"  Queue Item ID: {data.get('queue_item_id')}")
            print(f"  Status: {data.get('status')}")
            return data.get('task_id')
        else:
            print(f"✗ Enqueue failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return None
    except Exception as e:
        print(f"✗ Error enqueueing: {e}")
        return None


def test_status(task_id: str, max_wait: int = 60):
    """Test checking task status."""
    print("\n" + "=" * 60)
    print("Step 2: Check Task Status")
    print("=" * 60)
    
    print(f"Task ID: {task_id}")
    print("Waiting for task to complete...")
    
    start_time = time.time()
    last_status = None
    
    while time.time() - start_time < max_wait:
        try:
            response = requests.get(
                f"{API_BASE_URL}/api/digidoc/status/{task_id}",
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                status = data.get('status')
                
                # Only print if status changed
                if status != last_status:
                    print(f"  Status: {status}")
                    last_status = status
                
                if status == 'completed':
                    print("\n✓ Task completed successfully!")
                    print(f"  Result: {json.dumps(data.get('result', {}), indent=2)}")
                    return data
                elif status == 'failed':
                    print(f"\n✗ Task failed")
                    print(f"  Error: {data.get('error', 'Unknown error')}")
                    return data
                elif status in ['queued', 'started']:
                    # Still processing
                    time.sleep(2)
                    continue
                else:
                    print(f"  Unknown status: {status}")
                    time.sleep(2)
                    continue
            else:
                print(f"✗ Status check failed: {response.status_code}")
                print(f"  Response: {response.text}")
                return None
        except Exception as e:
            print(f"✗ Error checking status: {e}")
            time.sleep(2)
            continue
    
    print(f"\n✗ Task did not complete within {max_wait} seconds")
    return None


def verify_files(queue_item_id: str):
    """Verify that files were created correctly."""
    print("\n" + "=" * 60)
    print("Step 3: Verify Files Created")
    print("=" * 60)
    
    # Import from digidoc app
    import sys
    digidoc_dir = Path(__file__).parent.parent / 'apps' / 'digidoc'
    sys.path.insert(0, str(digidoc_dir))
    
    from ocr_service.config import get_config
    config = get_config()
    storage_base = config.paths.storage_base
    queue_dir = Path(storage_base) / 'queue' / queue_item_id
    
    print(f"Queue item directory: {queue_dir}")
    
    if not queue_dir.exists():
        print(f"✗ Queue item directory does not exist")
        return False
    
    files_found = []
    expected_files = ['original.png', 'preprocessed.png', 'preprocessing_comparison.png']
    
    for file in queue_dir.iterdir():
        if file.is_file():
            files_found.append(file.name)
            print(f"  ✓ {file.name}")
    
    for expected in expected_files:
        if expected not in files_found:
            print(f"  ✗ Missing: {expected}")
    
    if 'preprocessing_comparison.png' in files_found:
        print(f"\n✓ Visual verification image created: {queue_dir / 'preprocessing_comparison.png'}")
        print("  You can review this image to verify preprocessing results.")
    
    return True


def main():
    """Main test function."""
    print("=" * 60)
    print("DigiDoc Skeleton End-to-End Flow Test")
    print("=" * 60)
    
    # Check prerequisites
    if not check_redis():
        sys.exit(1)
    
    if not check_api_server():
        sys.exit(1)
    
    # Get test image
    if not TEST_IMAGE:
        # Use first available image from queue
        queue_dir = Path.home() / 'Dropbox' / 'Application Data' / 'DigiDoc' / 'queue'
        images = list(queue_dir.glob('*.png'))
        if images:
            test_image = str(images[0])
            print(f"\nUsing test image: {test_image}")
        else:
            print("\n✗ No test image provided and none found in queue directory")
            print("Usage: python3 test_skeleton_flow.py <image_path>")
            sys.exit(1)
    else:
        test_image = TEST_IMAGE
    
    # Test workflow
    task_id = test_enqueue(test_image)
    if not task_id:
        sys.exit(1)
    
    result = test_status(task_id)
    if not result:
        sys.exit(1)
    
    # Extract queue_item_id from result
    queue_item_id = result.get('result', {}).get('queue_item_id')
    if not queue_item_id:
        # Try to get from task metadata
        queue_item_id = result.get('result', {}).get('queue_item_id', 'unknown')
    
    verify_files(queue_item_id)
    
    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Review the preprocessing_comparison.png image")
    print("2. Check the queue item directory for all generated files")
    print("3. Verify the task result matches expected skeleton output")


if __name__ == '__main__':
    main()

