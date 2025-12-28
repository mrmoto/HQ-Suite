#!/bin/bash
# Uninstall DigiDoc File Watcher LaunchDaemon (requires sudo)

set -e

PLIST_NAME="com.digidoc.filewatcher.daemon.plist"
PLIST_DEST="/Library/LaunchDaemons/$PLIST_NAME"

echo "=========================================="
echo "DigiDoc File Watcher - LaunchDaemon Uninstall"
echo "=========================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "ERROR: This script must be run with sudo"
    echo "Usage: sudo ./uninstall_launchdaemon.sh"
    exit 1
fi

# Stop the service
if launchctl list | grep -q "com.digidoc.filewatcher"; then
    echo "Stopping service..."
    launchctl stop com.digidoc.filewatcher
    echo "✓ Service stopped"
fi

# Unload the service
if [ -f "$PLIST_DEST" ]; then
    echo "Unloading LaunchDaemon..."
    launchctl unload "$PLIST_DEST" 2>/dev/null || true
    echo "✓ LaunchDaemon unloaded"
    
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
