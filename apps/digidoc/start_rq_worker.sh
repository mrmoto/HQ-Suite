#!/bin/bash
# RQ Worker Startup Wrapper
# Sets environment variables in shell before starting Python
# This ensures they're available when RQ forks processes

export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
export MP_START_METHOD=spawn
export ARROW_DISABLE_CURL=1

# Change to digidoc directory
cd "$(dirname "$0")"

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Run the Python worker script
exec python3 -m ocr_service.queue.start_rq_worker "$@"

