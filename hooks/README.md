# Hooks Configuration Guide

This directory contains hook scripts that extend Claude Code's functionality. Hooks run automatically in response to specific events.

**Note:** All hooks are automatically configured when you install the plugin via `claude plugin install sejas/ai-code-skills`. No manual configuration needed!

## Available Hooks

### PreToolUse Hooks (run before tool execution)

#### `commit-validator.sh`
Validates git commit messages before execution.

**Features:**
- Enforces conventional commit prefixes (feat, fix, docs, etc.)
- Maximum length check (75 characters)
- Blocks force commits (-f flag)
- Auto-configured on plugin install

**Customize validation rules:**
Edit `commit-validator.sh` to modify allowed prefixes or max length.

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


#### `speak-commit.sh`
Text-to-speech announcement after successful commits.

**Features:**
- Speaks repository name and commit message
- Contextual announcements based on commit type
- Runs in background (non-blocking)


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


---

### SessionEnd Hooks (run when session ends)

#### `save-summary` (AI-powered, recommended)
Uses Claude Agent SDK to generate intelligent session summaries.

**Requirements:**
- Python 3
- `claude-agent-sdk` (installed automatically on first run)


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


**Common matchers:**
- `permission_prompt` - Permission requests
- `idle_prompt` - Waiting for input (60+ seconds)
- `auth_success` - Authentication success

---

## Auto-Configuration

After installation via `claude plugin install sejas/ai-code-skills`, all hooks are automatically configured. You can view the configuration in `.claude-plugin/plugin.json`:

```json
{
  "hooks": {
    "PreToolUse": [...],
    "PostToolUse": [...],
    "SessionStart": [...],
    "SessionEnd": [...],
    "Notification": [...]
  }
}
```

The plugin uses `${CLAUDE_PLUGIN_ROOT}` variable for portable path resolution.

## Troubleshooting

### Hooks not executing?

1. **Check plugin is installed:**
   ```bash
   claude plugin list
   ```

2. **Debug mode:**
   ```bash
   claude --debug
   ```

3. **Verify hook scripts are executable:**
   ```bash
   ls -la ~/.claude/plugins/*/dev-workflow/*/hooks/
   ```

### Hook errors?

Most hooks require external tools:
- `jq` - JSON parsing (install: `brew install jq`)
- `prettier` - Code formatting (install: `npm install -g prettier`)
- `terminal-notifier` - Notifications (install: `brew install terminal-notifier`)

## Customization Tips

### Disable specific hooks
Clone the plugin and edit `.claude-plugin/plugin.json`, then use `claude --plugin-dir .`

### Modify hook behavior
Edit scripts directly - they're designed to be customizable:
```bash
git clone https://github.com/sejas/ai-code-skills.git
cd ai-code-skills
vi hooks/commit-validator.sh
claude --plugin-dir .
```

### Add new hooks
1. Create script in `hooks/` directory
2. Add hook configuration to `.claude-plugin/plugin.json`
3. Test with `claude --plugin-dir .`

## Hook Types Reference

| Type | When it runs | Can block? | Returns JSON? |
|------|--------------|------------|---------------|
| PreToolUse | Before tool execution | Yes | Yes |
| PostToolUse | After tool execution | No | No |
| SessionStart | Session begins | No | Yes (can add context) |
| SessionEnd | Session ends | No | No |
| Notification | Various events | No | No |

For more information, see [Claude Code Hooks Documentation](https://docs.anthropic.com/claude/docs/hooks).
