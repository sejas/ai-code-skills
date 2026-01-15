#!/bin/bash
# Claude Code Hook: Auto-format files (PostToolUse)
#
# This hook automatically formats files after Write/Edit operations.
# Place in ~/.claude/hooks/ and reference in your settings.json
#
# Supports: TypeScript (prettier), PHP (phpcbf)

# Read JSON input from stdin
JSON_DATA=$(cat)

# Get the file path from the tool output
FILE_PATH=$(echo "$JSON_DATA" | jq -r '.tool_input.file_path // ""')

# Exit if no file path
if [ -z "$FILE_PATH" ] || [ "$FILE_PATH" = "null" ]; then
    exit 0
fi

# Skip if file doesn't exist
if [ ! -f "$FILE_PATH" ]; then
    exit 0
fi

# Get file extension
EXT="${FILE_PATH##*.}"

# Format based on file type
case "$EXT" in
    ts|tsx|js|jsx)
        # TypeScript/JavaScript - use prettier if available
        if command -v prettier &> /dev/null; then
            prettier --write "$FILE_PATH" 2>/dev/null
        fi
        ;;
    php)
        # PHP - use phpcbf (PHP Code Beautifier) if available
        if command -v phpcbf &> /dev/null; then
            phpcbf --standard=WordPress "$FILE_PATH" 2>/dev/null
        fi
        ;;
esac

# PostToolUse hooks don't return JSON - they're fire-and-forget
exit 0
