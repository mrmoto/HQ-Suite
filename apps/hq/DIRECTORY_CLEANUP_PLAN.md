# Directory Cleanup Plan

## Current State Analysis

### Active Working Directory
**Path:** `/Users/scottroberts/Library/CloudStorage/Dropbox/app_development/hq`
- **Status:** ✅ Active project location
- **Size:** 117M
- **Contains:** Laravel application, chat_recovery scripts, active project files
- **Git:** No git repository initialized

### Legacy/Backup Directories

#### 1. `/Users/scottroberts/Library/CloudStorage/Dropbox/apps/hq`
- **Status:** ⚠️ Old location, contains legacy files
- **Size:** 116M
- **Contains:** 
  - 60+ scanner/SMB setup scripts and documentation files
  - Old migration scripts
  - Duplicate Laravel application files
- **Git:** No git repository initialized
- **Note:** Based on training data (message 216), scanner-related files should be deleted

#### 2. `/Users/scottroberts/Library/CloudStorage/Dropbox/apps/hq-symlink`
- **Status:** ⚠️ Symlink pointing to `../app_development/hq`
- **Type:** Symbolic link
- **Target:** `/Users/scottroberts/Library/CloudStorage/Dropbox/app_development/hq`
- **Note:** Created during migration, may cause confusion

#### 3. `/Users/scottroberts/Library/CloudStorage/Dropbox/application Backups/hq`
- **Status:** 📦 Backup copy
- **Size:** 117M
- **Note:** Appears to be a backup, should be preserved

## Cleanup Strategy

### Phase 1: Verification (No Changes)
1. ✅ Verify current working directory structure
2. ✅ Identify unique files in `apps/hq` that might need preservation
3. ✅ Compare critical files between directories
4. ✅ Document what will be deleted

### Phase 2: Safe Cleanup (Requires Approval)

#### Step 1: Remove Symlink
**Action:** Delete `/Users/scottroberts/Library/CloudStorage/Dropbox/apps/hq-symlink`
- **Reason:** No longer needed, current workspace is in `app_development/hq`
- **Risk:** Low - symlink only, not actual data
- **Command:** `rm /Users/scottroberts/Library/CloudStorage/Dropbox/apps/hq-symlink`

#### Step 2: Archive Scanner/SMB Files (Optional Safety Step)
**Action:** Create archive of scanner/SMB files before deletion
- **Location:** `/Users/scottroberts/Library/CloudStorage/Dropbox/app_development/hq/archived_scanner_files/`
- **Reason:** Safety backup in case any documentation is needed later
- **Risk:** None - creates backup before deletion
- **Files to archive:** All `.sh` and `.md` files in `apps/hq` related to scanner/SMB

#### Step 3: Remove Scanner/SMB Files from `apps/hq`
**Action:** Delete all scanner/SMB related scripts and documentation
- **Files to delete:** 60+ files (see list below)
- **Reason:** No longer needed, cluttering directory structure
- **Risk:** Low - these are setup/troubleshooting files, not application code
- **Note:** Based on your explicit request in training data (message 216)

**Files to be deleted:**
- All `*SCANNER*.sh`, `*SCANNER*.md` files
- All `*SMB*.sh`, `*SMB*.md` files
- All `*SFTP*.sh`, `*SFTP*.md` files
- All `*FTP*.sh`, `*FTP*.md` files
- Migration/aggregation scripts: `AGGREGATE_CHAT_HISTORY.sh`, `EXTRACT_ALL_PROMPTS_TO_CSV.sh`
- Setup scripts: `SETUP_COMMANDS.sh`, `CREATE_SCANNER_USER.sh`, etc.
- Test scripts: `TEST_*.sh` files
- Fix scripts: `FIX_*.sh` files
- Documentation: `*_PLAN.md`, `*_GUIDE.md`, `*_ANALYSIS.md` files

