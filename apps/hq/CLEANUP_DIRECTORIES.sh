#!/bin/bash

# Directory Cleanup Script
# Removes symlink, deletes SMB/FTP/scanner files, and moves apps/hq to backup location
# Usage: ./CLEANUP_DIRECTORIES.sh [--execute]

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Directories
APPS_HQ="/Users/scottroberts/Library/CloudStorage/Dropbox/apps/hq"
SYMLINK="/Users/scottroberts/Library/CloudStorage/Dropbox/apps/hq-symlink"
BACKUP_BASE="/Users/scottroberts/Library/CloudStorage/Dropbox/application Backups"
BACKUP_NAME="hq-backup-$(date +%Y%m%d_%H%M%S)"
BACKUP_TARGET="${BACKUP_BASE}/${BACKUP_NAME}"

# Check if we're in execute mode
EXECUTE_MODE=false
if [[ "$1" == "--execute" ]]; then
    EXECUTE_MODE=true
fi

echo "=========================================="
if [ "$EXECUTE_MODE" = true ]; then
    echo "DIRECTORY CLEANUP - EXECUTE MODE"
else
    echo "DIRECTORY CLEANUP - DRY RUN MODE"
fi
echo "=========================================="
echo ""

# Function to check if file matches patterns to delete
should_delete() {
    local file="$1"
    local basename=$(basename "$file")
    
    # Check for SMB, FTP, SFTP, SCANNER patterns (case insensitive)
    if [[ "$basename" =~ ^.*(SMB|FTP|SFTP|SCANNER|scanner|smb|ftp|sftp).*\.(sh|md)$ ]]; then
        return 0  # Should delete
    fi
    
    # Check for specific migration/aggregation scripts
    if [[ "$basename" =~ ^(AGGREGATE_CHAT_HISTORY|EXTRACT_ALL_PROMPTS_TO_CSV|CHAT_AGGREGATION_PLAN|CURSOR_WORKSPACE) ]]; then
        return 0  # Should delete
    fi
    
    # Check for other cleanup/migration files
    if [[ "$basename" =~ ^(ARCHITECTURE_COMPARISON|CLEANUP_SUMMARY|README_DEPRECATED) ]]; then
        return 0  # Should delete
    fi
    
    return 1  # Keep file
}

# Step 1: Remove symlink
echo "Step 1: Remove symlink"
echo "  Target: $SYMLINK"
if [ -L "$SYMLINK" ]; then
    if [ "$EXECUTE_MODE" = true ]; then
        rm "$SYMLINK"
        echo "  ${GREEN}✓${NC} Symlink removed"
    else
        echo "  ${YELLOW}[DRY RUN]${NC} Would remove symlink"
    fi
else
    echo "  ${YELLOW}⚠${NC} Symlink not found (may already be removed)"
fi
echo ""

# Step 2: Find and list files to delete from apps/hq
echo "Step 2: Identify files to delete from apps/hq"
if [ ! -d "$APPS_HQ" ]; then
    echo "  ${RED}✗${NC} Directory not found: $APPS_HQ"
    exit 1
fi

files_to_delete=()
while IFS= read -r -d '' file; do
    if should_delete "$file"; then
        files_to_delete+=("$file")
    fi
done < <(find "$APPS_HQ" -maxdepth 1 -type f \( -name "*.sh" -o -name "*.md" \) -print0)

echo "  Found ${#files_to_delete[@]} files to delete:"
for file in "${files_to_delete[@]}"; do
    basename=$(basename "$file")
    echo "    - $basename"
done
echo ""

# Step 3: Delete files
if [ ${#files_to_delete[@]} -gt 0 ]; then
    echo "Step 3: Delete SMB/FTP/Scanner files"
    for file in "${files_to_delete[@]}"; do
        basename=$(basename "$file")
        if [ "$EXECUTE_MODE" = true ]; then
            rm "$file"
            echo "  ${GREEN}✓${NC} Deleted: $basename"
        else
            echo "  ${YELLOW}[DRY RUN]${NC} Would delete: $basename"
        fi
    done
else
    echo "Step 3: No files to delete"
fi
echo ""

# Step 4: Move apps/hq to backup location
echo "Step 4: Move apps/hq to backup location"
echo "  Source: $APPS_HQ"
echo "  Target: $BACKUP_TARGET"

if [ ! -d "$BACKUP_BASE" ]; then
    echo "  ${YELLOW}⚠${NC} Creating backup base directory: $BACKUP_BASE"
    if [ "$EXECUTE_MODE" = true ]; then
        mkdir -p "$BACKUP_BASE"
    fi
fi

if [ -d "$APPS_HQ" ]; then
    # Check if directory is empty or has remaining files
    remaining_files=$(find "$APPS_HQ" -maxdepth 1 -type f | wc -l | tr -d ' ')
    remaining_dirs=$(find "$APPS_HQ" -maxdepth 1 -type d ! -path "$APPS_HQ" | wc -l | tr -d ' ')
    
    echo "  Remaining files in apps/hq: $remaining_files"
    echo "  Remaining directories in apps/hq: $remaining_dirs"
    
    if [ "$EXECUTE_MODE" = true ]; then
        if [ -d "$BACKUP_TARGET" ]; then
            echo "  ${RED}✗${NC} Backup target already exists: $BACKUP_TARGET"
            exit 1
        fi
        mv "$APPS_HQ" "$BACKUP_TARGET"
        echo "  ${GREEN}✓${NC} Moved apps/hq to backup location"
    else
        echo "  ${YELLOW}[DRY RUN]${NC} Would move apps/hq to: $BACKUP_TARGET"
    fi
else
    echo "  ${YELLOW}⚠${NC} Source directory not found (may already be moved)"
fi
echo ""

# Step 5: Verify app_development/hq integrity
echo "Step 5: Verify app_development/hq integrity"
CURRENT_DIR="/Users/scottroberts/Library/CloudStorage/Dropbox/app_development/hq"

if [ -d "$CURRENT_DIR" ]; then
    echo "  ${GREEN}✓${NC} Current directory exists: $CURRENT_DIR"
    
    # Check for key directories
    key_dirs=("app" "bootstrap" "config" "database" "chat_recovery")
    for dir in "${key_dirs[@]}"; do
        if [ -d "$CURRENT_DIR/$dir" ]; then
            echo "  ${GREEN}✓${NC} Key directory exists: $dir"
        else
            echo "  ${RED}✗${NC} Missing key directory: $dir"
        fi
    done
    
    # Check for key files
    key_files=("artisan" "composer.json" "README.md")
    for file in "${key_files[@]}"; do
        if [ -f "$CURRENT_DIR/$file" ]; then
            echo "  ${GREEN}✓${NC} Key file exists: $file"
        else
            echo "  ${RED}✗${NC} Missing key file: $file"
        fi
    done
else
    echo "  ${RED}✗${NC} Current directory not found: $CURRENT_DIR"
    exit 1
fi
echo ""

# Summary
echo "=========================================="
echo "SUMMARY"
echo "=========================================="
if [ "$EXECUTE_MODE" = true ]; then
    echo "Cleanup completed:"
    echo "  - Symlink removed: $SYMLINK"
    echo "  - Files deleted: ${#files_to_delete[@]}"
    echo "  - Backup created: $BACKUP_TARGET"
    echo "  - Current directory verified: $CURRENT_DIR"
    echo ""
    echo "${GREEN}✓ Cleanup successful${NC}"
else
    echo "Dry run completed. Review the actions above."
    echo ""
    echo "To execute cleanup, run:"
    echo "  ./CLEANUP_DIRECTORIES.sh --execute"
fi
echo "=========================================="
