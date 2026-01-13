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

### Skills/Commands (4 total)

1. **/commit** - Intelligent commit message generation following repo conventions
2. **/intent-start** - Start spec-driven development with structured intent tracking
3. **/intent-finish** - Complete intents with PR descriptions and archiving
4. **/intent-list** - List all open intents with progress tracking

## Installation

### Option 1: Install from GitHub (Recommended for distribution)

1. **Create a GitHub repository** for this plugin:
   ```bash
   cd dev-workflow-plugin
   git init
   git add .
   git commit -m "feat: initial plugin release"
   git remote add origin https://github.com/YOUR_USERNAME/dev-workflow-plugin.git
   git push -u origin main
   ```

2. **On any computer**, install via Claude Code:
   ```bash
   claude plugin install github:YOUR_USERNAME/dev-workflow-plugin
   ```

### Option 2: Install Locally (For testing/development)

1. **Copy the plugin directory** to the target machine

2. **Install locally**:
   ```bash
   claude plugin install /path/to/dev-workflow-plugin
   ```

### Option 3: Manual Installation

1. **Copy plugin to Claude's plugins directory**:
   ```bash
   # Create a unique plugin directory
   mkdir -p ~/.claude/plugins/cache/local/dev-workflow/0.1.0

   # Copy all plugin files
   cp -r dev-workflow-plugin/* ~/.claude/plugins/cache/local/dev-workflow/0.1.0/
   ```

2. **Register the plugin** in `~/.claude/plugins/installed_plugins.json`:
   ```json
   {
     "version": 2,
     "plugins": {
       "dev-workflow@local": [
         {
           "scope": "user",
           "installPath": "/Users/YOUR_USERNAME/.claude/plugins/cache/local/dev-workflow/0.1.0",
           "version": "0.1.0",
           "installedAt": "2026-01-13T00:00:00.000Z",
           "lastUpdated": "2026-01-13T00:00:00.000Z"
         }
       ]
     }
   }
   ```

3. **Restart Claude Code**

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

# Create a commit with AI-generated message
/commit

# Complete an intent and generate PR description
/intent-finish
```

## Configuration

### Customize Hook Behavior

Edit hooks in your installation directory:
```bash
# Change commit message max length
vi ~/.claude/plugins/cache/local/dev-workflow/0.1.0/hooks/commit-validator.sh

# Change text-to-speech voice
vi ~/.claude/plugins/cache/local/dev-workflow/0.1.0/hooks/speak-commit.sh
```

### Available macOS Voices

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

## Uninstalling

```bash
claude plugin uninstall dev-workflow
```

Or manually:
```bash
rm -rf ~/.claude/plugins/cache/local/dev-workflow
# Remove entry from ~/.claude/plugins/installed_plugins.json
```

## Requirements

- **macOS** (for text-to-speech and notifications)
- **Git** (for all git-related hooks and skills)
- **Node.js/npm** (optional, for prettier auto-formatting)
- **PHP/Composer** (optional, for PHP code formatting)
- **Python 3 + anthropic-sdk** (optional, for AI-powered session summaries)

## Troubleshooting

### Hooks not running?
```bash
# Ensure execute permissions
chmod +x ~/.claude/plugins/cache/local/dev-workflow/0.1.0/hooks/*.sh
```

### Skills not appearing?
```bash
# Restart Claude Code
claude --version  # This reloads plugins
```

### Text-to-speech not working?
```bash
# Test manually
say "Hello from Claude Code"

# Check if voice exists
say -v Samantha "Test"
```

## Development

### Project Structure
```
dev-workflow-plugin/
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

0.1.0
