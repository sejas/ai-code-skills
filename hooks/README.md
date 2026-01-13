# Hooks Configuration Guide

This directory contains hook scripts that extend Claude Code's functionality. Hooks run automatically in response to specific events.

## Available Hooks

### PreToolUse Hooks (run before tool execution)

#### `commit-validator.sh`
Validates git commit messages before execution.

**Features:**
- Enforces conventional commit prefixes (feat, fix, docs, etc.)
- Maximum length check (75 characters)
- Blocks force commits (-f flag)

**Configuration:**
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/plugins/PLUGIN_PATH/hooks/commit-validator.sh"
          }
        ]
      }
    ]
  }
}
```

**Customize validation rules:**
Edit line 60-80 in `commit-validator.sh` to modify allowed prefixes or max length.

---

### PostToolUse Hooks (run after tool execution)

#### `auto-format.sh`
Automatically formats files after Write/Edit operations.

**Supported formats:**
- TypeScript/JavaScript (prettier)
- PHP (phpcbf with WordPress standards)

**Requirements:**
- `prettier` (install: `npm install -g prettier`)
- `phpcbf` (install via Composer)

**Configuration:**
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/plugins/PLUGIN_PATH/hooks/auto-format.sh"
          }
        ]
      }
    ]
  }
}
```

#### `speak-commit.sh`
Text-to-speech announcement after successful commits.

**Features:**
- Speaks repository name and commit message
- Contextual announcements based on commit type
- Runs in background (non-blocking)

**Configuration:**
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/plugins/PLUGIN_PATH/hooks/speak-commit.sh"
          }
        ]
      }
    ]
  }
}
```

**Customize voice:**
Edit line 69 to change from `Samantha` to another voice:
```bash
say -v Alex "$announcement" &  # Male voice
say -v Daniel "$announcement" &  # British male
```

---

### SessionStart Hooks (run when session starts)

#### `session-context.sh`
Injects git status and recent commits at session start.

**Features:**
- Shows uncommitted changes
- Displays current branch
- Lists last 5 commits

**Configuration:**
```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|resume|clear|compact",
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/plugins/PLUGIN_PATH/hooks/session-context.sh"
          }
        ]
      }
    ]
  }
}
```

---

### SessionEnd Hooks (run when session ends)

#### `save-summary` (AI-powered, recommended)
Uses Claude Agent SDK to generate intelligent session summaries.

**Requirements:**
- Python 3
- `claude-agent-sdk` (installed automatically on first run)

**Configuration:**
```json
{
  "hooks": {
    "SessionEnd": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/plugins/PLUGIN_PATH/hooks/save-summary"
          }
        ]
      }
    ]
  }
}
```

**Output location:** `~/.claude/session-logs/SESSION_ID.md`

#### `save-summary-basic.sh` (lightweight alternative)
Simple logging without AI summarization.

**Output location:** `~/.claude/session-log.txt`

#### `save-summary.py`
Direct Python implementation (called by `save-summary` wrapper).

---

### Notification Hooks

#### `notify.sh`
Sends macOS desktop notifications when Claude needs attention.

**Requirements:**
- `terminal-notifier` (install: `brew install terminal-notifier`)

**Configuration:**
```json
{
  "hooks": {
    "Notification": [
      {
        "matcher": "permission_prompt|idle_prompt",
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/plugins/PLUGIN_PATH/hooks/notify.sh"
          }
        ]
      }
    ]
  }
}
```

**Common matchers:**
- `permission_prompt` - Permission requests
- `idle_prompt` - Waiting for input (60+ seconds)
- `auth_success` - Authentication success

---

## Complete Configuration Example

Add this to `~/.claude/settings.json` (replace `PLUGIN_PATH` with actual path):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/plugins/PLUGIN_PATH/hooks/commit-validator.sh"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/plugins/PLUGIN_PATH/hooks/auto-format.sh"
          }
        ]
      },
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/plugins/PLUGIN_PATH/hooks/speak-commit.sh"
          }
        ]
      }
    ],
    "SessionStart": [
      {
        "matcher": "startup",
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/plugins/PLUGIN_PATH/hooks/session-context.sh"
          }
        ]
      }
    ],
    "SessionEnd": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/plugins/PLUGIN_PATH/hooks/save-summary"
          }
        ]
      }
    ],
    "Notification": [
      {
        "matcher": "permission_prompt|idle_prompt",
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/plugins/PLUGIN_PATH/hooks/notify.sh"
          }
        ]
      }
    ]
  }
}
```

## Finding Your Plugin Path

After installation via `claude plugin install`, find the path:

```bash
# List installed plugins
claude plugin list

# Common paths:
# - GitHub installs: ~/.claude/plugins/cache/github/USERNAME/REPO/VERSION/
# - Local installs: ~/.claude/plugins/cache/local/PLUGIN_NAME/VERSION/
```

## Troubleshooting

### Hooks not executing?

1. **Check permissions:**
   ```bash
   chmod +x ~/.claude/plugins/PLUGIN_PATH/hooks/*.sh
   ```

2. **Verify settings.json syntax:**
   ```bash
   cat ~/.claude/settings.json | jq .
   ```

3. **Check Claude Code logs:**
   ```bash
   claude --verbose
   ```

### Hook errors?

Most hooks require external tools:
- `jq` - JSON parsing (install: `brew install jq`)
- `prettier` - Code formatting (install: `npm install -g prettier`)
- `terminal-notifier` - Notifications (install: `brew install terminal-notifier`)

## Customization Tips

### Disable specific hooks
Comment out or remove entries from `settings.json`.

### Modify hook behavior
Edit scripts directly - they're designed to be customizable.

### Add new hooks
1. Create script in `hooks/` directory
2. Add hook configuration to `settings.json`
3. Test with `claude --verbose`

## Hook Types Reference

| Type | When it runs | Can block? | Returns JSON? |
|------|--------------|------------|---------------|
| PreToolUse | Before tool execution | Yes | Yes |
| PostToolUse | After tool execution | No | No |
| SessionStart | Session begins | No | Yes (can add context) |
| SessionEnd | Session ends | No | No |
| Notification | Various events | No | No |

For more information, see [Claude Code Hooks Documentation](https://docs.anthropic.com/claude/docs/hooks).
