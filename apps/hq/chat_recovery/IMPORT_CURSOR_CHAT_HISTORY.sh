#!/bin/bash

# Script to import Cursor chat history from JSON export file into workspace database
# Usage:
#   ./IMPORT_CURSOR_CHAT_HISTORY.sh [export_file.json]                    # Dry-run mode (default)
#   ./IMPORT_CURSOR_CHAT_HISTORY.sh [export_file.json] --sandbox --execute # Test in sandbox
#   ./IMPORT_CURSOR_CHAT_HISTORY.sh [export_file.json] --execute          # Import to real DB (requires confirmation)
#   ./IMPORT_CURSOR_CHAT_HISTORY.sh [export_file.json] --execute --force  # Skip confirmation (dangerous)
#   ./IMPORT_CURSOR_CHAT_HISTORY.sh [export_file.json] --sandbox --execute --import-all-workspaces # Import ALL workspaces into sandbox

# Don't exit on error - we want to continue processing and report errors
set +e

# Determine if we're in execute mode
EXECUTE_MODE=false
SANDBOX_MODE=false
FORCE_MODE=false
IMPORT_ALL_WORKSPACES=false
EXPORT_FILE=""

# Parse arguments
for arg in "$@"; do
    if [ "$arg" == "--execute" ]; then
        EXECUTE_MODE=true
    elif [ "$arg" == "--sandbox" ]; then
        SANDBOX_MODE=true
    elif [ "$arg" == "--force" ]; then
        FORCE_MODE=true
    elif [ "$arg" == "--import-all-workspaces" ]; then
        IMPORT_ALL_WORKSPACES=true
    elif [ -f "$arg" ] || [ -f "../chat_recovery_files/$arg" ] || [ -f "../../chat_recovery_files/$arg" ]; then
        # Check if it's a valid file path
        if [ -f "$arg" ]; then
            EXPORT_FILE="$arg"
        elif [ -f "../chat_recovery_files/$arg" ]; then
            EXPORT_FILE="../chat_recovery_files/$arg"
        elif [ -f "../../chat_recovery_files/$arg" ]; then
            EXPORT_FILE="../../chat_recovery_files/$arg"
        fi
    fi
done

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CHAT_RECOVERY_FILES_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)/chat_recovery_files"
SANDBOX_DIR="$SCRIPT_DIR/sandbox"
SANDBOX_DB="$SANDBOX_DIR/state.vscdb"

# Cursor storage location
CURSOR_STORAGE="$HOME/Library/Application Support/Cursor/User/workspaceStorage"

# Function to find current workspace ID by matching workspace.json paths
find_current_workspace() {
    local workspace_id=""
    
    # Check if Cursor storage directory exists
    if [ ! -d "$CURSOR_STORAGE" ]; then
        echo "ERROR: Cursor storage directory not found: $CURSOR_STORAGE" >&2
        return 1
    fi
    
    # Find all workspace directories
    while IFS= read -r -d '' dir; do
        if [ -f "$dir/workspace.json" ]; then
            workspace_path=$(cat "$dir/workspace.json" 2>/dev/null | python3 -c "import sys, json; data = json.load(sys.stdin); print(data.get('workspace', ''))" 2>/dev/null)
            
            # Check if workspace path contains "app_development/hq" or "hq.code-workspace"
            if echo "$workspace_path" | grep -q "app_development/hq" || echo "$workspace_path" | grep -q "hq.code-workspace"; then
                workspace_id=$(basename "$dir")
                echo "$workspace_id"
                return 0
            fi
        fi
    done < <(find "$CURSOR_STORAGE" -mindepth 1 -maxdepth 1 -type d -print0 2>/dev/null)
    
    return 1
}

