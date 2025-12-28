#!/bin/bash

# Convenience script to test Cursor chat history import in sandbox
# Usage:
#   ./TEST_IMPORT.sh [export_file.json]  # Test import in sandbox and validate

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SANDBOX_DIR="$SCRIPT_DIR/sandbox"
SANDBOX_DB="$SANDBOX_DIR/state.vscdb"

# Parse export file argument
EXPORT_FILE=""
for arg in "$@"; do
    if [ -f "$arg" ] || [ -f "../chat_recovery_files/$arg" ] || [ -f "../../chat_recovery_files/$arg" ]; then
        if [ -f "$arg" ]; then
            EXPORT_FILE="$arg"
        elif [ -f "../chat_recovery_files/$arg" ]; then
            EXPORT_FILE="../chat_recovery_files/$arg"
        elif [ -f "../../chat_recovery_files/$arg" ]; then
            EXPORT_FILE="../../chat_recovery_files/$arg"
        fi
    fi
done

# Print header
echo "=========================================="
echo "TEST IMPORT IN SANDBOX"
echo "=========================================="
echo ""

# Check if sandbox exists, create if not
if [ ! -f "$SANDBOX_DB" ]; then
    echo "Sandbox database not found. Creating sandbox..."
    echo ""
    if [ -f "$SCRIPT_DIR/SETUP_SANDBOX_DB.sh" ]; then
        bash "$SCRIPT_DIR/SETUP_SANDBOX_DB.sh"
        if [ $? -ne 0 ]; then
            echo "ERROR: Failed to create sandbox database" >&2
            exit 1
        fi
        echo ""
    else
        echo "ERROR: SETUP_SANDBOX_DB.sh not found" >&2
        exit 1
    fi
fi

# Run import in sandbox mode
echo "Running import in sandbox mode..."
echo ""
bash "$SCRIPT_DIR/IMPORT_CURSOR_CHAT_HISTORY.sh" "$EXPORT_FILE" --sandbox --execute
IMPORT_EXIT_CODE=$?

echo ""

# If import succeeded and export file is provided, compare results
if [ $IMPORT_EXIT_CODE -eq 0 ] && [ -n "$EXPORT_FILE" ] && [ -f "$EXPORT_FILE" ]; then
    echo "=========================================="
    echo "COMPARING SANDBOX TO EXPORT FILE"
    echo "=========================================="
    echo ""
    
    # Extract workspace ID (needed for comparison)
    CURSOR_STORAGE="$HOME/Library/Application Support/Cursor/User/workspaceStorage"
    CURRENT_WORKSPACE_ID=""
    
    if [ -d "$CURSOR_STORAGE" ]; then
        while IFS= read -r -d '' dir; do
            if [ -f "$dir/workspace.json" ]; then
                workspace_path=$(cat "$dir/workspace.json" 2>/dev/null | python3 -c "import sys, json; data = json.load(sys.stdin); print(data.get('workspace', ''))" 2>/dev/null)
                
                if echo "$workspace_path" | grep -q "app_development/hq" || echo "$workspace_path" | grep -q "hq.code-workspace"; then
                    CURRENT_WORKSPACE_ID=$(basename "$dir")
                    break
                fi
            fi
        done < <(find "$CURSOR_STORAGE" -mindepth 1 -maxdepth 1 -type d -print0 2>/dev/null)
    fi
    
    if [ -n "$CURRENT_WORKSPACE_ID" ]; then
        # Use Python to compare
        python3 <<PYTHON_SCRIPT
import json
import sqlite3
import sys

sandbox_db = "$SANDBOX_DB"
export_file = "$EXPORT_FILE"
workspace_id = "$CURRENT_WORKSPACE_ID"

