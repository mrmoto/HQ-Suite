#!/bin/bash

# Script to extract all Cursor chat history from all workspace IDs
# Creates a comprehensive export file with all user prompts and agent replies
# Usage:
#   ./EXTRACT_CURSOR_CHAT_HISTORY.sh                    # Dry-run mode (default)
#   ./EXTRACT_CURSOR_CHAT_HISTORY.sh --execute          # Actually extract and create export file
#   ./EXTRACT_CURSOR_CHAT_HISTORY.sh --diagnose         # Show key patterns in databases (diagnostic mode)

# Don't exit on error - we want to continue processing even if some databases are locked
set +e

# Determine if we're in execute mode or diagnose mode
EXECUTE_MODE=false
DIAGNOSE_MODE=false
for arg in "$@"; do
    if [ "$arg" == "--execute" ]; then
        EXECUTE_MODE=true
    elif [ "$arg" == "--diagnose" ]; then
        DIAGNOSE_MODE=true
    fi
done

# Get script directory and set output directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Output to app_development/chat_recovery_files/ (two levels up from script, then into chat_recovery_files)
OUTPUT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)/chat_recovery_files"

# Cursor storage location
CURSOR_STORAGE="$HOME/Library/Application Support/Cursor/User/workspaceStorage"

# Timestamp for filename
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Determine output filename
if [ "$EXECUTE_MODE" = true ]; then
    OUTPUT_FILE="$OUTPUT_DIR/cursor_chat_history_export_${TIMESTAMP}.json"
else
    OUTPUT_FILE="$OUTPUT_DIR/cursor_chat_history_export_DRYRUN_${TIMESTAMP}.json"
fi

# Function to safely query SQLite database with locking handling
query_sqlite() {
    local db_file="$1"
    local query="$2"
    local timeout=5000  # 5 seconds timeout in milliseconds
    
    # Create a temporary SQL file with timeout and query
    local sql_file=$(mktemp)
    echo ".timeout $timeout" > "$sql_file"
    echo "$query" >> "$sql_file"
    
    # Try to query with busy timeout
    # First try read-only mode which is less likely to conflict
    sqlite3 -readonly "$db_file" < "$sql_file" 2>/dev/null || {
        # If that fails, try normal mode
        sqlite3 "$db_file" < "$sql_file" 2>/dev/null || {
            # If still fails, return empty (silent fail for locked database)
            rm -f "$sql_file"
            return 1
        }
    }
    
    rm -f "$sql_file"
}

# Function to check if database is accessible (not locked)
check_db_accessible() {
    local db_file="$1"
    
    # Try a simple query to check if database is accessible
    query_sqlite "$db_file" "SELECT 1;" >/dev/null 2>&1
    return $?
}

# Function to escape JSON string
escape_json() {
    local str="$1"
    echo "$str" | python3 -c "import sys, json; print(json.dumps(sys.stdin.read()))" 2>/dev/null || echo "\"$str\""
}

