# End-to-End Testing Guide

**Purpose**: Test the complete extraction pipeline with real document images  
**Steps**: 1-4 from extraction testing workflow

---

## Prerequisites

- Redis server installed and running
- Python virtual environment activated (`.venv` in digidoc directory)
- Dependencies installed: `pip install -r requirements_ocr.txt`
- Test document image available

---

## Step 1: Start Redis Server

**Check if Redis is running:**
```bash
redis-cli ping
```

If you see `PONG`, Redis is already running. Skip to Step 2.

**If Redis is not running, start it:**

**macOS (Homebrew):**
```bash
brew services start redis
```

**Or run manually:**
```bash
redis-server
```

**Verify Redis is running:**
```bash
redis-cli ping
# Should return: PONG
```

---

## Step 2: Start RQ Worker

**Open a new terminal window/tab** (keep Redis running in the first terminal)

**Navigate to digidoc directory:**
```bash
cd /Users/scottroberts/Library/CloudStorage/Dropbox/app_development/Construction_Suite/apps/digidoc
```

**Activate virtual environment** (if not using direnv):
```bash
source .venv/bin/activate
```

**Start RQ worker:**
```bash
rq worker
```

You should see output like:
```
12:34:56 Worker rq:worker:... started, version 1.x.x
12:34:56 Listening on default
12:34:56 *** Listening on default...
```

**Keep this terminal open** - the worker needs to stay running.

---

## Step 3: Start API Server

**Open another new terminal window/tab** (keep Redis and RQ worker running)

**Navigate to digidoc directory:**
```bash
cd /Users/scottroberts/Library/CloudStorage/Dropbox/app_development/Construction_Suite/apps/digidoc
```

**Activate virtual environment** (if not using direnv):
```bash
source .venv/bin/activate
```

**Start API server:**
```bash
python3 -m ocr_service.api_server
```

Or use the script:
```bash
./ocr_service/run_server.sh
```

You should see output like:
```
 * Running on http://127.0.0.1:8001
 * Press CTRL+C to quit
```

**Keep this terminal open** - the API server needs to stay running.

**Verify API is running:**
```bash
curl http://localhost:8001/health
```

Should return a JSON response with status.

---

## Step 4: Test with Real Document Image

**Find a test document image:**
- Look in `apps/hq/receipt_samples/images/` (if any exist)
- Or use any document image you have
- **Important**: Use absolute path to the image file

**Test via API endpoint:**

**Option A: Using curl**
```bash
curl -X POST http://localhost:8001/api/digidoc/queue \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "/absolute/path/to/your/document.png",
    "calling_app_id": "test_app"
  }'
```

**Example response:**
```json
{
  "task_id": "abc123-def456-...",
  "status": "queued",
  "message": "Task 'process_document_task' enqueued successfully"
}
```

**Save the `task_id` from the response.**

**Check task status:**
```bash
curl http://localhost:8001/api/digidoc/status/<task_id>
```

**Watch the RQ worker terminal** - you should see processing activity:
```
12:34:56 default: ocr_service.tasks.document_tasks.process_document_task(...)
12:34:57 Processing document: /path/to/document.png
12:34:58 Preprocessing complete
12:34:59 Template matching complete
12:35:00 Extraction complete
```

**When status is "completed", check the result:**
```bash
curl http://localhost:8001/api/digidoc/status/<task_id>
```

**Option B: Using Python script (semi-automated)**
```bash
cd apps/digidoc
python3 tests/integration/test_extraction_accuracy.py \
  --document "/absolute/path/to/your/document.png" \
  --use-queue
```

This will:
- Enqueue the document
- Wait for processing
- Display extraction results
- Save extracted fields to JSON (if configured)

---

## Expected Results

**Successful processing should return:**
```json
{
  "status": "completed",
  "confidence": 0.85,
  "template_matched": "mead_clark_format1",
  "extracted_fields": {
    "receipt_date": "2025-12-15",
    "receipt_number": "12345",
    "total_amount": 162.00,
    ...
  },
  "extraction_metadata": {
    "vendor": "Mead Clark Lumber",
    "format_detected": "mead_clark_format1",
    "confidence": 0.85,
    "confidence_level": "high"
  }
}
```

---

## Troubleshooting

### Redis not running
- Check: `redis-cli ping`
- Start: `brew services start redis` or `redis-server`

### RQ worker not processing
- Check Redis is running
- Check worker terminal for errors
- Verify virtual environment is activated
- Check dependencies: `pip list | grep rq`

### API server not responding
- Check server terminal for errors
- Verify port 8001 is not in use: `lsof -i :8001`
- Check virtual environment is activated

### Task stuck in "queued" status
- Check RQ worker is running
- Check worker terminal for errors
- Check Redis connection: `redis-cli ping`

### Extraction errors
- Check RQ worker terminal for detailed error messages
- Verify document image exists and is readable
- Check Tesseract is installed: `tesseract --version`

---

## Next Steps

After successful testing:
- **Step 5**: Validate extracted fields match expected values
  - See: `logs/testing/field_extraction_validation_plan.md`
  - Use: `tests/integration/test_extraction_accuracy.py`

---

## Quick Reference

**Terminal 1 (Redis):**
```bash
redis-server
# or
brew services start redis
```

**Terminal 2 (RQ Worker):**
```bash
cd apps/digidoc
source .venv/bin/activate  # if not using direnv
rq worker
```

**Terminal 3 (API Server):**
```bash
cd apps/digidoc
source .venv/bin/activate  # if not using direnv
python3 -m ocr_service.api_server
```

**Terminal 4 (Testing):**
```bash
curl -X POST http://localhost:8001/api/digidoc/queue \
  -H "Content-Type: application/json" \
  -d '{"file_path": "/absolute/path/to/image.png", "calling_app_id": "test"}'
```

