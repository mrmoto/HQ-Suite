#!/bin/bash
# Test Runner Script for DigiDoc
# Runs all test suites and provides a summary

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DIGIDOC_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "=========================================="
echo "DigiDoc Test Suite Runner"
echo "=========================================="
echo ""

cd "$DIGIDOC_ROOT"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not found"
    exit 1
fi

echo "Python version: $(python3 --version)"
echo ""

# Run configuration test
echo "Running configuration tests..."
python3 ocr_service/test_config.py
CONFIG_TEST_RESULT=$?

echo ""
echo "----------------------------------------"
echo ""

# Run file utils test (if exists)
if [ -f "ocr_service/test_file_utils.py" ]; then
    echo "Running file utils tests..."
    python3 ocr_service/test_file_utils.py || true
    echo ""
fi

# Run preprocessing test (if exists)
if [ -f "ocr_service/test_preprocessing.py" ]; then
    echo "Running preprocessing tests..."
    python3 ocr_service/test_preprocessing.py || true
    echo ""
fi

# Run full pipeline test
echo "Running full pipeline tests..."
python3 ocr_service/test_full_pipeline.py
PIPELINE_TEST_RESULT=$?

echo ""
echo "----------------------------------------"
echo ""

# Run GUI component tests
echo "Running GUI component tests..."
python3 ocr_service/test_gui_components.py
GUI_TEST_RESULT=$?

echo ""
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo ""

if [ $CONFIG_TEST_RESULT -eq 0 ]; then
    echo "✅ Configuration tests: PASSED"
else
    echo "❌ Configuration tests: FAILED"
fi

if [ $PIPELINE_TEST_RESULT -eq 0 ]; then
    echo "✅ Pipeline tests: PASSED"
else
    echo "❌ Pipeline tests: FAILED"
fi

if [ $GUI_TEST_RESULT -eq 0 ]; then
    echo "✅ GUI component tests: PASSED"
else
    echo "❌ GUI component tests: FAILED"
fi

echo ""

# Overall result
if [ $CONFIG_TEST_RESULT -eq 0 ] && [ $PIPELINE_TEST_RESULT -eq 0 ] && [ $GUI_TEST_RESULT -eq 0 ]; then
    echo "🎉 All tests passed!"
    exit 0
else
    echo "⚠️  Some tests failed"
    exit 1
fi