# Function to diagnose key patterns in a database
diagnose_database() {
    local workspace_id="$1"
    local workspace_dir="$CURSOR_STORAGE/$workspace_id"
    local db_file="$workspace_dir/state.vscdb"
    
    echo "=== Workspace: $workspace_id ===" >&2
    
    # Check if database exists
    if [ ! -f "$db_file" ]; then
        echo "  Database not found: $db_file" >&2
        return 1
    fi
    
    # Check if database is accessible
    if ! check_db_accessible "$db_file"; then
        echo "  Database locked (Cursor may be running)" >&2
        return 1
    fi
    
    # Analyze cursorDiskKV table
    echo "  cursorDiskKV table:" >&2
    local cursor_kv_count=$(query_sqlite "$db_file" "SELECT COUNT(*) FROM cursorDiskKV;" 2>/dev/null || echo "0")
    echo "    Total records: $cursor_kv_count" >&2
    
    if [ "$cursor_kv_count" -gt 0 ]; then
        echo "    Key patterns (top 20):" >&2
        query_sqlite "$db_file" "SELECT DISTINCT substr(key, 1, 50) as key_prefix, COUNT(*) as count FROM cursorDiskKV GROUP BY key_prefix ORDER BY count DESC LIMIT 20;" 2>/dev/null | while IFS='|' read -r prefix count; do
            echo "      $prefix: $count records" >&2
        done
        
        # Check for chat-related patterns
        echo "    Chat-related keys:" >&2
        local chat_keys=$(query_sqlite "$db_file" "SELECT COUNT(*) FROM cursorDiskKV WHERE key LIKE '%bubble%' OR key LIKE '%chat%' OR key LIKE '%message%' OR key LIKE '%conversation%';" 2>/dev/null || echo "0")
        echo "      Found: $chat_keys keys matching chat patterns" >&2
        
        if [ "$chat_keys" -gt 0 ]; then
            query_sqlite "$db_file" "SELECT DISTINCT substr(key, 1, 60) FROM cursorDiskKV WHERE key LIKE '%bubble%' OR key LIKE '%chat%' OR key LIKE '%message%' OR key LIKE '%conversation%' LIMIT 10;" 2>/dev/null | while read -r key; do
                echo "        - $key" >&2
            done
        fi
    else
        echo "    Table is empty" >&2
    fi
    
    # Analyze ItemTable
    echo "  ItemTable:" >&2
    local item_count=$(query_sqlite "$db_file" "SELECT COUNT(*) FROM ItemTable;" 2>/dev/null || echo "0")
    echo "    Total records: $item_count" >&2
    
    if [ "$item_count" -gt 0 ]; then
        # Show all key prefixes in ItemTable (not just chat-related)
        echo "    All key patterns (top 30):" >&2
        query_sqlite "$db_file" "SELECT DISTINCT substr(key, 1, 60) as key_prefix, COUNT(*) as count FROM ItemTable GROUP BY key_prefix ORDER BY count DESC LIMIT 30;" 2>/dev/null | while IFS='|' read -r prefix count; do
            echo "      $prefix: $count records" >&2
        done
        
        # Check for chat-related patterns
        local chat_item_keys=$(query_sqlite "$db_file" "SELECT COUNT(*) FROM ItemTable WHERE key LIKE '%chat%' OR key LIKE '%bubble%' OR key LIKE '%message%';" 2>/dev/null || echo "0")
        echo "    Chat-related keys: $chat_item_keys" >&2
        
        if [ "$chat_item_keys" -gt 0 ]; then
            query_sqlite "$db_file" "SELECT key FROM ItemTable WHERE key LIKE '%chat%' OR key LIKE '%bubble%' OR key LIKE '%message%' LIMIT 10;" 2>/dev/null | while read -r key; do
                echo "      - $key" >&2
            done
        fi
        
        # Sample ItemTable values to check for chat content
        echo "    Sampling ItemTable values for chat content:" >&2
        local sample_file=$(mktemp)
        query_sqlite "$db_file" "SELECT key, substr(value, 1, 200) FROM ItemTable LIMIT 20;" 2>/dev/null > "$sample_file"
        
        local sample_count=0
        while IFS='|' read -r key value_preview; do
            # Check if value contains chat-like content
            if echo "$value_preview" | grep -qiE "(bubble|message|prompt|response|conversation|chat)" 2>/dev/null; then
                sample_count=$((sample_count + 1))
                if [ $sample_count -le 5 ]; then
                    echo "      Key: $key" >&2
                    local preview_len=${#value_preview}
                    if [ $preview_len -gt 100 ]; then
                        echo "        Value preview: ${value_preview:0:100}..." >&2
                    else
                        echo "        Value preview: $value_preview" >&2
                    fi
                fi
            fi
        done < "$sample_file"
        rm -f "$sample_file"
        
        if [ $sample_count -eq 0 ]; then
            echo "      No chat-like content found in sampled values" >&2
        else
            echo "      Found $sample_count entries with chat-like content (showing first 5)" >&2
        fi
    fi
    
    # Search for other files in workspace directory
    echo "  Files in workspace directory:" >&2
    if [ -d "$workspace_dir" ]; then
        # Find database files
        local db_files=$(find "$workspace_dir" -maxdepth 1 -type f \( -name "*.db" -o -name "*.sqlite" -o -name "*.sqlite3" \) 2>/dev/null)
        if [ -n "$db_files" ]; then
            echo "    Database files:" >&2
            echo "$db_files" | while read -r file; do
                local file_size=$(du -h "$file" 2>/dev/null | cut -f1)
                echo "      - $(basename "$file") ($file_size)" >&2
            done
        else
            echo "    No additional database files found" >&2
        fi
        
        # Find JSON files
        local json_files=$(find "$workspace_dir" -maxdepth 1 -type f -name "*.json" 2>/dev/null | head -10)
        if [ -n "$json_files" ]; then
            echo "    JSON files:" >&2
            echo "$json_files" | while read -r file; do
                local file_size=$(du -h "$file" 2>/dev/null | cut -f1)
                echo "      - $(basename "$file") ($file_size)" >&2
            done
        else
            echo "    No JSON files found" >&2
        fi
        
        # Find files with chat-related names
        local chat_files=$(find "$workspace_dir" -maxdepth 1 -type f \( -iname "*chat*" -o -iname "*conversation*" -o -iname "*message*" -o -iname "*history*" \) 2>/dev/null | head -10)
        if [ -n "$chat_files" ]; then
            echo "    Files with chat-related names:" >&2
            echo "$chat_files" | while read -r file; do
                local file_size=$(du -h "$file" 2>/dev/null | cut -f1)
                echo "      - $(basename "$file") ($file_size)" >&2
            done
        fi
        
        # List all files (for comprehensive view)
        local all_files=$(find "$workspace_dir" -maxdepth 1 -type f 2>/dev/null | wc -l | tr -d ' ')
        echo "    Total files in directory: $all_files" >&2
        if [ "$all_files" -gt 0 ] && [ "$all_files" -le 20 ]; then
            echo "    All files:" >&2
            find "$workspace_dir" -maxdepth 1 -type f 2>/dev/null | while read -r file; do
                echo "      - $(basename "$file")" >&2
            done
        fi
    else
        echo "    Workspace directory not found" >&2
    fi
    
    echo "" >&2
    return 0
}

# Function to extract chat history from a workspace
extract_workspace_chat() {
    local workspace_id="$1"
    local workspace_dir="$CURSOR_STORAGE/$workspace_id"
    local db_file="$workspace_dir/state.vscdb"
    local temp_file=$(mktemp)
    
    # Check if database exists
    if [ ! -f "$db_file" ]; then
        echo "    ⚠ Database not found: $db_file" >&2
        rm -f "$temp_file"
        return 1
    fi
    
    # Check if database is accessible (not locked)
    if ! check_db_accessible "$db_file"; then
        echo "    ⚠ Database locked (Cursor may be running): $db_file" >&2
        echo "      → Skipping (will work when Cursor is closed)" >&2
        rm -f "$temp_file"
        return 1
    fi
    
    # Extract workspace info
    local workspace_info="{}"
    if [ -f "$workspace_dir/workspace.json" ]; then
        workspace_info=$(cat "$workspace_dir/workspace.json" 2>/dev/null || echo "{}")
        # Validate JSON
        echo "$workspace_info" | python3 -m json.tool >/dev/null 2>&1 || workspace_info="{}"
    fi
    
    # Extract chat messages from cursorDiskKV table
    # Try multiple key patterns to find chat messages
    local chat_messages_file=$(mktemp)
    local chat_count=0
    
    # Try primary pattern first
    query_sqlite "$db_file" "SELECT key, value FROM cursorDiskKV WHERE key LIKE 'bubbleId:%' ORDER BY key;" > "$chat_messages_file" 2>/dev/null
    chat_count=$(wc -l < "$chat_messages_file" 2>/dev/null || echo "0")
    
    # If no messages found, try alternative patterns
    if [ "$chat_count" -eq 0 ]; then
        # Try multiple patterns (more specific to avoid UI state keys)
        # Exclude workbench.* keys which are UI state, not chat content
        query_sqlite "$db_file" "SELECT key, value FROM cursorDiskKV WHERE (key LIKE 'bubbleId:%' OR key LIKE 'chat:%' OR key LIKE 'message:%' OR key LIKE 'conversation:%' OR key LIKE 'bubble:%') AND key NOT LIKE 'workbench.%' ORDER BY key;" > "$chat_messages_file" 2>/dev/null
        chat_count=$(wc -l < "$chat_messages_file" 2>/dev/null || echo "0")
    fi
    
    # Diagnostic output only in diagnose mode (to avoid breaking JSON parsing)
    if [ "$DIAGNOSE_MODE" = true ] && [ "$chat_count" -eq 0 ]; then
        local all_keys_file=$(mktemp)
        query_sqlite "$db_file" "SELECT key FROM cursorDiskKV ORDER BY key LIMIT 100;" > "$all_keys_file" 2>/dev/null
        local all_keys_count=$(wc -l < "$all_keys_file" 2>/dev/null || echo "0")
        
        if [ "$all_keys_count" -gt 0 ]; then
            echo "    ⚠ No chat messages found with known patterns" >&2
            echo "    → Found $all_keys_count total keys in cursorDiskKV (showing first 20):" >&2
            head -20 "$all_keys_file" | while read -r key; do
                echo "      - $key" >&2
            done
        else
            echo "    ⚠ cursorDiskKV table is empty" >&2
        fi
        rm -f "$all_keys_file"
    fi
    
    # Extract user rules from ItemTable
    local user_rules=$(query_sqlite "$db_file" "SELECT value FROM ItemTable WHERE key = 'aicontext.personalContext';" 2>/dev/null | head -1)
    
    # Extract all ItemTable entries (may contain other relevant data)
    local item_table_file=$(mktemp)
    query_sqlite "$db_file" "SELECT key, value FROM ItemTable;" > "$item_table_file" 2>/dev/null
    
    # Build JSON using Python for proper escaping
    python3 <<PYTHON_SCRIPT > "$temp_file"
import json
import sys

workspace_id = "$workspace_id"
workspace_info_str = '''$workspace_info'''
user_rules_str = '''$user_rules'''

# Parse workspace info
try:
    workspace_info = json.loads(workspace_info_str)
except:
    workspace_info = {}

# Parse user rules
user_rules_json = None
if user_rules_str:
    try:
        user_rules_json = json.loads(user_rules_str)
    except:
        user_rules_json = user_rules_str

# Parse chat messages
chat_messages = []
try:
    with open("$chat_messages_file", "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split("|", 1)
            if len(parts) == 2:
                key, value = parts
                try:
                    value_json = json.loads(value)
                    chat_messages.append({"key": key, "value": value_json})
                except:
                    chat_messages.append({"key": key, "value": value})
except Exception as e:
    pass

# Parse item table entries
item_table_entries = []
try:
    with open("$item_table_file", "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split("|", 1)
            if len(parts) == 2:
                key, value = parts
                try:
                    value_json = json.loads(value)
                    item_table_entries.append({"key": key, "value": value_json})
                except:
                    item_table_entries.append({"key": key, "value": value})
except Exception as e:
    pass

# Build result
result = {
    "workspace_id": workspace_id,
    "workspace_info": workspace_info,
    "user_rules": user_rules_json,
    "chat_messages": chat_messages,
    "item_table_entries": item_table_entries
}

print(json.dumps(result, indent=2, ensure_ascii=False))
PYTHON_SCRIPT
    
    # Output the JSON
    cat "$temp_file"
    
    # Cleanup
    rm -f "$temp_file" "$chat_messages_file" "$item_table_file"
    return 0
}

# Print header
echo "=========================================="
if [ "$DIAGNOSE_MODE" = true ]; then
    echo "DIAGNOSE CURSOR DATABASES - KEY PATTERN ANALYSIS"
    echo "=========================================="
    echo ""
    echo "This mode analyzes database key patterns to help identify chat message storage."
    echo "Cursor Storage: $CURSOR_STORAGE"
    echo ""
elif [ "$EXECUTE_MODE" = true ]; then
    echo "EXTRACT CURSOR CHAT HISTORY - EXECUTE MODE"
    echo "=========================================="
else
    echo "EXTRACT CURSOR CHAT HISTORY - DRY RUN MODE"
    echo "=========================================="
fi

if [ "$DIAGNOSE_MODE" = false ]; then
    echo ""
    echo "Cursor Storage: $CURSOR_STORAGE"
    echo "Output File: $OUTPUT_FILE"
    echo ""
fi

# Check if Cursor storage directory exists
if [ ! -d "$CURSOR_STORAGE" ]; then
    echo "ERROR: Cursor storage directory not found: $CURSOR_STORAGE"
    exit 1
fi

# Find all workspace directories
echo "Scanning for workspace IDs..."
workspace_dirs=()
while IFS= read -r -d '' dir; do
    if [ -f "$dir/state.vscdb" ] || [ -f "$dir/workspace.json" ]; then
        workspace_id=$(basename "$dir")
        workspace_dirs+=("$workspace_id")
    fi
done < <(find "$CURSOR_STORAGE" -mindepth 1 -maxdepth 1 -type d -print0 2>/dev/null)

total_workspaces=${#workspace_dirs[@]}
echo "Found $total_workspaces workspace(s)"
echo ""

if [ $total_workspaces -eq 0 ]; then
    echo "No workspaces found. Make sure Cursor has been used at least once."
    exit 1
fi

# Function to check global Cursor storage for chat data
check_global_storage() {
    local global_storage="$HOME/Library/Application Support/Cursor/User"
    
    echo "=== Global Cursor Storage Analysis ===" >&2
    echo "Location: $global_storage" >&2
    echo "" >&2
    
    if [ ! -d "$global_storage" ]; then
        echo "  Global storage directory not found" >&2
        return 1
    fi
    
    # Search for database files
    echo "  Database files:" >&2
    local global_dbs=$(find "$global_storage" -maxdepth 3 -type f \( -name "*.db" -o -name "*.sqlite" -o -name "*.sqlite3" \) 2>/dev/null | head -20)
    if [ -n "$global_dbs" ]; then
        echo "$global_dbs" | while read -r file; do
            local file_size=$(du -h "$file" 2>/dev/null | cut -f1)
            local rel_path=$(echo "$file" | sed "s|^$global_storage/||")
            echo "    - $rel_path ($file_size)" >&2
        done
    else
        echo "    No database files found" >&2
    fi
    
    # Search for JSON files with chat-related names
    echo "  JSON files (chat-related):" >&2
    local global_json=$(find "$global_storage" -maxdepth 3 -type f -name "*.json" \( -iname "*chat*" -o -iname "*conversation*" -o -iname "*message*" -o -iname "*history*" \) 2>/dev/null | head -20)
    if [ -n "$global_json" ]; then
        echo "$global_json" | while read -r file; do
            local file_size=$(du -h "$file" 2>/dev/null | cut -f1)
            local rel_path=$(echo "$file" | sed "s|^$global_storage/||")
            echo "    - $rel_path ($file_size)" >&2
        done
    else
        echo "    No chat-related JSON files found" >&2
    fi
    
    # List subdirectories that might contain chat data
    echo "  Subdirectories:" >&2
    find "$global_storage" -maxdepth 2 -type d 2>/dev/null | head -20 | while read -r dir; do
        local rel_path=$(echo "$dir" | sed "s|^$global_storage/||")
        if [ -n "$rel_path" ]; then
            local file_count=$(find "$dir" -maxdepth 1 -type f 2>/dev/null | wc -l | tr -d ' ')
            echo "    - $rel_path ($file_count files)" >&2
        fi
    done
    
    echo "" >&2
}

# If diagnose mode, run diagnostics and exit
if [ "$DIAGNOSE_MODE" = true ]; then
    echo "Analyzing databases for key patterns..."
    echo ""
    
    for workspace_id in "${workspace_dirs[@]}"; do
        diagnose_database "$workspace_id"
    done
    
    # Check global storage
    check_global_storage
    
    echo "=========================================="
    echo "DIAGNOSIS COMPLETE"
    echo "=========================================="
    echo ""
    echo "Review the key patterns above to identify how chat messages are stored."
    echo "Common patterns to look for:"
    echo "  - bubbleId:* (original pattern)"
    echo "  - chat:* or message:* (alternative patterns)"
    echo "  - Any keys containing 'chat', 'message', 'bubble', or 'conversation'"
    echo ""
    echo "If chat messages are not found:"
    echo "  - They may be stored in cloud-synced storage"
    echo "  - They may be stored in a different format/location"
    echo "  - They may have been cleared or never saved locally"
    echo ""
    exit 0
fi

# Start building JSON output
if [ "$EXECUTE_MODE" = true ]; then
    exec 3>"$OUTPUT_FILE"
else
    exec 3>"$OUTPUT_FILE"
fi

cat >&3 <<EOF
{
  "export_timestamp": "$TIMESTAMP",
  "export_mode": "$([ "$EXECUTE_MODE" = true ] && echo "execute" || echo "dryrun")",
  "cursor_storage_path": "$CURSOR_STORAGE",
  "workspaces": [
EOF

# Process each workspace
processed=0
skipped=0
failed=0
workspace_data_file=$(mktemp)

for i in "${!workspace_dirs[@]}"; do
    workspace_id="${workspace_dirs[$i]}"
    echo "Processing workspace $((i+1))/$total_workspaces: $workspace_id"
    
    # Extract chat history (capture stderr separately)
    extract_workspace_chat "$workspace_id" > "$workspace_data_file" 2>&1
    exit_code=$?
    workspace_data=$(cat "$workspace_data_file")
    
    if [ $exit_code -eq 0 ] && [ -n "$workspace_data" ] && echo "$workspace_data" | python3 -m json.tool >/dev/null 2>&1; then
        processed=$((processed + 1))
        
        # Count chat messages extracted
        chat_msg_count=$(echo "$workspace_data" | python3 -c "import sys, json; data = json.load(sys.stdin); print(len(data.get('chat_messages', [])))" 2>/dev/null || echo "0")
        chat_msg_count=${chat_msg_count:-0}  # Default to 0 if empty
        
        if [ "${chat_msg_count:-0}" -gt 0 ] 2>/dev/null; then
            echo "  ✓ Extracted chat history ($chat_msg_count messages)"
        else
            echo "  ✓ Extracted workspace data (0 chat messages found)"
        fi
        
        # Add to JSON (with comma if not last)
        if [ $i -lt $((${#workspace_dirs[@]} - 1)) ]; then
            echo "$workspace_data," >&3
        else
            echo "$workspace_data" >&3
        fi
    elif echo "$workspace_data" | grep -q "locked"; then
        skipped=$((skipped + 1))
        echo "  ⚠ Skipped (database locked)"
    else
        failed=$((failed + 1))
        echo "  ✗ Failed to extract"
        # Show error details in dry-run mode
        if [ "$EXECUTE_MODE" = false ]; then
            echo "    Error output: $(echo "$workspace_data" | head -3)"
        fi
    fi
    echo ""
done

rm -f "$workspace_data_file"

# Close JSON
cat >&3 <<EOF
  ],
  "summary": {
    "total_workspaces": $total_workspaces,
    "processed": $processed,
    "skipped": $skipped,
    "failed": $failed
  }
}
EOF

exec 3>&-

# Print summary
echo "=========================================="
echo "SUMMARY"
echo "=========================================="
echo "Total workspaces found: $total_workspaces"
echo "Successfully processed: $processed"
echo "Skipped (locked): $skipped"
echo "Failed: $failed"
echo ""

# Count total chat messages in export file
if [ -f "$OUTPUT_FILE" ]; then
    total_chat_messages=$(python3 <<PYTHON_SCRIPT
import json
import sys

try:
    with open("$OUTPUT_FILE", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    total = sum(len(w.get("chat_messages", [])) for w in data.get("workspaces", []))
    print(total)
except:
    print("0")
PYTHON_SCRIPT
)
    
    if [ "$total_chat_messages" -gt 0 ]; then
        echo "Total chat messages extracted: $total_chat_messages"
    else
        echo "⚠ No chat messages found in any workspace"
        echo "  → Run with --diagnose to analyze key patterns"
    fi
    echo ""
fi
if [ "$EXECUTE_MODE" = true ]; then
    echo "✓ Export file created: $OUTPUT_FILE"
    if [ -f "$OUTPUT_FILE" ]; then
        file_size=$(du -h "$OUTPUT_FILE" | cut -f1)
        echo "  File size: $file_size"
    fi
else
    echo "✓ Dry-run export file created: $OUTPUT_FILE"
    if [ -f "$OUTPUT_FILE" ]; then
        file_size=$(du -h "$OUTPUT_FILE" | cut -f1)
        echo "  File size: $file_size"
    fi
    echo ""
    echo "To create the actual export file, run:"
    echo "  ./EXTRACT_CURSOR_CHAT_HISTORY.sh --execute"
fi
echo "=========================================="
