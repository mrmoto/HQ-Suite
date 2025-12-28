#!/bin/bash
# Install DigiDoc File Watcher as macOS LaunchAgent (user-level)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLIST_NAME="com.digidoc.filewatcher.plist"
PLIST_SOURCE="$SCRIPT_DIR/$PLIST_NAME"
PLIST_DEST="$HOME/Library/LaunchAgents/$PLIST_NAME"

echo "=========================================="
echo "DigiDoc File Watcher - LaunchAgent Install"
echo "=========================================="
echo ""

# Check if plist exists
if [ ! -f "$PLIST_SOURCE" ]; then
    echo "ERROR: Plist file not found: $PLIST_SOURCE"
    exit 1
fi

# Copy plist to LaunchAgents
echo "Copying plist to LaunchAgents..."
cp "$PLIST_SOURCE" "$PLIST_DEST"
echo "✓ Plist copied to: $PLIST_DEST"

# Load the service
echo ""
echo "Loading LaunchAgent..."
launchctl load "$PLIST_DEST" 2>/dev/null || launchctl load -w "$PLIST_DEST"
echo "✓ LaunchAgent loaded"

# Start the service
echo ""
echo "Starting service..."
launchctl start com.digidoc.filewatcher
echo "✓ Service started"

echo ""
echo "=========================================="
echo "Installation complete!"
echo "=========================================="
echo ""
echo "To check status: launchctl list | grep digidoc"
echo "To view logs: tail -f ~/Dropbox/cloud_storage/DigiDoc/logs/file_watcher_digidoc.log"
echo "To stop: launchctl stop com.digidoc.filewatcher"
echo "To uninstall: ./uninstall_launchagent.sh"
