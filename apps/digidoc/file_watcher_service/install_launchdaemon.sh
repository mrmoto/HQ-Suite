#!/bin/bash
# Install DigiDoc File Watcher as macOS LaunchDaemon (system-level, requires sudo)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLIST_NAME="com.digidoc.filewatcher.daemon.plist"
PLIST_SOURCE="$SCRIPT_DIR/$PLIST_NAME"
PLIST_DEST="/Library/LaunchDaemons/$PLIST_NAME"

echo "=========================================="
echo "DigiDoc File Watcher - LaunchDaemon Install"
echo "=========================================="
echo ""
echo "WARNING: This requires sudo/root access"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "ERROR: This script must be run with sudo"
    echo "Usage: sudo ./install_launchdaemon.sh"
    exit 1
fi

# Check if plist exists
if [ ! -f "$PLIST_SOURCE" ]; then
    echo "ERROR: Plist file not found: $PLIST_SOURCE"
    exit 1
fi

# Copy plist to LaunchDaemons
echo "Copying plist to LaunchDaemons..."
cp "$PLIST_SOURCE" "$PLIST_DEST"
chown root:wheel "$PLIST_DEST"
chmod 644 "$PLIST_DEST"
echo "✓ Plist copied to: $PLIST_DEST"

# Load the service
echo ""
echo "Loading LaunchDaemon..."
launchctl load "$PLIST_DEST" 2>/dev/null || launchctl load -w "$PLIST_DEST"
echo "✓ LaunchDaemon loaded"

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
echo "To check status: sudo launchctl list | grep digidoc"
echo "To view logs: sudo tail -f /var/log/digidoc_filewatcher.log"
echo "To stop: sudo launchctl stop com.digidoc.filewatcher"
echo "To uninstall: sudo ./uninstall_launchdaemon.sh"
