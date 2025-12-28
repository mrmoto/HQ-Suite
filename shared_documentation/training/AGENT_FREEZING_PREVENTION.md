# Agent Freezing Prevention: Best Practices

**Date**: 2025-12-23  
**Purpose**: Prevent AI agents from freezing or becoming unresponsive during development work  
**Status**: Active Guidelines

---

## Critical Problem

**Observed Issue**: Agents frequently freeze or become unresponsive, causing:
- 5+ minute delays with no response
- User repeatedly asking "are you frozen?"
- Lost productivity and frustration
- Broken workflow continuity

**Root Causes Identified**:
1. Dropbox cloud sync conflicts (file system locks)
2. Large directory operations (11,000+ files)
3. Tool call timeouts without proper error handling
4. Plan mode restrictions not properly handled
5. Rate limiting on complex operations
6. Workspace path resolution delays

---

## Best Practices for Users

### 1. Avoid Dropbox for Active Development

**Problem**: Dropbox sync locks files during operations, causing timeouts

**Solution**:
- Use local filesystem (`~/Development/` or `~/Projects/`) for active code
- Sync to Dropbox for backup only (not real-time)
- Or use Dropbox selectively (docs only, not code)

**If Must Use Dropbox**:
- Pause Dropbox sync temporarily during large file operations
- Use Finder/Manual moves instead of terminal commands
- Work outside Dropbox during reorganization, then move back

### 2. Break Large Operations into Smaller Chunks

**Problem**: Large operations (many file edits, directory scans) cause timeouts

**Solution**:
- Request operations in 15-30 minute chunks
- Ask agent to work on one file/directory at a time
- Use incremental commits instead of massive changes
- Break complex tasks into smaller sub-tasks

**Example**:
- ❌ "Update all 50 files in the codebase"
- ✅ "Update the config.py file first, then we'll do the next file"

### 3. Provide Clear, Single-Step Instructions

**Problem**: Complex, multi-part requests can cause agent confusion and delays

**Solution**:
- Give one instruction at a time
- Wait for completion before next instruction
- Be explicit about what you want
- Avoid ambiguous requests

**Example**:
- ❌ "Fix the bugs and update the docs and test everything"
- ✅ "Fix the bug in config.py" → wait → "Now update the README" → wait → "Now run tests"

### 4. Monitor Agent Response Times

**Problem**: Agents may be working but appear frozen

**Solution**:
- Wait 30-60 seconds for simple operations
- Wait 2-3 minutes for complex operations (file scans, large edits)
- If no response after 3 minutes, interrupt and ask status
- Check if agent is in "Planning next steps" mode (may take longer)

**Red Flags**:
- No response after 5+ minutes
- Agent says "Planning next steps" for > 2 minutes
- Multiple failed tool calls in a row

### 5. Use Plan Mode Strategically

**Problem**: Plan mode prevents execution, which can cause confusion

**Solution**:
- Use plan mode for complex, multi-step tasks
- Explicitly say "execute the plan" when ready
- Don't assume agent will automatically execute
- Review plans before execution

**When to Use Plan Mode**:
- ✅ Complex refactoring (10+ files)
- ✅ New feature implementation (multiple components)
- ✅ Architecture changes
- ❌ Simple single-file edits
- ❌ Quick fixes

### 6. Avoid Terminal Commands for File Operations

**Problem**: Terminal commands in Dropbox-synced directories often timeout

**Solution**:
- Use file read/write tools for documentation
- Use file editing tools instead of terminal commands
- Only use terminal for actual command execution (git, npm, etc.)
- Avoid `mv`, `cp`, `rm` in Dropbox directories

**Example**:
- ❌ `mv file1.txt file2.txt` (in Dropbox)
- ✅ Use file editing tools to read/write files
- ✅ Use terminal only for: `git commit`, `npm install`, etc.

### 7. Exclude Large Directories from Workspace

**Problem**: Large directories (node_modules, vendor, __pycache__) slow indexing

