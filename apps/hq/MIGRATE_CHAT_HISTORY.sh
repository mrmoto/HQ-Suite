#!/bin/bash

# Script to migrate chat history from apps/hq workspace to app_development/hq workspace
# This preserves chat history when using the multi-root workspace file

set -e

CURSOR_STORAGE="$HOME/Library/Application Support/Cursor/User/workspaceStorage"
APPS_HQ_PATH="file:///Users/scottroberts/Library/CloudStorage/Dropbox/apps/hq"
WORKSPACE_FILE_PATH="file:///Users/scottroberts/Library/CloudStorage/Dropbox/app_development/hq/hq.code-workspace"

echo "=== Chat History Migration Script ==="
echo ""
echo "Detecting workspace IDs..."
echo ""

# Find old workspace (apps/hq folder)
OLD_WORKSPACE_ID=""
for dir in "$CURSOR_STORAGE"/*/; do
    if [ -f "$dir/workspace.json" ]; then
        if grep -q "$APPS_HQ_PATH" "$dir/workspace.json" 2>/dev/null; then
            OLD_WORKSPACE_ID=$(basename "$dir")
            echo "Found old workspace: $OLD_WORKSPACE_ID (apps/hq)"
            break
        fi
    fi
done

# Find new workspace (workspace file)
NEW_WORKSPACE_ID=""
for dir in "$CURSOR_STORAGE"/*/; do
    if [ -f "$dir/workspace.json" ]; then
        if grep -q "$WORKSPACE_FILE_PATH" "$dir/workspace.json" 2>/dev/null; then
            NEW_WORKSPACE_ID=$(basename "$dir")
            echo "Found new workspace: $NEW_WORKSPACE_ID (workspace file)"
            break
        fi
    fi
done

if [ -z "$OLD_WORKSPACE_ID" ]; then
    echo "ERROR: Could not find workspace for apps/hq"
    echo "Make sure you've opened apps/hq as a folder in Cursor at least once"
    exit 1
fi

if [ -z "$NEW_WORKSPACE_ID" ]; then
    echo "ERROR: Could not find workspace for workspace file"
    echo "Please open the workspace file first: app_development/hq/hq.code-workspace"
    exit 1
fi

OLD_WORKSPACE_DIR="$CURSOR_STORAGE/$OLD_WORKSPACE_ID"
NEW_WORKSPACE_DIR="$CURSOR_STORAGE/$NEW_WORKSPACE_ID"

echo ""
echo "Old workspace: $OLD_WORKSPACE_ID (apps/hq)"
echo "New workspace: $NEW_WORKSPACE_ID (app_development/hq workspace file)"
echo ""

# Verify directories exist
if [ ! -d "$OLD_WORKSPACE_DIR" ]; then
    echo "ERROR: Old workspace directory not found: $OLD_WORKSPACE_DIR"
    exit 1
fi

if [ ! -d "$NEW_WORKSPACE_DIR" ]; then
    echo "ERROR: New workspace directory not found: $NEW_WORKSPACE_DIR"
    exit 1
fi

# Backup new workspace first
echo "Creating backup of new workspace..."
BACKUP_DIR="$NEW_WORKSPACE_DIR.backup.$(date +%Y%m%d_%H%M%S)"
cp -R "$NEW_WORKSPACE_DIR" "$BACKUP_DIR"
echo "Backup created: $BACKUP_DIR"
echo ""

# Copy state.vscdb (contains chat history, rules, preferences, and workspace state)
echo "Copying state.vscdb (chat history + AI learning)..."
echo "  This includes:"
echo "    - All chat messages (conversation history)"
echo "    - Rules and preferences discussed in chat"
echo "    - Architectural decisions documented in chat"
echo "    - Workspace state and metadata"
if [ -f "$OLD_WORKSPACE_DIR/state.vscdb" ]; then
    cp "$OLD_WORKSPACE_DIR/state.vscdb" "$NEW_WORKSPACE_DIR/state.vscdb"
    echo "  ✓ Copied state.vscdb ($(du -h "$OLD_WORKSPACE_DIR/state.vscdb" | cut -f1))"
else
    echo "  ⚠ Warning: state.vscdb not found in old workspace"
fi

# Copy state.vscdb.backup if it exists
if [ -f "$OLD_WORKSPACE_DIR/state.vscdb.backup" ]; then
    cp "$OLD_WORKSPACE_DIR/state.vscdb.backup" "$NEW_WORKSPACE_DIR/state.vscdb.backup"
    echo "  ✓ Copied state.vscdb.backup"
fi

# Copy anysphere.cursor-retrieval directory (contains code context and embeddings)
echo ""
echo "Copying cursor-retrieval data (code understanding)..."
echo "  This includes:"
echo "    - File embeddings (AI's understanding of your codebase)"
echo "    - Code context and structure"
echo "    - High-level folder descriptions"
if [ -d "$OLD_WORKSPACE_DIR/anysphere.cursor-retrieval" ]; then
    rm -rf "$NEW_WORKSPACE_DIR/anysphere.cursor-retrieval"
    cp -R "$OLD_WORKSPACE_DIR/anysphere.cursor-retrieval" "$NEW_WORKSPACE_DIR/"
    echo "  ✓ Copied cursor-retrieval data"
else
    echo "  ⚠ Warning: cursor-retrieval directory not found in old workspace"
fi

echo ""
echo "=== Migration Complete ==="
echo ""
echo "WHAT WAS PRESERVED:"
echo "  ✓ Chat messages (all conversation history)"
echo "  ✓ Rules and preferences (discussed in chat)"
echo "  ✓ Architectural decisions (documented in chat)"
echo "  ✓ Code embeddings (AI's understanding of your codebase)"
echo "  ✓ Workspace state and metadata"
echo ""
echo "NOTE: The AI's 'learning' (rules, preferences, architectural decisions)"
echo "      is primarily stored in the chat messages themselves. By copying"
echo "      state.vscdb, we preserve all of this context."
echo ""
echo "Next steps:"
echo "1. Close Cursor completely (Cmd+Q)"
echo "2. Reopen Cursor"
echo "3. Open the workspace file: app_development/hq/hq.code-workspace"
echo "4. Chat history and AI context should now be available"
echo ""
echo "If something goes wrong, restore from: $BACKUP_DIR"

