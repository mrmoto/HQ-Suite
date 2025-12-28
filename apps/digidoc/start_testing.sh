#!/bin/bash
# Quick-start script for end-to-end testing
# Starts Redis, RQ worker, and API server

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "DigiDoc End-to-End Testing Setup"
echo "=========================================="
echo ""

# Check Redis
echo "1. Checking Redis..."
if redis-cli ping > /dev/null 2>&1; then
    echo "   ✅ Redis is running"
else
    echo "   ⚠️  Redis is not running"
    echo "   Starting Redis..."
    brew services start redis || redis-server &
    sleep 2
    if redis-cli ping > /dev/null 2>&1; then
        echo "   ✅ Redis started"
    else
        echo "   ❌ Failed to start Redis"
        exit 1
    fi
fi

echo ""
echo "=========================================="
echo "Next Steps (run in separate terminals):"
echo "=========================================="
echo ""
echo "Terminal 2 - Start RQ Worker:"
echo "  cd $SCRIPT_DIR"
echo "  source .venv/bin/activate  # if not using direnv"
echo "  rq worker"
echo ""
echo "Terminal 3 - Start API Server:"
echo "  cd $SCRIPT_DIR"
echo "  source .venv/bin/activate  # if not using direnv"
echo "  python3 -m ocr_service.api_server"
echo ""
echo "Terminal 4 - Test:"
echo "  curl -X POST http://localhost:8001/api/digidoc/queue \\"
echo "    -H \"Content-Type: application/json\" \\"
echo "    -d '{\"file_path\": \"/absolute/path/to/image.png\", \"calling_app_id\": \"test\"}'"
echo ""
echo "Or use the semi-automated script:"
echo "  python3 tests/integration/test_extraction_accuracy.py \\"
echo "    --document \"/absolute/path/to/image.png\" \\"
echo "    --use-queue"
echo ""
echo "See TESTING_END_TO_END.md for detailed instructions"
echo ""

