#!/bin/bash
# Claude Code Hook: macOS Notification (Notification)
#
# Sends a native macOS notification when Claude needs attention.
# Uses terminal-notifier (brew install terminal-notifier)
#
# Configure in settings.json with matchers:
#   "Notification": [
#     {
#       "matcher": "permission_prompt|idle_prompt",
#       "hooks": [{"type": "command", "command": "~/.claude/hooks/notify.sh"}]
#     }
#   ]
#
# Common matchers:
#   - permission_prompt: Permission requests
#   - idle_prompt: Waiting for input (60+ seconds)
#   - auth_success: Authentication success

terminal-notifier -title "Claude Code" -message "Claude needs your attention" -sound default