**Solution**:
- Add to workspace `.gitignore` patterns
- Exclude from workspace settings
- Use `.cursorignore` for agent-specific exclusions

**Common Exclusions**:
- `node_modules/`
- `vendor/` (PHP)
- `__pycache__/`
- `.venv/`, `venv/`
- `*.log`
- Large data directories

### 8. Provide Context Upfront

**Problem**: Agent needs to search/read many files to understand context

**Solution**:
- Reference specific files in your request
- Mention relevant documentation
- Provide brief context in your message
- Point to specific sections of architecture docs

**Example**:
- ❌ "Fix the preprocessing"
- ✅ "Fix the deskew method in `ocr_service/utils/image_preprocessing.py` - it should use HoughLinesP per MASTER_ARCHITECTURE.md section 5.1"

### 9. Interrupt Long-Running Operations

**Problem**: Agent may be stuck in a loop or waiting for timeout

**Solution**:
- If no response after 3 minutes, send a simple message: "Status?"
- If still no response after 5 minutes, interrupt: "Stop, let's try a different approach"
- Don't wait indefinitely - agent may be frozen

**Interruption Pattern**:
1. Wait 2-3 minutes (normal for complex operations)
2. Send "Status?" or "Are you working?"
3. Wait 1 more minute
4. If still no response: "Stop, let's try a different approach"

### 10. Use Explicit Confirmation for Critical Operations

**Problem**: Agent may proceed with wrong assumptions

**Solution**:
- Ask for confirmation before large changes
- Review plans before execution
- Verify understanding: "So you're going to do X, Y, Z?"
- Get explicit "yes" before proceeding

---

## Best Practices for Agents

### 1. Acknowledge Long Operations Immediately

**When to Acknowledge**:
- Operations that will take > 30 seconds
- File scans of large directories
- Multiple file edits
- Complex searches

**Acknowledgment Format**:
```
"I'm scanning the codebase for all Python dependencies. This may take a minute..."
```

### 2. Provide Progress Updates

**When to Update**:
- Every 30-60 seconds during long operations
- After completing each major step
- When encountering delays

**Update Format**:
```
"Found 15 Python files so far, scanning 5 more directories..."
```

### 3. Handle Timeouts Gracefully

**When Timeout Occurs**:
- Acknowledge immediately: "The file operation timed out"
- Suggest alternative approach
- Don't retry indefinitely
- Ask user for guidance

**Example**:
```
"The file read timed out (likely Dropbox sync). Should I:
1. Try again in 30 seconds?
2. Use a different approach?
3. Skip this file for now?"
```

### 4. Batch Related Operations

**Best Practice**:
- Group file reads together
- Batch file edits when possible
- Use parallel tool calls when safe
- Avoid sequential operations that could timeout

**Example**:
- ✅ Read 5 files in parallel (if independent)
- ❌ Read file 1 → wait → read file 2 → wait → read file 3

### 5. Use Efficient Search Patterns

**Best Practice**:
- Use `grep` for exact string searches (faster than semantic search)
- Use semantic search for conceptual queries
- Limit search scope when possible
- Cache results when appropriate

**Example**:
- ✅ `grep "def process_receipt"` (exact function name)
- ❌ Semantic search for "process receipt function" (slower, less precise)

### 6. Avoid Unnecessary Tool Calls

**Best Practice**:
- Don't read files you already have in context
- Don't search for information already provided
- Don't re-read documentation unnecessarily
- Cache information from previous reads

**Example**:
- ❌ Read MASTER_ARCHITECTURE.md 3 times in same session
- ✅ Reference it from memory, only re-read if needed

### 7. Provide Clear Error Messages

**When Errors Occur**:
- Explain what went wrong clearly
- Suggest specific alternatives
- Don't just say "error occurred"
- Help user understand the issue

**Example**:
```
"File read timed out after 30 seconds. This is likely due to Dropbox sync locking the file. 
Options:
1. Pause Dropbox sync and retry
2. Use a different file path
3. Skip this file for now"
```

