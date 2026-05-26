#!/bin/bash
#
# Skill Dirty Marker Hook
#
# Watches Write/Edit/MultiEdit tool calls. If the edited file lives under
# ~/.claude/skills/<name>/, record the skill name in ~/.claude/.skills-dirty
# so a later sync step (the `sync-skills` skill) knows what to push to the
# public ai-code-skills repo.
#
# Excludes per-user state (config.json, *.local.*, .env*) and the marker file
# itself. Silent on non-matching edits.
#
# Hook input: JSON on stdin with .tool_input.file_path (Claude Code PostToolUse).

set -euo pipefail

MARKER="$HOME/.claude/.skills-dirty"
SKILLS_ROOT="$HOME/.claude/skills"

# Read JSON from stdin
INPUT=$(cat)

# Extract file path (try common shapes)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // .tool_input.path // empty' 2>/dev/null || echo "")

[ -z "$FILE_PATH" ] && exit 0

# Normalize: resolve ~
FILE_PATH="${FILE_PATH/#\~/$HOME}"

# Must be under skills root
case "$FILE_PATH" in
  "$SKILLS_ROOT"/*) ;;
  *) exit 0 ;;
esac

# Strip the prefix to get "<skill-name>/<rest>"
REL="${FILE_PATH#$SKILLS_ROOT/}"
SKILL_NAME="${REL%%/*}"

[ -z "$SKILL_NAME" ] && exit 0

# Skip per-user state and secret-prone files
case "$REL" in
  */config.json) exit 0 ;;
  */config.local.* | */*.local.* ) exit 0 ;;
  */.env | */.env.* ) exit 0 ;;
  */*.token | */*.secret ) exit 0 ;;
esac

# Append (de-duped) to marker
touch "$MARKER"
if ! grep -Fxq "$SKILL_NAME" "$MARKER" 2>/dev/null; then
  echo "$SKILL_NAME" >> "$MARKER"
fi

exit 0
