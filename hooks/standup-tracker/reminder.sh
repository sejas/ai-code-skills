#!/bin/bash
# Claude Code Hook: Standup Reminder (SessionEnd)
#
# Checks if today's diary has been updated with a Claude Code Session block.
# If not, reminds the user to run /standup.

# Set STANDUP_DIARY_PATH in your environment, e.g.:
#   export STANDUP_DIARY_PATH="$HOME/Library/Mobile Documents/iCloud~md~obsidian/Documents/<vault>/Diary"
DIARY_PATH="${STANDUP_DIARY_PATH:-}"
if [[ -z "$DIARY_PATH" ]]; then
    exit 0
fi
TODAY=$(date +%Y-%m-%d)
DIARY_FILE="$DIARY_PATH/$TODAY.md"

# Check if diary file exists and contains a session block
if [[ -f "$DIARY_FILE" ]]; then
    if grep -q "^\*\*Claude Code Session" "$DIARY_FILE"; then
        # Session block exists, no reminder needed
        exit 0
    fi
fi

# No session block found, print reminder
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Reminder: Run /standup to update your daily log"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
