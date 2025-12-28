# Testing Skeleton End-to-End Flow

This guide walks through testing the complete skeleton workflow.

## Prerequisites

### 1. Install Dependencies

```bash
cd /Users/scottroberts/Library/CloudStorage/Dropbox/app_development/Construction_Suite/apps/digidoc
pip3 install -r requirements_ocr.txt
```

This installs:
- Flask (API server)
- RQ (Redis Queue)
- Redis Python client
- OpenCV, Pillow, etc.

### 2. Start Redis

**Option A: Using Homebrew (recommended)**
```bash
brew services start redis
```

**Option B: Manual start**
```bash
redis-server
```

**Verify Redis is running:**
```bash
python3 -c "import redis; r = redis.Redis.from_url('redis://localhost:6379/0'); r.ping(); print('Redis OK')"
```

### 3. Start RQ Worker

In a **separate terminal window**, start the RQ worker:

```bash
cd /Users/scottroberts/Library/CloudStorage/Dropbox/app_development/Construction_Suite/apps/digidoc
rq worker
```

You should see:
```
*** Listening for work on default...
```

**Keep this terminal open** - the worker needs to be running to process tasks.

### 4. Start API Server

In **another terminal window**, start the API server:

```bash
cd /Users/scottroberts/Library/CloudStorage/Dropbox/app_development/Construction_Suite/apps/digidoc
python3 -m ocr_service.api_server
```

You should see:
```
Starting OCR Service on port 8001
Debug mode: False
 * Running on http://127.0.0.1:8001
```

**Keep this terminal open** - the API server needs to be running.

## Testing the Flow

### Option 1: Using the Test Script

```bash
cd /Users/scottroberts/Library/CloudStorage/Dropbox/app_development/Construction_Suite/development
python3 test_skeleton_flow.py ~/Dropbox/Application\ Data/DigiDoc/queue/Scan2025-12-18_133624_000.png
```

### Option 2: Manual Testing with curl

#### Step 1: Enqueue a Document

```bash
curl -X POST http://127.0.0.1:8001/api/digidoc/queue \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "/Users/scottroberts/Dropbox/Application Data/DigiDoc/queue/Scan2025-12-18_133624_000.png",
    "calling_app_id": "test_app"
  }'
```

**Expected Response:**
```json
{
  "task_id": "abc123-def456-...",
  "queue_item_id": "xyz789-...",
  "status": "queued",
  "message": "Task 'process_receipt_task' enqueued successfully"
}
```

**Save the `task_id`** from the response.

#### Step 2: Check Task Status

```bash
curl http://127.0.0.1:8001/api/digidoc/status/<task_id>
```

Replace `<task_id>` with the task_id from Step 1.

**Expected Response (while processing):**
```json
{
  "task_id": "abc123-def456-...",
  "status": "started",
  "created_at": "2025-12-24T...",
  "started_at": "2025-12-24T..."
}
```

**Expected Response (when complete):**
```json
{
  "task_id": "abc123-def456-...",
  "status": "completed",
  "result": {
    "status": "completed",
    "confidence": 0.85,
    "template_matched": "mock_template",
    "extracted_fields": {
      "total": "0.00",
      "date": "2025-12-23",
      "vendor": "Mock Vendor"
    },
    "queue_item_id": "xyz789-...",
    "preprocessed_path": "...",
    "original_path": "...",
    "comparison_path": "...",
    "skeleton_mode": true
  }
}
```

#### Step 3: Visual Verification

The workflow will **pause** during processing for visual verification. You should see in the RQ worker terminal:

```
PREPROCESSING VISUAL VERIFICATION
============================================================
Original image: /path/to/original.png
Preprocessed image: /path/to/preprocessed.png
Comparison image: /path/to/preprocessing_comparison.png

Please review the preprocessing results.
Press Enter to continue processing...
```

**Review the images**, then press Enter in the RQ worker terminal to continue.

#### Step 4: Verify Files Created

Check the queue item directory:

```bash
ls -la ~/Dropbox/Application\ Data/DigiDoc/queue/<queue_item_id>/
```

You should see:
- `original.png` - Original image
- `preprocessed.png` - Preprocessed image
- `preprocessing_comparison.png` - Side-by-side comparison

## Expected Behavior

### Skeleton Mode Features

1. **Visual Verification**: Workflow pauses after preprocessing for review
2. **Mock Values**: Uses values from `Construction_Suite/development/skeleton.yaml`
3. **Comparison Image**: Creates side-by-side before/after image
4. **Skeleton Flag**: Results include `"skeleton_mode": true`

### What to Verify

1. ✅ Task enqueues successfully
2. ✅ RQ worker picks up the task
3. ✅ Preprocessing runs and saves images
4. ✅ Visual verification pause occurs
5. ✅ Comparison image is created
6. ✅ Task completes with skeleton mode results
7. ✅ All files saved to queue item directory

## Troubleshooting

### Redis Connection Error

**Error**: `ConnectionError: Error connecting to Redis`

**Solution**: 
- Ensure Redis is running: `brew services list | grep redis`
- Start Redis: `brew services start redis`

### RQ Worker Not Processing

**Error**: Tasks stay in "queued" status

**Solution**:
- Ensure RQ worker is running: Check the terminal where you ran `rq worker`
- Check worker logs for errors
- Verify Redis connection: `redis-cli ping` (if redis-cli is installed)

### API Server Not Starting

**Error**: `Address already in use`

**Solution**:
- Port 8001 is already in use
- Change port: `export DIGIDOC_API_PORT=8002`
- Or stop the process using port 8001

### Import Errors

**Error**: `ModuleNotFoundError: No module named 'ocr_service'`

**Solution**:
- Ensure you're in the correct directory: `apps/digidoc/`
- Install dependencies: `pip3 install -r requirements_ocr.txt`
- Use Python path: `PYTHONPATH=. python3 -m ocr_service.api_server`

### Visual Verification Not Pausing

**Check**:
- `Construction_Suite/development/skeleton.yaml` exists
- `preprocessing.visual_verification.enabled` is `true`
- RQ worker terminal is visible (pause happens there, not API server)

## Next Steps After Testing

Once skeleton flow is verified:

1. Review preprocessing results in comparison image
2. Adjust preprocessing parameters in `digidoc_config.yaml` if needed
3. Test with multiple documents
4. Move to Phase 2: Replace mocks with real implementations

