#!/bin/bash
#
# Generic Remote Notification Hook for Claude Code
#
# Sends remote notifications when Claude needs attention.
# Auto-detects enabled backends based on environment variables.
#
# Supported backends:
# - Telegram: CLAUDE_TELEGRAM_TOKEN, CLAUDE_TELEGRAM_CHAT_ID
# - ntfy.sh: CLAUDE_NTFY_TOPIC, CLAUDE_NTFY_SERVER (optional)
#
# Usage: Called automatically by Claude Code on notification events
#

set -euo pipefail

# Load environment variables from .env if it exists
if [ -f "$(pwd)/.env" ]; then
    export $(grep -v '^#' "$(pwd)/.env" | xargs)
fi

# Load from global .env if it exists
if [ -f "$HOME/.claude/.env" ]; then
    export $(grep -v '^#' "$HOME/.claude/.env" | xargs)
fi

# Get notification context from Claude
TOOL_USE="${TOOL_USE:-unknown}"
RESULT="${RESULT:-}"

# Get repository context
REPO_NAME=""
if git rev-parse --git-dir > /dev/null 2>&1; then
    # Try to get GitHub repo name from remote
    REMOTE_URL=$(git config --get remote.origin.url 2>/dev/null || echo "")
    if [ -n "$REMOTE_URL" ]; then
        # Extract owner/repo from URLs like:
        # - https://github.com/owner/repo.git
        # - git@github.com:owner/repo.git
        REPO_NAME=$(echo "$REMOTE_URL" | sed -E 's#.*/([^/]+/[^/]+)(\.git)?$#\1#' | sed 's/\.git$//')
    fi

    # Fallback to just the directory name if no remote
    if [ -z "$REPO_NAME" ]; then
        REPO_NAME=$(basename "$(git rev-parse --show-toplevel 2>/dev/null)")
    fi
fi

# Extract summary from RESULT if available
SUMMARY=""
if [ -n "$RESULT" ]; then
    # Try to extract a meaningful summary from the result
    # Look for common patterns in Claude's responses
    SUMMARY=$(echo "$RESULT" | grep -oE "(permission|approve|confirm|waiting|input|feedback)" | head -1)
fi

# Build context prefix
CONTEXT=""
if [ -n "$REPO_NAME" ]; then
    CONTEXT="[$REPO_NAME] "
fi

# Determine notification message (detailed for Telegram)
if echo "$TOOL_USE" | grep -q "permission_prompt"; then
    if [ -n "$SUMMARY" ]; then
        MESSAGE="${CONTEXT}🔐 Permission needed: $SUMMARY"
    else
        MESSAGE="${CONTEXT}🔐 Claude needs permission to proceed"
    fi
elif echo "$TOOL_USE" | grep -q "idle_prompt"; then
    MESSAGE="${CONTEXT}⏸️ Waiting for your input"
else
    MESSAGE="${CONTEXT}🤖 Claude needs attention"
fi

# Add timestamp to message (for Telegram)
TIMESTAMP=$(date +"%H:%M")
MESSAGE="$TIMESTAMP | $MESSAGE"

# Simple message for ntfy.sh (security through obscurity - don't leak details)
# Just repo name + "ready" to avoid filtering sensitive information
SIMPLE_MESSAGE="ready"
if [ -n "$REPO_NAME" ]; then
    # Extract just the repo name (last part after /)
    SIMPLE_MESSAGE="${REPO_NAME##*/} ready"
fi

# Track if any notification was sent
SENT_COUNT=0

# ============================================================================
# Telegram Backend
# ============================================================================
send_telegram() {
    local token="$1"
    local chat_id="$2"
    local message="$3"

    local url="https://api.telegram.org/bot${token}/sendMessage"
    local payload=$(cat <<EOF
{
    "chat_id": "${chat_id}",
    "text": "${message}",
    "parse_mode": "HTML"
}
EOF
)

    if curl -s -X POST "$url" \
        -H "Content-Type: application/json" \
        -d "$payload" > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

if [ -n "${CLAUDE_TELEGRAM_TOKEN:-}" ] && [ -n "${CLAUDE_TELEGRAM_CHAT_ID:-}" ]; then
    if send_telegram "$CLAUDE_TELEGRAM_TOKEN" "$CLAUDE_TELEGRAM_CHAT_ID" "$MESSAGE"; then
        SENT_COUNT=$((SENT_COUNT + 1))
    fi
fi

# ============================================================================
# ntfy.sh Backend
# ============================================================================
send_ntfy() {
    local topic="$1"
    local server="${2:-https://ntfy.sh}"
    local message="$3"

    local url="${server}/${topic}"

    if curl -s -X POST "$url" \
        -H "Title: Claude Code" \
        -H "Tags: robot" \
        -d "$message" > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

if [ -n "${CLAUDE_NTFY_TOPIC:-}" ]; then
    NTFY_SERVER="${CLAUDE_NTFY_SERVER:-https://ntfy.sh}"
    if send_ntfy "$CLAUDE_NTFY_TOPIC" "$NTFY_SERVER" "$SIMPLE_MESSAGE"; then
        SENT_COUNT=$((SENT_COUNT + 1))
    fi
fi

# ============================================================================
# Future backends can be added here following the same pattern
# ============================================================================

# Discord example (commented out, for reference):
# if [ -n "${CLAUDE_DISCORD_WEBHOOK_URL:-}" ]; then
#     curl -s -X POST "$CLAUDE_DISCORD_WEBHOOK_URL" \
#         -H "Content-Type: application/json" \
#         -d "{\"content\": \"$MESSAGE\"}" > /dev/null 2>&1 && \
#         SENT_COUNT=$((SENT_COUNT + 1))
# fi

# Exit silently if no backends configured (not an error)
if [ $SENT_COUNT -eq 0 ]; then
    # No backends configured, exit silently
    exit 0
fi

exit 0