### 8. Set Realistic Expectations

**When Starting Long Operations**:
- Estimate time required
- Explain what you're doing
- Set expectations for progress updates

**Example**:
```
"I need to scan 50 Python files to find all imports. This will take about 2 minutes. 
I'll update you every 30 seconds with progress."
```

### 9. Don't Wait for Timeouts

**Best Practice**:
- If operation is clearly stuck, acknowledge and suggest alternative
- Don't wait for full timeout period
- Be proactive about suggesting workarounds

**Example**:
```
"This directory listing is taking longer than expected. Let me try a different approach 
- I'll search for specific file patterns instead of listing the entire directory."
```

### 10. Confirm Understanding Before Long Operations

**Before Complex Tasks**:
- Summarize what you're about to do
- Ask for confirmation if uncertain
- Clarify ambiguous requirements

**Example**:
```
"Just to confirm: You want me to update all hardcoded thresholds in the codebase to use 
the configuration system. This will affect about 10 files. Should I proceed?"
```

---

## Emergency Procedures

### If Agent Appears Frozen

**User Actions**:
1. Wait 2-3 minutes (may be working on complex operation)
2. Send simple message: "Status?" or "Are you working?"
3. Wait 1 more minute
4. If no response: "Stop, let's try a different approach"
5. If still frozen: Start new chat session

**Agent Should**:
- Always respond to "Status?" within 10 seconds
- Acknowledge if stuck: "I'm stuck on X, let me try Y"
- Never go silent for > 3 minutes without acknowledgment

### If Operation Times Out

**User Actions**:
1. Acknowledge the timeout
2. Suggest alternative approach
3. Ask if user wants to retry or skip

**Agent Should**:
- Immediately acknowledge timeout
- Explain likely cause (Dropbox sync, large directory, etc.)
- Suggest specific alternatives
- Not retry indefinitely

---

## Monitoring and Prevention

### Signs Agent May Freeze

**Watch For**:
- "Planning next steps" message for > 2 minutes
- Multiple failed tool calls in a row
- No response to simple questions
- Repeated timeouts on same operation

**Preventive Actions**:
- Break operation into smaller chunks
- Use alternative approach
- Exclude problematic directories
- Pause Dropbox sync if needed

### Performance Baselines

**Expected Performance**:
- Simple file read: < 1 second
- Directory listing: < 2 seconds
- File edit: < 5 seconds
- Tool call overhead: < 1 second

**If Slower Than Baseline**:
- Likely Dropbox sync issue
- Consider pausing sync
- Use alternative approach
- Report to user

---

## Summary: Quick Reference

### For Users
1. ✅ Avoid Dropbox for active development
2. ✅ Break large operations into chunks
3. ✅ Give one instruction at a time
4. ✅ Wait 2-3 minutes before interrupting
5. ✅ Use plan mode for complex tasks
6. ✅ Avoid terminal commands for file ops
7. ✅ Exclude large directories
8. ✅ Provide context upfront
9. ✅ Interrupt if frozen > 3 minutes
10. ✅ Confirm before critical operations

### For Agents
1. ✅ Acknowledge long operations immediately
2. ✅ Provide progress updates every 30-60 seconds
3. ✅ Handle timeouts gracefully
4. ✅ Batch related operations
5. ✅ Use efficient search patterns
6. ✅ Avoid unnecessary tool calls
7. ✅ Provide clear error messages
8. ✅ Set realistic expectations
9. ✅ Don't wait for timeouts
10. ✅ Confirm understanding before long operations

---

## Related Documents

- **LATENCY_DIAGNOSIS.md**: Detailed analysis of Dropbox sync issues
- **AGENT_TRAINING_GUIDE.md**: Comprehensive agent training guide
- **MASTER_ARCHITECTURE.md**: System architecture (reference for context)

---

**Last Updated**: 2025-12-23  
**Status**: Active Guidelines - Update as new patterns emerge

