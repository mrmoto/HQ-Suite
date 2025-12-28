#!/bin/bash
# Uninstall DigiDoc File Watcher LaunchAgent

set -e

PLIST_NAME="com.digidoc.filewatcher.plist"
PLIST_DEST="$HOME/Library/LaunchAgents/$PLIST_NAME"

echo "=========================================="
echo "DigiDoc File Watcher - LaunchAgent Uninstall"
echo "=========================================="
echo ""

# Stop the service
if launchctl list | grep -q "com.digidoc.filewatcher"; then
    echo "Stopping service..."
    launchctl stop com.digidoc.filewatcher
    echo "✓ Service stopped"
fi

# Unload the service
if [ -f "$PLIST_DEST" ]; then
    echo "Unloading LaunchAgent..."
    launchctl unload "$PLIST_DEST" 2>/dev/null || true
    echo "✓ LaunchAgent unloaded"
    
    # Remove plist
    echo "Removing plist..."
    rm "$PLIST_DEST"
    echo "✓ Plist removed"
else
    echo "Plist not found at: $PLIST_DEST"
fi

echo ""
echo "=========================================="
echo "Uninstallation complete!"
echo "=========================================="
