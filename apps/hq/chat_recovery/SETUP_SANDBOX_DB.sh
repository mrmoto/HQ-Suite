#!/bin/bash

# Script to setup sandbox database for testing Cursor chat history imports
# Usage:
#   ./SETUP_SANDBOX_DB.sh              # Create/reset sandbox database
#   ./SETUP_SANDBOX_DB.sh --copy-data   # Copy existing data from real database for realistic testing

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SANDBOX_DIR="$SCRIPT_DIR/sandbox"
SANDBOX_DB="$SANDBOX_DIR/state.vscdb"

# Cursor storage location (for copying data)
CURSOR_STORAGE="$HOME/Library/Application Support/Cursor/User/workspaceStorage"

# Parse arguments
COPY_DATA=false
if [ "$1" == "--copy-data" ]; then
    COPY_DATA=true
fi

# Print header
echo "=========================================="
echo "SETUP SANDBOX DATABASE"
echo "=========================================="
echo ""

# Create sandbox directory if it doesn't exist
if [ ! -d "$SANDBOX_DIR" ]; then
    echo "Creating sandbox directory: $SANDBOX_DIR"
    mkdir -p "$SANDBOX_DIR"
fi

# Remove existing database if it exists
if [ -f "$SANDBOX_DB" ]; then
    echo "Removing existing sandbox database..."
    rm -f "$SANDBOX_DB"
fi

# Create new database with schema
echo "Creating sandbox database with schema..."
sqlite3 "$SANDBOX_DB" <<SQL
-- Create cursorDiskKV table (stores chat messages)
CREATE TABLE IF NOT EXISTS cursorDiskKV (
    key TEXT PRIMARY KEY,
    value TEXT
);

-- Create ItemTable (stores workspace settings and data)
CREATE TABLE IF NOT EXISTS ItemTable (
    key TEXT PRIMARY KEY,
    value TEXT
);
SQL

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create sandbox database" >&2
    exit 1
fi

echo "✓ Sandbox database created: $SANDBOX_DB"
echo ""

# Verify tables were created
echo "Verifying schema..."
TABLES=$(sqlite3 "$SANDBOX_DB" "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")

if echo "$TABLES" | grep -q "cursorDiskKV" && echo "$TABLES" | grep -q "ItemTable"; then
    echo "✓ Tables created successfully:"
    echo "  - cursorDiskKV"
    echo "  - ItemTable"
else
    echo "ERROR: Tables not created correctly" >&2
    exit 1
fi
echo ""

# Optionally copy data from real database
if [ "$COPY_DATA" = true ]; then
    echo "Copying data from real database..."
    
    # Find current workspace
    WORKSPACE_ID=""
    if [ -d "$CURSOR_STORAGE" ]; then
        while IFS= read -r -d '' dir; do
            if [ -f "$dir/workspace.json" ]; then
                workspace_path=$(cat "$dir/workspace.json" 2>/dev/null | python3 -c "import sys, json; data = json.load(sys.stdin); print(data.get('workspace', ''))" 2>/dev/null)
                
                if echo "$workspace_path" | grep -q "app_development/hq" || echo "$workspace_path" | grep -q "hq.code-workspace"; then
                    WORKSPACE_ID=$(basename "$dir")
                    break
                fi
            fi
        done < <(find "$CURSOR_STORAGE" -mindepth 1 -maxdepth 1 -type d -print0 2>/dev/null)
    fi
    
    if [ -n "$WORKSPACE_ID" ]; then
        REAL_DB="$CURSOR_STORAGE/$WORKSPACE_ID/state.vscdb"
        
        if [ -f "$REAL_DB" ]; then
            # Check if database is accessible
            if sqlite3 -readonly "$REAL_DB" "SELECT 1;" >/dev/null 2>&1; then
                echo "  Found workspace: $WORKSPACE_ID"
                echo "  Copying data from: $REAL_DB"
                
                # Copy cursorDiskKV data
                sqlite3 "$REAL_DB" "SELECT key, value FROM cursorDiskKV;" | while IFS='|' read -r key value; do
                    if [ -n "$key" ] && [ -n "$value" ]; then
                        sqlite3 "$SANDBOX_DB" "INSERT OR IGNORE INTO cursorDiskKV (key, value) VALUES (\"$(echo "$key" | sed 's/"/""/g')\", \"$(echo "$value" | sed 's/"/""/g')\");"
                    fi
                done
                
                # Copy ItemTable data
                sqlite3 "$REAL_DB" "SELECT key, value FROM ItemTable;" | while IFS='|' read -r key value; do
                    if [ -n "$key" ] && [ -n "$value" ]; then
                        sqlite3 "$SANDBOX_DB" "INSERT OR IGNORE INTO ItemTable (key, value) VALUES (\"$(echo "$key" | sed 's/"/""/g')\", \"$(echo "$value" | sed 's/"/""/g')\");"
                    fi
                done
                
                # Count copied records
                CHAT_COUNT=$(sqlite3 "$SANDBOX_DB" "SELECT COUNT(*) FROM cursorDiskKV;")
                ITEM_COUNT=$(sqlite3 "$SANDBOX_DB" "SELECT COUNT(*) FROM ItemTable;")
                
                echo "  ✓ Copied $CHAT_COUNT chat messages"
                echo "  ✓ Copied $ITEM_COUNT item table entries"
            else
                echo "  ⚠ Real database is locked (Cursor may be running)"
                echo "     → Sandbox created empty. Close Cursor and use --copy-data again if needed."
            fi
        else
            echo "  ⚠ Real database not found: $REAL_DB"
            echo "     → Sandbox created empty."
        fi
    else
        echo "  ⚠ Could not find current workspace"
        echo "     → Sandbox created empty."
    fi
    echo ""
fi

# Show final status
CHAT_COUNT=$(sqlite3 "$SANDBOX_DB" "SELECT COUNT(*) FROM cursorDiskKV;")
ITEM_COUNT=$(sqlite3 "$SANDBOX_DB" "SELECT COUNT(*) FROM ItemTable;")

echo "=========================================="
echo "SANDBOX DATABASE READY"
echo "=========================================="
echo "Location: $SANDBOX_DB"
echo "Chat messages: $CHAT_COUNT"
echo "Item table entries: $ITEM_COUNT"
echo ""
echo "You can now test imports using:"
echo "  ./IMPORT_CURSOR_CHAT_HISTORY.sh --sandbox --execute [export_file.json]"
echo ""
echo "To reset the sandbox, run this script again."
echo "=========================================="