#### Step 4: Evaluate `apps/hq` Directory
**Action:** After removing scanner files, assess if `apps/hq` should be:
- **Option A:** Completely removed (if it's just a backup with no unique files)
- **Option B:** Kept as backup but cleaned (if it contains important historical data)
- **Option C:** Renamed to `apps/hq-backup-YYYYMMDD` for clarity

**Decision Required:** Which option do you prefer?

#### Step 5: Verify `app_development/hq` Integrity
**Action:** After cleanup, verify:
- ✅ All Laravel application files present
- ✅ `chat_recovery/` directory intact
- ✅ No broken references
- ✅ All necessary scripts present

## Files to be Deleted (from `apps/hq`)

### Scanner-Related Scripts (30+ files)
- `CHECK_SMB_STATUS.sh`
- `CLEANUP_SMB_SETUP.sh`
- `CONFIGURE_SMB_NTLM.sh`
- `CREATE_SCANNER_USER.sh`
- `DEBUG_SMB_AUTH.sh`
- `ENABLE_BROTHER_SSH_LEGACY.sh`
- `ENABLE_NETWORK_LOGIN.sh`
- `FIX_SCANNER_ACCOUNT.sh`
- `FIX_SCANNER_FOLDER_STRUCTURE.sh`
- `FIX_SFTP_PERMISSIONS.sh`
- `FIX_SMB_AUTH.sh`
- `FIX_SMB_AUTH_MACOS.sh`
- `FIX_SMB_COMPLETE.sh`
- `FIX_SMB_KERBEROS.sh`
- `FIX_SMB_SERVICE.sh`
- `FORCE_KERBEROS_KEYS.sh`
- `MONITOR_SMB_CONNECTIONS.sh`
- `SETUP_COMMANDS.sh`
- `SETUP_SFTP_SCANNER.sh`
- `TEST_SCANNER_USER_SMB.sh`
- `TEST_SFTP_CONNECTION.sh`
- `TEST_SMB_AUTH_ALTERNATIVES.sh`
- `TEST_SMB_CONNECTION.sh`
- `TEST_SMB_SIMPLE.sh`

### Scanner-Related Documentation (30+ files)
- `BROTHER_BRADMIN_CONFIG.md`
- `FIX_BROTHER_SFTP_SSH.md`
- `FTP_COMPATIBILITY_ANALYSIS.md`
- `HTTP_API_WORKAROUND.md`
- `MACOS_SMB_AUTH_GUIDE.md`
- `SCANNER_SECURE_SETUP.md`
- `SCANNER_SETUP.md`
- `SCANNER_SFTP_CONFIG.md`
- `SCANNER_SINGLE_URL.md`
- `SCANNER_SMB_PATH.md`
- `SCANNER_SMB_SETUP.md`
- `SCANNER_TOUCHSCREEN_CONFIG.md`
- `SCANNER_TROUBLESHOOTING.md`
- `SECURE_SCANNER_SETUP.md`
- `SECURITY_ANALYSIS.md`
- `SERVICE_ACCOUNT_SETUP.md`
- `SFTP_SETUP_GUIDE.md`
- `SMB_AUTH_FIX_STEPS.md`
- `SMB_DEBUGGING_GUIDE.md`
- `SMB_DIAGNOSIS.md`
- `SMB_STATUS_SUMMARY.md`
- `SMB_VS_FTP_COMPARISON.md`
- `TEST_SCANNER_CONNECTION.md`
- `TEST_SCANNER_DIRECTLY.md`
- `VERIFY_SHARE_REGISTRATION.md`
- `WATCHER_RESOURCES.md`
- `WATCHER_SETUP.md`

### Migration/Chat History Scripts
- `AGGREGATE_CHAT_HISTORY.sh`
- `EXTRACT_ALL_PROMPTS_TO_CSV.sh`
- `CHAT_AGGREGATION_PLAN.md`
- `CURSOR_WORKSPACE_CHAT_RELATIONSHIP.md`
- `CURSOR_WORKSPACE_MIGRATION_PLAN.md`

### Other Documentation
- `ARCHITECTURE_COMPARISON.md`
- `CLEANUP_SUMMARY.md`
- `README_DEPRECATED.md`

## Safety Measures

1. **Backup First:** All files will be archived before deletion (optional but recommended)
2. **Dry Run:** Script will list all files before deletion
3. **Verification:** After cleanup, verify `app_development/hq` is intact
4. **Reversible:** Archived files can be restored if needed

## Execution Plan

### Pre-Execution Checklist
- [ ] Review this plan
- [ ] Confirm which option for `apps/hq` (A, B, or C)
- [ ] Confirm archive creation (yes/no)
- [ ] Close Cursor to prevent file locks
- [ ] Backup critical data (if not already done)

### Execution Steps
1. Create cleanup script with dry-run mode
2. Run dry-run to show what will be deleted
3. Get explicit approval
4. Create archive (if requested)
5. Execute cleanup
6. Verify results
7. Report completion

## Questions for You

1. **Archive scanner files?** (Yes/No) - Creates backup before deletion
2. **What to do with `apps/hq` after cleanup?** (Option A/B/C)
3. **Any files in `apps/hq` that should be preserved?** (List if any)
4. **Proceed with cleanup?** (Yes/No after reviewing plan)

## Next Steps

1. Review this plan
2. Answer questions above
3. Approve execution
4. Script will be created and executed

---

**Created:** 2025-12-18
**Status:** Awaiting Approval
