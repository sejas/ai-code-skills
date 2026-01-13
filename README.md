# Dev Workflow Plugin for Claude Code

A comprehensive plugin that enhances your development workflow with intelligent git hooks and intent-based development skills.

## Features

### Hooks (8 total)

1. **commit-validator.sh** (PreToolUse) - Validates conventional commits, enforces max length
2. **speak-commit.sh** (PostToolUse) - Text-to-speech announcements for commits
3. **auto-format.sh** (PostToolUse) - Auto-formats code (prettier for JS/TS, phpcbf for PHP)
4. **notify.sh** (Notification) - macOS desktop notifications when Claude needs attention
5. **save-summary** (SessionEnd) - AI-powered session summaries
6. **save-summary-basic.sh** (SessionEnd) - Simple session logging
7. **save-summary.py** (SessionEnd) - Python implementation for session summaries
8. **session-context.sh** (SessionStart) - Injects git context at session start

### Skills/Commands (5 total)

1. **/commit** - Intelligent commit message generation following repo conventions
2. **/intent-start** - Start spec-driven development with structured intent tracking
3. **/intent-finish** - Complete intents with PR descriptions and archiving
4. **/intent-list** - List all open intents with progress tracking
5. **/presentation** - Generate Marp presentations from intent specifications

## Installation

### One-Command Install

Install directly from GitHub with hooks auto-configured:
```bash
claude plugin install sejas/ai-code-skills
```

That's it! The plugin will:
- ✅ Install all hooks automatically
- ✅ Register all skills/commands
- ✅ Configure MCP servers
- ✅ Set up executable permissions

No manual configuration needed!

### Update

Update to the latest version:
```bash
claude plugin update dev-workflow
```

### Development/Testing

Load plugin during development:
```bash
# From plugin directory
claude --plugin-dir .

# Or specify path
claude --plugin-dir /path/to/ai-code-skills
```

## Quick Start

### Using Hooks

The hooks are automatically active after installation. They will:
- Validate commit messages before they execute
- Announce commits with text-to-speech
- Auto-format code after editing
- Send notifications when Claude needs input
- Generate session summaries on exit
- Inject git context on startup

### Using Skills

```bash
# Start a new feature with structured planning
/intent-start

# List all open intents
/intent-list

# Create a presentation from an intent
/presentation

# Create a commit with AI-generated message
/commit

# Complete an intent and generate PR description
/intent-finish
```

## Uninstalling

```bash
claude plugin uninstall dev-workflow
```

## Configuration

All hooks are automatically configured from the plugin manifest. No manual `settings.json` editing required!

### Customize Hook Behavior

To customize hook behavior, edit the scripts in your local copy and use development mode:
```bash
git clone https://github.com/sejas/ai-code-skills.git
cd ai-code-skills

# Edit hooks as needed
vi hooks/commit-validator.sh

# Load with your changes
claude --plugin-dir .
```

### Available macOS Voices

For text-to-speech customization, edit `hooks/speak-commit.sh` and change the voice:
```bash
# List all voices
say -v "?"

# Popular options:
# - Samantha (default, female)
# - Alex (male)
# - Daniel (British male)
# - Fiona (Scottish female)
# - Karen (Australian female)
```

## Requirements

- **macOS** (for text-to-speech and notifications)
- **Git** (for all git-related hooks and skills)
- **Node.js/npm/npx** (optional, for prettier auto-formatting and Marp presentations)
- **PHP/Composer** (optional, for PHP code formatting)
- **Python 3 + anthropic-sdk** (optional, for AI-powered session summaries)

## Troubleshooting

### Plugin not loading?
```bash
# Check installed plugins
claude plugin list

# Try reinstalling
claude plugin uninstall dev-workflow
claude plugin install sejas/ai-code-skills
```

### Hooks not running?
```bash
# Debug mode to see hook execution
claude --debug

# Verify hook scripts are executable
ls -la ~/.claude/plugins/*/dev-workflow/*/hooks/
```

### Text-to-speech not working?
```bash
# Test manually
say "Hello from Claude Code"

# Check if voice exists
say -v Samantha "Test"

# macOS only - won't work on Linux
```

## Development

### Project Structure
```
ai-code-skills/
├── .claude-plugin/
│   └── plugin.json           # Plugin metadata
├── hooks/                    # All hook scripts
│   ├── commit-validator.sh
│   ├── speak-commit.sh
│   ├── auto-format.sh
│   └── ...
├── commands/                 # All skills/commands
│   ├── commit/
│   │   └── skill.md
│   ├── intent-start/
│   │   └── skill.md
│   └── ...
└── README.md                # This file
```

### Creating New Hooks

1. Add script to `hooks/` directory
2. Make executable: `chmod +x hooks/your-hook.sh`
3. Document in this README

### Creating New Skills

1. Create directory in `commands/`
2. Add `skill.md` with frontmatter:
   ```markdown
   ---
   name: your-skill
   description: What it does
   user-invocable: true
   ---

   # Your Skill Name

   Instructions for Claude...
   ```

## License

MIT

## Author

Antonio Sejas <antonio@sejas.es>

## Version

0.2.0

### Changelog

**v0.2.0** - Simplified Installation
- ✨ Auto-configuration of all hooks via manifest
- 🚀 One-command install: `claude plugin install sejas/ai-code-skills`
- 📦 Hooks use `${CLAUDE_PLUGIN_ROOT}` for portable paths
- 📝 Updated documentation to reflect simplified workflow
- 🔄 Easy updates via `claude plugin update dev-workflow`

**v0.1.0** - Initial Release
- 8 hooks (commit validator, auto-format, text-to-speech, notifications, etc.)
- 5 skills (commit, intent-start, intent-finish, intent-list, presentation)
- Intent-based development workflow
- MCP server integration for Playwright