try:
    # Load export file
    with open(export_file, "r", encoding="utf-8") as f:
        export_data = json.load(f)
    
    # Find matching workspace
    workspace_found = None
    for workspace in export_data.get("workspaces", []):
        if workspace.get("workspace_id") == workspace_id:
            workspace_found = workspace
            break
    
    if not workspace_found:
        print("ERROR: Workspace not found in export file", file=sys.stderr)
        sys.exit(1)
    
    # Get expected counts
    expected_chat = len(workspace_found.get("chat_messages", []))
    expected_items = len(workspace_found.get("item_table_entries", []))
    has_user_rules = 1 if workspace_found.get("user_rules") else 0
    
    # Get actual counts from sandbox
    conn = sqlite3.connect(sandbox_db)
    cursor = conn.cursor()
    
    actual_chat = cursor.execute("SELECT COUNT(*) FROM cursorDiskKV WHERE key LIKE 'bubbleId:%';").fetchone()[0]
    actual_items = cursor.execute("SELECT COUNT(*) FROM ItemTable;").fetchone()[0]
    actual_user_rules = cursor.execute("SELECT COUNT(*) FROM ItemTable WHERE key = 'aicontext.personalContext';").fetchone()[0]
    
    conn.close()
    
    # Compare
    print("Expected vs Actual:")
    print(f"  Chat messages:    {expected_chat:4d} vs {actual_chat:4d}", end="")
    if expected_chat == actual_chat:
        print(" ✓")
    else:
        print(" ✗")
    
    expected_total_items = expected_items + has_user_rules
    print(f"  Item table:       {expected_total_items:4d} vs {actual_items:4d}", end="")
    if expected_total_items == actual_items:
        print(" ✓")
    else:
        print(" ✗")
    
    if has_user_rules:
        print(f"  User rules:       {'Yes':4s} vs {'Yes' if actual_user_rules > 0 else 'No':4s}", end="")
        if actual_user_rules > 0:
            print(" ✓")
        else:
            print(" ✗")
    
    # Check if all chat message keys match
    export_chat_keys = set(msg.get("key", "") for msg in workspace_found.get("chat_messages", []))
    sandbox_chat_keys = set()
    
    conn = sqlite3.connect(sandbox_db)
    cursor = conn.cursor()
    for row in cursor.execute("SELECT key FROM cursorDiskKV WHERE key LIKE 'bubbleId:%';"):
        sandbox_chat_keys.add(row[0])
    conn.close()
    
    missing_in_sandbox = export_chat_keys - sandbox_chat_keys
    extra_in_sandbox = sandbox_chat_keys - export_chat_keys
    
    if missing_in_sandbox:
        print(f"\n  ⚠ Missing {len(missing_in_sandbox)} chat messages in sandbox")
    if extra_in_sandbox:
        print(f"  ⚠ Extra {len(extra_in_sandbox)} chat messages in sandbox (may be from previous tests)")
    
    if not missing_in_sandbox and not extra_in_sandbox:
        print("\n  ✓ All chat message keys match")
    
    # Overall result
    if expected_chat == actual_chat and expected_total_items == actual_items:
        if has_user_rules == 0 or actual_user_rules > 0:
            print("\n✓ Comparison passed - sandbox matches export file")
            sys.exit(0)
        else:
            print("\n✗ Comparison failed - user rules missing")
            sys.exit(1)
    else:
        print("\n✗ Comparison failed - counts don't match")
        sys.exit(1)
        
except Exception as e:
    print(f"ERROR: {e}", file=sys.stderr)
    sys.exit(1)
PYTHON_SCRIPT
    
    COMPARE_EXIT_CODE=$?
    echo ""
    
    if [ $COMPARE_EXIT_CODE -eq 0 ]; then
        echo "=========================================="
        echo "✓ SANDBOX TEST PASSED"
        echo "=========================================="
        echo ""
        echo "The import was successful and matches the export file."
        echo "You can now safely import to the real database:"
        echo "  ./IMPORT_CURSOR_CHAT_HISTORY.sh \"$EXPORT_FILE\" --execute"
    else
        echo "=========================================="
        echo "✗ SANDBOX TEST FAILED"
        echo "=========================================="
        echo ""
        echo "The import did not match the export file. Review the errors above."
        echo "Do not import to the real database until issues are resolved."
        exit 1
    fi
else
    if [ $IMPORT_EXIT_CODE -eq 0 ]; then
        echo "=========================================="
        echo "✓ SANDBOX IMPORT COMPLETED"
        echo "=========================================="
        echo ""
        echo "Import completed. To compare with export file, provide the export file:"
        echo "  ./TEST_IMPORT.sh [export_file.json]"
    else
        echo "=========================================="
        echo "✗ SANDBOX IMPORT FAILED"
        echo "=========================================="
        echo ""
        echo "The import failed. Review the errors above."
        exit 1
    fi
fi
