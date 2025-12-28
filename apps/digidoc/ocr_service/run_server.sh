#!/bin/bash

# Run OCR Service API Server
# Usage: ./run_server.sh [port]

PORT=${1:-5000}
DEBUG=${OCR_SERVICE_DEBUG:-false}

export OCR_SERVICE_PORT=$PORT
export OCR_SERVICE_DEBUG=$DEBUG

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Get project root (one level up from ocr_service/)
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Check for virtual environment
VENV_PYTHON="$PROJECT_ROOT/venv/bin/python3"

if [ -f "$VENV_PYTHON" ]; then
    echo "Using virtual environment Python: $VENV_PYTHON"
    PYTHON_CMD="$VENV_PYTHON"
elif [ -n "$VIRTUAL_ENV" ]; then
    # Already in a virtual environment
    echo "Using active virtual environment"
    PYTHON_CMD="python3"
else
    echo "Warning: No virtual environment found. Using system Python."
    echo "Consider creating a venv: python3 -m venv venv"
    PYTHON_CMD="python3"
fi

# Run Flask server from project root (so ocr_service module can be found)
cd "$PROJECT_ROOT"
$PYTHON_CMD -m ocr_service.api_server
