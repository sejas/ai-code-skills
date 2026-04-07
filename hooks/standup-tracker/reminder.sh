#!/bin/bash
# Claude Code Hook: Standup Reminder (SessionEnd)
#
# Checks if today's diary has been updated with a Claude Code Session block.
# If not, reminds the user to run /standup.

DIARY_PATH="$HOME/Library/Mobile Documents/iCloud~md~obsidian/Documents/sejas/🗓️ Diary"
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
