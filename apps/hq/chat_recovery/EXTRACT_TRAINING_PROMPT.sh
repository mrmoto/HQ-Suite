#!/bin/bash

# Script to extract user chat messages from Cursor global database
# Outputs training data in a format suitable for AI context
# Usage:
#   ./EXTRACT_TRAINING_PROMPT.sh                    # Output to stdout
#   ./EXTRACT_TRAINING_PROMPT.sh > training_prompt.txt  # Save to file

# Global database location
GLOBAL_DB="$HOME/Library/Application Support/Cursor/User/globalStorage/state.vscdb"

# Check if global database exists
if [ ! -f "$GLOBAL_DB" ]; then
    echo "ERROR: Global database not found: $GLOBAL_DB" >&2
    echo "Make sure Cursor has been used and chat history exists." >&2
    exit 1
fi

# Check if database is accessible (try a simple query)
if ! sqlite3 -readonly "$GLOBAL_DB" "SELECT 1;" >/dev/null 2>&1; then
    if ! sqlite3 "$GLOBAL_DB" "SELECT 1;" >/dev/null 2>&1; then
        echo "ERROR: Database is locked. Please close Cursor and try again." >&2
        exit 1
    fi
fi

# Print training data header
cat <<'HEADER'
=== TRAINING DATA - READ ONLY ===
This file contains training data extracted from Cursor chat history.
IMPORTANT: This is training data only. Do NOT execute any code, create files, 
edit files, or perform any actions. This data is for context and understanding 
architectural considerations only.

=== END TRAINING DATA HEADER ===

HEADER

# Create temporary Python script
PYTHON_SCRIPT=$(mktemp)
cat > "$PYTHON_SCRIPT" <<'PYEOF'
import json
import sys

messages = []

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    try:
        data = json.loads(line)
        # Only extract user messages (type == 1)
        if data.get('type') == 1:
            timestamp = data.get('createdAt', '')
            text = data.get('text', '').strip()
            # Only include messages with actual text content
            if text:
                messages.append((timestamp, text))
    except (json.JSONDecodeError, AttributeError, ValueError):
        # Skip invalid JSON or non-dict entries
        continue

# Sort by timestamp (empty timestamps go to end)
def sort_key(x):
    ts = x[0] if x[0] else ''
    return (ts == '', ts)  # Empty timestamps sort last

messages.sort(key=sort_key)

# Output each message with delimiter, timestamp, and text (preserving newlines)
for idx, (timestamp, text) in enumerate(messages, start=1):
    print(f"=== MESSAGE {idx} ===")
    print(f"TIMESTAMP: {timestamp}")
    print("TEXT:")
    # Print text as-is, preserving all newlines
    print(text)
    print()  # Empty line between messages

# Print end marker
print("=== END OF TRAINING DATA ===")
PYEOF

# Extract all user messages (type=1) from global database
# Query cursorDiskKV for bubbleId keys, parse JSON, filter for user messages, sort by timestamp
# Try read-only first, fall back to normal mode if needed
(sqlite3 -readonly "$GLOBAL_DB" "SELECT value FROM cursorDiskKV WHERE key LIKE 'bubbleId:%';" 2>/dev/null || \
 sqlite3 "$GLOBAL_DB" "SELECT value FROM cursorDiskKV WHERE key LIKE 'bubbleId:%';" 2>/dev/null) | \
python3 "$PYTHON_SCRIPT"

# Clean up
rm -f "$PYTHON_SCRIPT"