# Function to validate JSON export file structure
validate_export_file() {
    local json_file="$1"
    
    if [ ! -f "$json_file" ]; then
        echo "ERROR: Export file not found: $json_file" >&2
        return 1
    fi
    
    # Validate JSON structure
    if ! python3 -m json.tool "$json_file" >/dev/null 2>&1; then
        echo "ERROR: Invalid JSON file: $json_file" >&2
        return 1
    fi
    
    # Check for required fields
    if ! python3 <<PYTHON_SCRIPT
import json
import sys

try:
    with open("$json_file", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    if "workspaces" not in data:
        print("ERROR: Missing 'workspaces' field in JSON", file=sys.stderr)
        sys.exit(1)
    
    if not isinstance(data["workspaces"], list):
        print("ERROR: 'workspaces' must be an array", file=sys.stderr)
        sys.exit(1)
    
    print("OK")
except Exception as e:
    print(f"ERROR: {e}", file=sys.stderr)
    sys.exit(1)
PYTHON_SCRIPT
    then
        return 1
    fi
    
    return 0
}

# Function to check if database is accessible (not locked)
check_db_accessible() {
    local db_file="$1"
    
    # Try a simple query to check if database is accessible
    sqlite3 -readonly "$db_file" "SELECT 1;" >/dev/null 2>&1
    return $?
}

# Function to validate import results
validate_import() {
    local db_file="$1"
    local expected_chat_count="$2"
    local expected_item_count="$3"
    local expected_user_rules="$4"  # "1" if user rules should exist, "0" otherwise
    
    local validation_errors=0
    
    echo "  Validating import..." >&2
    
    # Count actual records
    local actual_chat_count=$(sqlite3 "$db_file" "SELECT COUNT(*) FROM cursorDiskKV WHERE key LIKE 'bubbleId:%';" 2>/dev/null || echo "0")
    local actual_item_count=$(sqlite3 "$db_file" "SELECT COUNT(*) FROM ItemTable;" 2>/dev/null || echo "0")
    local actual_user_rules=$(sqlite3 "$db_file" "SELECT COUNT(*) FROM ItemTable WHERE key = 'aicontext.personalContext';" 2>/dev/null || echo "0")
    
    # Validate chat message count
    if [ "$actual_chat_count" -ne "$expected_chat_count" ]; then
        echo "    ✗ Chat message count mismatch: expected $expected_chat_count, got $actual_chat_count" >&2
        validation_errors=$((validation_errors + 1))
    else
        echo "    ✓ Chat messages: $actual_chat_count" >&2
    fi
    
    # Validate item table count (should match expected + user rules if present)
    local expected_total_items=$expected_item_count
    if [ "$expected_user_rules" = "1" ]; then
        expected_total_items=$((expected_total_items + 1))
    fi
    
    if [ "$actual_item_count" -ne "$expected_total_items" ]; then
        echo "    ✗ Item table count mismatch: expected $expected_total_items, got $actual_item_count" >&2
        validation_errors=$((validation_errors + 1))
    else
        echo "    ✓ Item table entries: $actual_item_count" >&2
    fi
    
    # Validate user rules if expected
    if [ "$expected_user_rules" = "1" ]; then
        if [ "$actual_user_rules" -ne 1 ]; then
            echo "    ✗ User rules not found" >&2
            validation_errors=$((validation_errors + 1))
        else
            echo "    ✓ User rules present" >&2
        fi
    fi
    
    # Sample a few records to check data integrity
    local sample_chat=$(sqlite3 "$db_file" "SELECT key FROM cursorDiskKV WHERE key LIKE 'bubbleId:%' LIMIT 1;" 2>/dev/null)
    if [ -z "$sample_chat" ] && [ "$expected_chat_count" -gt 0 ]; then
        echo "    ✗ No chat messages found (expected $expected_chat_count)" >&2
        validation_errors=$((validation_errors + 1))
    elif [ -n "$sample_chat" ]; then
        # Verify JSON validity of a sample value
        local sample_value=$(sqlite3 "$db_file" "SELECT value FROM cursorDiskKV WHERE key = '$sample_chat';" 2>/dev/null)
        if ! echo "$sample_value" | python3 -m json.tool >/dev/null 2>&1; then
            echo "    ⚠ Sample chat message value is not valid JSON (may be intentional)" >&2
        fi
    fi
    
    # Check for duplicate keys (shouldn't happen with PRIMARY KEY, but verify)
    local duplicate_chat=$(sqlite3 "$db_file" "SELECT key, COUNT(*) as cnt FROM cursorDiskKV GROUP BY key HAVING cnt > 1 LIMIT 1;" 2>/dev/null)
    if [ -n "$duplicate_chat" ]; then
        echo "    ✗ Found duplicate keys in cursorDiskKV" >&2
        validation_errors=$((validation_errors + 1))
    fi
    
    local duplicate_item=$(sqlite3 "$db_file" "SELECT key, COUNT(*) as cnt FROM ItemTable GROUP BY key HAVING cnt > 1 LIMIT 1;" 2>/dev/null)
    if [ -n "$duplicate_item" ]; then
        echo "    ✗ Found duplicate keys in ItemTable" >&2
        validation_errors=$((validation_errors + 1))
    fi
    
    if [ $validation_errors -eq 0 ]; then
        echo "  ✓ Validation passed" >&2
        return 0
    else
        echo "  ✗ Validation failed with $validation_errors error(s)" >&2
        return 1
    fi
}

# Function to compare sandbox to export file
compare_sandbox_to_export() {
    local db_file="$1"
    local export_file="$2"
    
    echo "  Comparing sandbox to export file..." >&2
    
    # Extract expected data from export
    local result=$(python3 <<PYTHON_SCRIPT
import json
import sys

export_file = "$export_file"
workspace_id = "$CURRENT_WORKSPACE_ID"

try:
    with open(export_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Find matching workspace
    workspace_found = None
    for workspace in data.get("workspaces", []):
        if workspace.get("workspace_id") == workspace_id:
            workspace_found = workspace
            break
    
    if not workspace_found:
        print("ERROR: Workspace not found in export", file=sys.stderr)
        sys.exit(1)
    
    chat_count = len(workspace_found.get("chat_messages", []))
    item_count = len(workspace_found.get("item_table_entries", []))
    has_user_rules = 1 if workspace_found.get("user_rules") else 0
    
    print(f"{chat_count}|{item_count}|{has_user_rules}")
except Exception as e:
    print(f"ERROR: {e}", file=sys.stderr)
    sys.exit(1)
PYTHON_SCRIPT
)
    
    if [ $? -ne 0 ]; then
        echo "    ✗ Failed to parse export file" >&2
        return 1
    fi
    
    local expected_chat=$(echo "$result" | cut -d'|' -f1)
    local expected_items=$(echo "$result" | cut -d'|' -f2)
    local expected_rules=$(echo "$result" | cut -d'|' -f3)
    
    # Run validation
    validate_import "$db_file" "$expected_chat" "$expected_items" "$expected_rules"
    return $?
}

# Function to confirm real database operation
confirm_real_database() {
    if [ "$SANDBOX_MODE" = true ]; then
        return 0  # No confirmation needed for sandbox
    fi
    
    if [ "$FORCE_MODE" = true ]; then
        return 0  # Skip confirmation with --force
    fi
    
    echo ""
    echo "⚠️  WARNING: You are about to import data into the REAL Cursor database!" >&2
    echo "   This will modify your actual workspace data." >&2
    echo ""
    echo "   Database: $CURSOR_STORAGE/$CURRENT_WORKSPACE_ID/state.vscdb" >&2
    echo ""
    echo "   It is STRONGLY RECOMMENDED to:" >&2
    echo "   1. Test in sandbox first: --sandbox --execute" >&2
    echo "   2. Close Cursor before importing" >&2
    echo "   3. Backup your database if needed" >&2
    echo ""
    read -p "   Type 'yes' to continue: " confirmation
    
    if [ "$confirmation" != "yes" ]; then
        echo "   Import cancelled." >&2
        return 1
    fi
    
    return 0
}

# Function to insert chat messages into cursorDiskKV table
insert_chat_messages() {
    local db_file="$1"
    local messages_json="$2"
    local execute="$3"
    
    local count=0
    local inserted=0
    local failed=0
    
    # Parse messages and insert
    python3 <<PYTHON_SCRIPT
import json
import sqlite3
import sys

db_file = "$db_file"
messages_json = '''$messages_json'''
execute = "$execute" == "true"

try:
    messages = json.loads(messages_json) if messages_json else []
    count = len(messages)
    inserted = 0
    failed = 0
    
    if execute:
        try:
            conn = sqlite3.connect(db_file, timeout=10.0)
            cursor = conn.cursor()
            
            for msg in messages:
                key = msg.get("key", "")
                value = msg.get("value", "")
                
                # Convert value to JSON string if it's not already a string
                if not isinstance(value, str):
                    value_json = json.dumps(value, ensure_ascii=False)
                else:
                    value_json = value
                
                try:
                    cursor.execute("INSERT INTO cursorDiskKV (key, value) VALUES (?, ?)", (key, value_json))
                    inserted += 1
                except Exception as e:
                    failed += 1
                    print(f"Failed to insert message {key}: {e}", file=sys.stderr)
            
            conn.commit()
            conn.close()
        except sqlite3.OperationalError as e:
            if "locked" in str(e).lower():
                print("ERROR: Database is locked. Please close Cursor and try again.", file=sys.stderr)
            else:
                print(f"ERROR: {e}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"ERROR: {e}", file=sys.stderr)
            sys.exit(1)
    
    print(f"{count}|{inserted}|{failed}")
except Exception as e:
    print(f"ERROR: {e}", file=sys.stderr)
    sys.exit(1)
PYTHON_SCRIPT
}

# Function to insert user rules into ItemTable
insert_user_rules() {
    local db_file="$1"
    local user_rules_json="$2"
    local execute="$3"
    
    python3 <<PYTHON_SCRIPT
import json
import sqlite3
import sys

db_file = "$db_file"
user_rules_json = '''$user_rules_json'''
execute = "$execute" == "true"

try:
    if not user_rules_json or user_rules_json.strip() == "null" or user_rules_json.strip() == "":
        print("0|0|0")
        sys.exit(0)
    
    # Parse user rules
    try:
        user_rules = json.loads(user_rules_json) if isinstance(user_rules_json, str) else user_rules_json
    except:
        user_rules = user_rules_json
    
    # Convert to JSON string
    if not isinstance(user_rules, str):
        value_json = json.dumps(user_rules, ensure_ascii=False)
    else:
        value_json = user_rules
    
    if execute:
        try:
            conn = sqlite3.connect(db_file, timeout=10.0)
            cursor = conn.cursor()
            
            cursor.execute("INSERT INTO ItemTable (key, value) VALUES (?, ?)", ("aicontext.personalContext", value_json))
            
            conn.commit()
            conn.close()
            print("1|1|0")
        except sqlite3.OperationalError as e:
            if "locked" in str(e).lower():
                print("ERROR: Database is locked. Please close Cursor and try again.", file=sys.stderr)
            else:
                print(f"ERROR: {e}", file=sys.stderr)
            print("1|0|1")
            sys.exit(1)
        except Exception as e:
            print(f"ERROR: {e}", file=sys.stderr)
            print("1|0|1")
            sys.exit(1)
    else:
        print("1|0|0")
except Exception as e:
    print(f"ERROR: {e}", file=sys.stderr)
    print("0|0|1")
    sys.exit(1)
PYTHON_SCRIPT
}

# Function to insert item table entries into ItemTable
insert_item_entries() {
    local db_file="$1"
    local entries_json="$2"
    local execute="$3"
    
    local count=0
    local inserted=0
    local failed=0
    
    # Parse entries and insert
    python3 <<PYTHON_SCRIPT
import json
import sqlite3
import sys

db_file = "$db_file"
entries_json = '''$entries_json'''
execute = "$execute" == "true"

try:
    entries = json.loads(entries_json) if entries_json else []
    count = len(entries)
    inserted = 0
    failed = 0
    
    if execute:
        try:
            conn = sqlite3.connect(db_file, timeout=10.0)
            cursor = conn.cursor()
            
            for entry in entries:
                key = entry.get("key", "")
                value = entry.get("value", "")
                
                # Convert value to JSON string if it's not already a string
                if not isinstance(value, str):
                    value_json = json.dumps(value, ensure_ascii=False)
                else:
                    value_json = value
                
                try:
                    cursor.execute("INSERT INTO ItemTable (key, value) VALUES (?, ?)", (key, value_json))
                    inserted += 1
                except Exception as e:
                    failed += 1
                    print(f"Failed to insert entry {key}: {e}", file=sys.stderr)
            
            conn.commit()
            conn.close()
        except sqlite3.OperationalError as e:
            if "locked" in str(e).lower():
                print("ERROR: Database is locked. Please close Cursor and try again.", file=sys.stderr)
            else:
                print(f"ERROR: {e}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"ERROR: {e}", file=sys.stderr)
            sys.exit(1)
    
    print(f"{count}|{inserted}|{failed}")
except Exception as e:
    print(f"ERROR: {e}", file=sys.stderr)
    sys.exit(1)
PYTHON_SCRIPT
}

# Function to import workspace data from JSON
import_workspace_data() {
    local workspace_id="$1"
    local workspace_data_json="$2"
    local execute="$3"
    
    # Determine database file based on sandbox mode
    local db_file
    if [ "$SANDBOX_MODE" = true ]; then
        db_file="$SANDBOX_DB"
        
        # Ensure sandbox database exists
        if [ ! -f "$db_file" ]; then
            echo "ERROR: Sandbox database not found: $db_file" >&2
            echo "      → Run ./SETUP_SANDBOX_DB.sh first to create the sandbox" >&2
            return 1
        fi
    else
        local workspace_dir="$CURSOR_STORAGE/$workspace_id"
        db_file="$workspace_dir/state.vscdb"
        
        # Check if database exists
        if [ ! -f "$db_file" ]; then
            echo "ERROR: Database not found: $db_file" >&2
            return 1
        fi
    fi
    
    # Check if database is accessible (not locked)
    if ! check_db_accessible "$db_file"; then
        if [ "$SANDBOX_MODE" = true ]; then
            echo "ERROR: Sandbox database is locked: $db_file" >&2
        else
            echo "ERROR: Database is locked (Cursor may be running): $db_file" >&2
            echo "      → Please close Cursor and try again" >&2
        fi
        return 1
    fi
    
    # Extract data from JSON
    local result=$(python3 <<PYTHON_SCRIPT
import json
import sys

workspace_data_json = '''$workspace_data_json'''

try:
    data = json.loads(workspace_data_json)
    
    chat_messages = json.dumps(data.get("chat_messages", []), ensure_ascii=False)
    user_rules = json.dumps(data.get("user_rules"), ensure_ascii=False) if data.get("user_rules") else "null"
    item_table_entries = json.dumps(data.get("item_table_entries", []), ensure_ascii=False)
    
    print(f"CHAT_MESSAGES:{chat_messages}")
    print(f"USER_RULES:{user_rules}")
    print(f"ITEM_TABLE_ENTRIES:{item_table_entries}")
except Exception as e:
    print(f"ERROR: {e}", file=sys.stderr)
    sys.exit(1)
PYTHON_SCRIPT
)
    
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to parse workspace data" >&2
        return 1
    fi
    
    # Extract each section
    local chat_messages_json=$(echo "$result" | grep "^CHAT_MESSAGES:" | sed 's/^CHAT_MESSAGES://')
    local user_rules_json=$(echo "$result" | grep "^USER_RULES:" | sed 's/^USER_RULES://')
    local item_table_entries_json=$(echo "$result" | grep "^ITEM_TABLE_ENTRIES:" | sed 's/^ITEM_TABLE_ENTRIES://')
    
    # Import chat messages
    echo "  Importing chat messages..." >&2
    local chat_result=$(insert_chat_messages "$db_file" "$chat_messages_json" "$execute")
    local chat_count=$(echo "$chat_result" | cut -d'|' -f1)
    local chat_inserted=$(echo "$chat_result" | cut -d'|' -f2)
    local chat_failed=$(echo "$chat_result" | cut -d'|' -f3)
    
    if [ "$execute" = "true" ]; then
        echo "    ✓ Inserted $chat_inserted/$chat_count messages (failed: $chat_failed)" >&2
    else
        echo "    → Would insert $chat_count messages" >&2
    fi
    
    # Import user rules
    echo "  Importing user rules..." >&2
    local rules_result=$(insert_user_rules "$db_file" "$user_rules_json" "$execute")
    local rules_count=$(echo "$rules_result" | cut -d'|' -f1)
    local rules_inserted=$(echo "$rules_result" | cut -d'|' -f2)
    local rules_failed=$(echo "$rules_result" | cut -d'|' -f3)
    
    if [ "$execute" = "true" ]; then
        if [ "$rules_count" -gt 0 ]; then
            echo "    ✓ Inserted user rules (failed: $rules_failed)" >&2
        else
            echo "    → No user rules to import" >&2
        fi
    else
        if [ "$rules_count" -gt 0 ]; then
            echo "    → Would insert user rules" >&2
        else
            echo "    → No user rules to import" >&2
        fi
    fi
    
    # Import item table entries
    echo "  Importing item table entries..." >&2
    local items_result=$(insert_item_entries "$db_file" "$item_table_entries_json" "$execute")
    local items_count=$(echo "$items_result" | cut -d'|' -f1)
    local items_inserted=$(echo "$items_result" | cut -d'|' -f2)
    local items_failed=$(echo "$items_result" | cut -d'|' -f3)
    
    if [ "$execute" = "true" ]; then
        echo "    ✓ Inserted $items_inserted/$items_count entries (failed: $items_failed)" >&2
    else
        echo "    → Would insert $items_count entries" >&2
    fi
    
    # Validate import if in execute mode
    if [ "$execute" = "true" ]; then
        local has_user_rules="0"
        if [ "$rules_inserted" -gt 0 ]; then
            has_user_rules="1"
        fi
        validate_import "$db_file" "$chat_inserted" "$items_inserted" "$has_user_rules"
        local validation_result=$?
        
        if [ $validation_result -ne 0 ] && [ "$SANDBOX_MODE" = true ]; then
            echo "  ⚠ Validation warnings (see above)" >&2
        fi
    fi
    
    # Return summary to stdout (only this line goes to stdout)
    echo "$chat_inserted|$chat_failed|$rules_inserted|$rules_failed|$items_inserted|$items_failed"
    return 0
}

# Print header
echo "=========================================="
if [ "$IMPORT_ALL_WORKSPACES" = true ]; then
    if [ "$SANDBOX_MODE" = true ]; then
        if [ "$EXECUTE_MODE" = true ]; then
            echo "IMPORT ALL WORKSPACES - SANDBOX MODE (EXECUTE)"
            echo "=========================================="
        else
            echo "IMPORT ALL WORKSPACES - SANDBOX MODE (DRY RUN)"
            echo "=========================================="
        fi
    else
        echo "ERROR: --import-all-workspaces requires --sandbox for safety" >&2
        exit 1
    fi
elif [ "$SANDBOX_MODE" = true ]; then
    if [ "$EXECUTE_MODE" = true ]; then
        echo "IMPORT CURSOR CHAT HISTORY - SANDBOX MODE (EXECUTE)"
        echo "=========================================="
    else
        echo "IMPORT CURSOR CHAT HISTORY - SANDBOX MODE (DRY RUN)"
        echo "=========================================="
    fi
elif [ "$EXECUTE_MODE" = true ]; then
    echo "IMPORT CURSOR CHAT HISTORY - EXECUTE MODE (REAL DATABASE)"
    echo "=========================================="
else
    echo "IMPORT CURSOR CHAT HISTORY - DRY RUN MODE"
    echo "=========================================="
fi
echo ""

# Find export file if not specified
if [ -z "$EXPORT_FILE" ]; then
    echo "No export file specified. Looking for most recent export file..."
    
    # Look in chat_recovery_files directory
    if [ -d "$CHAT_RECOVERY_FILES_DIR" ]; then
        EXPORT_FILE=$(find "$CHAT_RECOVERY_FILES_DIR" -name "cursor_chat_history_export*.json" -type f -print0 | xargs -0 ls -t | head -1)
    fi
    
    if [ -z "$EXPORT_FILE" ] || [ ! -f "$EXPORT_FILE" ]; then
        echo "ERROR: No export file found. Please specify a file path or ensure export files exist in:"
        echo "  $CHAT_RECOVERY_FILES_DIR"
        exit 1
    fi
fi

echo "Export File: $EXPORT_FILE"
echo "Cursor Storage: $CURSOR_STORAGE"
echo ""

# Validate export file
if ! validate_export_file "$EXPORT_FILE"; then
    exit 1
fi

# Find current workspace
echo "Finding current workspace..."
CURRENT_WORKSPACE_ID=$(find_current_workspace)

if [ -z "$CURRENT_WORKSPACE_ID" ]; then
    echo "ERROR: Could not find current workspace matching 'app_development/hq' or 'hq.code-workspace'"
    echo "      Make sure you have opened this workspace in Cursor at least once."
    exit 1
fi

echo "Found workspace ID: $CURRENT_WORKSPACE_ID"
if [ "$SANDBOX_MODE" = true ]; then
    echo "Using sandbox database: $SANDBOX_DB"
fi
echo ""

# Confirm real database operation if needed
if [ "$EXECUTE_MODE" = true ] && [ "$SANDBOX_MODE" = false ]; then
    if ! confirm_real_database; then
        exit 1
    fi
    echo ""
fi

# Import all workspaces or single workspace
if [ "$IMPORT_ALL_WORKSPACES" = true ]; then
    echo "Importing data from ALL workspaces in export file..."
    echo ""
    
    # Get summary of all workspaces
    WORKSPACE_SUMMARY=$(python3 <<PYTHON_SCRIPT
import json
import sys

export_file = "$EXPORT_FILE"

try:
    with open(export_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    workspaces = data.get("workspaces", [])
    total_chat = sum(len(w.get("chat_messages", [])) for w in workspaces)
    total_items = sum(len(w.get("item_table_entries", [])) for w in workspaces)
    total_rules = sum(1 for w in workspaces if w.get("user_rules"))
    
    print(f"{len(workspaces)}|{total_chat}|{total_items}|{total_rules}")
except Exception as e:
    print(f"ERROR: {e}", file=sys.stderr)
    sys.exit(1)
PYTHON_SCRIPT
)
    
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to analyze export file" >&2
        exit 1
    fi
    
    TOTAL_WORKSPACES=$(echo "$WORKSPACE_SUMMARY" | cut -d'|' -f1)
    TOTAL_CHAT_EXPECTED=$(echo "$WORKSPACE_SUMMARY" | cut -d'|' -f2)
    TOTAL_ITEMS_EXPECTED=$(echo "$WORKSPACE_SUMMARY" | cut -d'|' -f3)
    TOTAL_RULES_EXPECTED=$(echo "$WORKSPACE_SUMMARY" | cut -d'|' -f4)
    
    echo "Found $TOTAL_WORKSPACES workspace(s) in export file:"
    echo "  - Total chat messages: $TOTAL_CHAT_EXPECTED"
    echo "  - Total item table entries: $TOTAL_ITEMS_EXPECTED"
    echo "  - Workspaces with user rules: $TOTAL_RULES_EXPECTED"
    echo ""
    
    # Import all workspaces using Python script
    IMPORT_RESULT=$(python3 <<PYTHON_SCRIPT
import json
import sqlite3
import sys
import subprocess
import os

export_file = "$EXPORT_FILE"
sandbox_db = "$SANDBOX_DB"
execute_mode = "$EXECUTE_MODE" == "true"

# Initialize totals
total_chat_inserted = 0
total_chat_failed = 0
total_rules_inserted = 0
total_rules_failed = 0
total_items_inserted = 0
total_items_failed = 0

try:
    with open(export_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    workspaces = data.get("workspaces", [])
    total_workspaces = len(workspaces)
    
    # Process each workspace
    for idx, workspace in enumerate(workspaces, 1):
        workspace_id = workspace.get("workspace_id", "unknown")
        chat_messages = workspace.get("chat_messages", [])
        user_rules = workspace.get("user_rules")
        item_table_entries = workspace.get("item_table_entries", [])
        
        print(f"Processing workspace {idx}/{total_workspaces}: {workspace_id[:20]}...", file=sys.stderr)
        print(f"  Chat messages: {len(chat_messages)}, Items: {len(item_table_entries)}", file=sys.stderr)
        
        if execute_mode:
            try:
                conn = sqlite3.connect(sandbox_db, timeout=10.0)
                cursor = conn.cursor()
                
                # Import chat messages
                chat_inserted = 0
                chat_failed = 0
                for msg in chat_messages:
                    key = msg.get("key", "")
                    value = msg.get("value", "")
                    
                    if not isinstance(value, str):
                        value_json = json.dumps(value, ensure_ascii=False)
                    else:
                        value_json = value
                    
                    try:
                        cursor.execute("INSERT OR IGNORE INTO cursorDiskKV (key, value) VALUES (?, ?)", (key, value_json))
                        if cursor.rowcount > 0:
                            chat_inserted += 1
                    except Exception as e:
                        chat_failed += 1
                        print(f"    Failed to insert chat {key}: {e}", file=sys.stderr)
                
                # Import user rules (only if present)
                rules_inserted = 0
                rules_failed = 0
                if user_rules:
                    try:
                        if not isinstance(user_rules, str):
                            value_json = json.dumps(user_rules, ensure_ascii=False)
                        else:
                            value_json = user_rules
                        cursor.execute("INSERT OR REPLACE INTO ItemTable (key, value) VALUES (?, ?)", ("aicontext.personalContext", value_json))
                        rules_inserted = 1
                    except Exception as e:
                        rules_failed = 1
                        print(f"    Failed to insert user rules: {e}", file=sys.stderr)
                
                # Import item table entries
                items_inserted = 0
                items_failed = 0
                for entry in item_table_entries:
                    key = entry.get("key", "")
                    value = entry.get("value", "")
                    
                    if not isinstance(value, str):
                        value_json = json.dumps(value, ensure_ascii=False)
                    else:
                        value_json = value
                    
                    try:
                        # Use INSERT OR REPLACE to handle duplicate keys (latest wins)
                        cursor.execute("INSERT OR REPLACE INTO ItemTable (key, value) VALUES (?, ?)", (key, value_json))
                        items_inserted += 1
                    except Exception as e:
                        items_failed += 1
                        print(f"    Failed to insert item {key}: {e}", file=sys.stderr)
                
                conn.commit()
                conn.close()
                
                total_chat_inserted += chat_inserted
                total_chat_failed += chat_failed
                total_rules_inserted += rules_inserted
                total_rules_failed += rules_failed
                total_items_inserted += items_inserted
                total_items_failed += items_failed
                
                print(f"  ✓ Inserted: {chat_inserted} chats, {items_inserted} items", file=sys.stderr)
            except Exception as e:
                print(f"  ✗ Failed to import workspace: {e}", file=sys.stderr)
        else:
            # Dry run - just count
            total_chat_inserted += len(chat_messages)
            if user_rules:
                total_rules_inserted += 1
            total_items_inserted += len(item_table_entries)
            print(f"  → Would insert: {len(chat_messages)} chats, {len(item_table_entries)} items", file=sys.stderr)
        
        print("", file=sys.stderr)
    
    # Return summary
    print(f"{total_chat_inserted}|{total_chat_failed}|{total_rules_inserted}|{total_rules_failed}|{total_items_inserted}|{total_items_failed}")
    
except Exception as e:
    print(f"ERROR: {e}", file=sys.stderr)
    sys.exit(1)
PYTHON_SCRIPT
)
    
    EXIT_CODE=$?
    
    if [ $EXIT_CODE -ne 0 ]; then
        echo "ERROR: Failed to import all workspaces" >&2
        exit 1
    fi
    
    # Parse summary
    SUMMARY_LINE=$(echo "$IMPORT_RESULT" | tail -1)
    CHAT_INSERTED=$(echo "$SUMMARY_LINE" | cut -d'|' -f1)
    CHAT_FAILED=$(echo "$SUMMARY_LINE" | cut -d'|' -f2)
    RULES_INSERTED=$(echo "$SUMMARY_LINE" | cut -d'|' -f3)
    RULES_FAILED=$(echo "$SUMMARY_LINE" | cut -d'|' -f4)
    ITEMS_INSERTED=$(echo "$SUMMARY_LINE" | cut -d'|' -f5)
    ITEMS_FAILED=$(echo "$SUMMARY_LINE" | cut -d'|' -f6)
else
    # Single workspace import (original logic)
    echo "Extracting workspace data from export file..."
    WORKSPACE_DATA=$(python3 <<PYTHON_SCRIPT
import json
import sys

export_file = "$EXPORT_FILE"
workspace_id = "$CURRENT_WORKSPACE_ID"

try:
    with open(export_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Find matching workspace
    workspace_found = None
    for workspace in data.get("workspaces", []):
        if workspace.get("workspace_id") == workspace_id:
            workspace_found = workspace
            break
    
    if not workspace_found:
        print("ERROR: Workspace ID not found in export file", file=sys.stderr)
        sys.exit(1)
    
    print(json.dumps(workspace_found, ensure_ascii=False))
except Exception as e:
    print(f"ERROR: {e}", file=sys.stderr)
    sys.exit(1)
PYTHON_SCRIPT
)

    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to extract workspace data from export file"
        exit 1
    fi

    # Check if workspace data is empty
    if [ -z "$WORKSPACE_DATA" ]; then
        echo "ERROR: No data found for workspace ID: $CURRENT_WORKSPACE_ID"
        exit 1
    fi

    echo "✓ Found workspace data in export file"
    echo ""

    # Import the data
    echo "Importing data..."
    echo ""

    SUMMARY=$(import_workspace_data "$CURRENT_WORKSPACE_ID" "$WORKSPACE_DATA" "$EXECUTE_MODE")
    EXIT_CODE=$?

    if [ $EXIT_CODE -ne 0 ]; then
        echo ""
        echo "ERROR: Failed to import data"
        exit 1
    fi

    # Parse summary (get last line in case there's any extra output)
    SUMMARY_LINE=$(echo "$SUMMARY" | tail -1)
    CHAT_INSERTED=$(echo "$SUMMARY_LINE" | cut -d'|' -f1)
    CHAT_FAILED=$(echo "$SUMMARY_LINE" | cut -d'|' -f2)
    RULES_INSERTED=$(echo "$SUMMARY_LINE" | cut -d'|' -f3)
    RULES_FAILED=$(echo "$SUMMARY_LINE" | cut -d'|' -f4)
    ITEMS_INSERTED=$(echo "$SUMMARY_LINE" | cut -d'|' -f5)
    ITEMS_FAILED=$(echo "$SUMMARY_LINE" | cut -d'|' -f6)
fi

# Print summary
echo ""
echo "=========================================="
echo "SUMMARY"
echo "=========================================="
if [ "$IMPORT_ALL_WORKSPACES" = true ]; then
    echo "IMPORTED FROM ALL WORKSPACES:"
    echo "  Workspaces processed: $TOTAL_WORKSPACES"
    echo "  Expected chat messages: $TOTAL_CHAT_EXPECTED"
    echo "  Expected item entries: $TOTAL_ITEMS_EXPECTED"
    echo ""
fi

if [ "$EXECUTE_MODE" = true ]; then
    echo "Chat messages inserted: $CHAT_INSERTED (failed: $CHAT_FAILED)"
    echo "User rules inserted: $RULES_INSERTED (failed: $RULES_FAILED)"
    echo "Item table entries inserted: $ITEMS_INSERTED (failed: $ITEMS_FAILED)"
    echo ""
    
    if [ "$IMPORT_ALL_WORKSPACES" = true ]; then
        echo "✓ Consolidated import completed in sandbox"
        echo ""
        echo "All workspace data has been imported into the sandbox database."
        echo "Note: Duplicate keys in item table were replaced with latest values."
    elif [ "$SANDBOX_MODE" = true ]; then
        echo "✓ Import completed in sandbox"
        echo ""
        echo "To compare sandbox to export file, run:"
        echo "  ./TEST_IMPORT.sh \"$EXPORT_FILE\""
        echo ""
        echo "To import to real database (after validation), run:"
        echo "  ./IMPORT_CURSOR_CHAT_HISTORY.sh \"$EXPORT_FILE\" --execute"
    else
        echo "✓ Import completed to real database"
    fi
else
    echo "Chat messages: Would insert (see details above)"
    echo "User rules: Would insert (see details above)"
    echo "Item table entries: Would insert (see details above)"
    echo ""
    echo "This was a dry run. No data was actually imported."
    echo ""
    if [ "$SANDBOX_MODE" = true ]; then
        echo "To actually import to sandbox, run:"
        echo "  ./IMPORT_CURSOR_CHAT_HISTORY.sh \"$EXPORT_FILE\" --sandbox --execute"
    else
        echo "To actually import the data, run:"
        echo "  ./IMPORT_CURSOR_CHAT_HISTORY.sh \"$EXPORT_FILE\" --execute"
        echo ""
        echo "Or test in sandbox first:"
        echo "  ./IMPORT_CURSOR_CHAT_HISTORY.sh \"$EXPORT_FILE\" --sandbox --execute"
    fi
fi
echo "=========================================="
