#!/bin/bash
# Create a checkpoint file for token drift mitigation

TIMESTAMP=$(date +%Y-%m-%d-%H%M)
CHECKPOINT_DIR="$(dirname "$0")/../checkpoints"
CHECKPOINT_FILE="${CHECKPOINT_DIR}/checkpoint-${TIMESTAMP}.md"

# Ensure checkpoint directory exists
mkdir -p "$CHECKPOINT_DIR"

cat > "$CHECKPOINT_FILE" << EOF
# Checkpoint: ${TIMESTAMP}

## Decisions Made
- [Add decisions made since last checkpoint]

## Files Modified
- [List files modified]

## Next Actions
- [ ] [Action 1]
- [ ] [Action 2]

## Critical Updates Needed
- [ ] [Update 1]
- [ ] [Update 2]
EOF

echo "✅ Checkpoint created: $CHECKPOINT_FILE"
echo "📝 Edit it to add details:"
echo "   code $CHECKPOINT_FILE"

