#!/bin/bash

# Script to delete scanner, SMB, and FTP setup-related files
# Usage:
#   ./DELETE_SCANNER_FILES.sh          # Dry-run mode (default)
#   ./DELETE_SCANNER_FILES.sh --execute # Actually delete files

set -e

# Determine if we're in execute mode
EXECUTE_MODE=false
if [ "$1" == "--execute" ]; then
    EXECUTE_MODE=true
fi

# Get the script directory (root of the project)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Arrays of files to delete
declare -a SHELL_SCRIPTS=(
    "CHECK_SMB_STATUS.sh"
    "CLEANUP_SMB_SETUP.sh"
    "CONFIGURE_SMB_NTLM.sh"
    "CREATE_SCANNER_USER.sh"
    "DEBUG_SMB_AUTH.sh"
    "ENABLE_BROTHER_SSH_LEGACY.sh"
    "ENABLE_NETWORK_LOGIN.sh"
    "FIX_SCANNER_ACCOUNT.sh"
    "FIX_SCANNER_FOLDER_STRUCTURE.sh"
    "FIX_SFTP_PERMISSIONS.sh"
    "FIX_SMB_AUTH_MACOS.sh"
    "FIX_SMB_AUTH.sh"
    "FIX_SMB_COMPLETE.sh"
    "FIX_SMB_KERBEROS.sh"
    "FIX_SMB_SERVICE.sh"
    "FORCE_KERBEROS_KEYS.sh"
    "MONITOR_SMB_CONNECTIONS.sh"
    "SETUP_COMMANDS.sh"
    "SETUP_SFTP_SCANNER.sh"
    "TEST_SCANNER_USER_SMB.sh"
    "TEST_SFTP_CONNECTION.sh"
    "TEST_SMB_AUTH_ALTERNATIVES.sh"
    "TEST_SMB_CONNECTION.sh"
    "TEST_SMB_SIMPLE.sh"
)

declare -a MARKDOWN_FILES=(
    "BROTHER_BRADMIN_CONFIG.md"
    "CLEANUP_SUMMARY.md"
    "FIX_BROTHER_SFTP_SSH.md"
    "FTP_COMPATIBILITY_ANALYSIS.md"
    "HTTP_API_WORKAROUND.md"
    "MACOS_SMB_AUTH_GUIDE.md"
    "SCANNER_SECURE_SETUP.md"
    "SCANNER_SETUP.md"
    "SCANNER_SFTP_CONFIG.md"
    "SCANNER_SINGLE_URL.md"
    "SCANNER_SMB_PATH.md"
    "SCANNER_SMB_SETUP.md"
    "SCANNER_TOUCHSCREEN_CONFIG.md"
    "SCANNER_TROUBLESHOOTING.md"
    "SECURE_SCANNER_SETUP.md"
    "SERVICE_ACCOUNT_SETUP.md"
    "SFTP_SETUP_GUIDE.md"
    "SMB_AUTH_FIX_STEPS.md"
    "SMB_DEBUGGING_GUIDE.md"
    "SMB_DIAGNOSIS.md"
    "SMB_STATUS_SUMMARY.md"
    "SMB_VS_FTP_COMPARISON.md"
    "TEST_SCANNER_CONNECTION.md"
    "TEST_SCANNER_DIRECTLY.md"
    "VERIFY_SHARE_REGISTRATION.md"
    "ARCHITECTURE_COMPARISON.md"
    "SECURITY_ANALYSIS.md"
    "WATCHER_RESOURCES.md"
    "WATCHER_SETUP.md"
)

# Print header
echo "=========================================="
if [ "$EXECUTE_MODE" = true ]; then
    echo "DELETE SCANNER/SMB/FTP FILES - EXECUTE MODE"
    echo "=========================================="
    echo ""
    echo "⚠️  WARNING: This will PERMANENTLY DELETE files!"
    echo ""
else
    echo "DELETE SCANNER/SMB/FTP FILES - DRY RUN MODE"
    echo "=========================================="
    echo ""
    echo "This is a dry-run. No files will be deleted."
    echo "Use --execute flag to actually delete files."
    echo ""
fi

# Counters
total_files=0
found_files=0
deleted_files=0
missing_files=0

# Function to process a file
process_file() {
    local file="$1"
    local file_path="$SCRIPT_DIR/$file"
    
    total_files=$((total_files + 1))
    
    if [ -f "$file_path" ]; then
        found_files=$((found_files + 1))
        if [ "$EXECUTE_MODE" = true ]; then
            if rm "$file_path" 2>/dev/null; then
                deleted_files=$((deleted_files + 1))
                echo "  ✓ Deleted: $file"
            else
                echo "  ✗ Failed to delete: $file"
            fi
        else
            echo "  [WOULD DELETE] $file"
        fi
    else
        missing_files=$((missing_files + 1))
        if [ "$EXECUTE_MODE" = true ]; then
            echo "  ⚠ Not found: $file (skipping)"
        else
            echo "  [NOT FOUND] $file"
        fi
    fi
}

# Process shell scripts
echo "Shell Scripts (${#SHELL_SCRIPTS[@]} files):"
echo "----------------------------------------"
for script in "${SHELL_SCRIPTS[@]}"; do
    process_file "$script"
done

echo ""
echo "Markdown Documentation (${#MARKDOWN_FILES[@]} files):"
echo "----------------------------------------"
for md_file in "${MARKDOWN_FILES[@]}"; do
    process_file "$md_file"
done

# Print summary
echo ""
echo "=========================================="
echo "SUMMARY"
echo "=========================================="
echo "Total files to process: $total_files"
echo "Files found: $found_files"
if [ "$EXECUTE_MODE" = true ]; then
    echo "Files deleted: $deleted_files"
    echo "Files not found: $missing_files"
    echo ""
    if [ $deleted_files -gt 0 ]; then
        echo "✓ Deletion complete!"
    fi
else
    echo "Files that would be deleted: $found_files"
    echo "Files not found: $missing_files"
    echo ""
    echo "To actually delete these files, run:"
    echo "  ./DELETE_SCANNER_FILES.sh --execute"
fi
echo "=========================================="
