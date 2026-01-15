# AI Code Skills for Claude Code

A collection of focused plugins that enhance your development workflow with intelligent git hooks, intent-based development, notifications, presentations, and more.

## Plugins

Organized by single responsibility principle. Choose the plugins that fit your workflow:

### 🎯 [Intents Plugin](./plugins/intents/)

Spec-driven development with intent-based task management.

**Skills:**
- `/intent-start` - Start a new intent with structured spec
- `/intent-finish` - Complete and archive intents with PR summaries
- `/intent-list` - View all open intents and progress

### 🔔 [Notifications Plugin](./plugins/notifications/)

Local and remote notifications when Claude needs attention.

**Hooks:**
- Local macOS notifications
- Telegram alerts
- ntfy.sh push notifications

### 🎨 [Presentations Plugin](./plugins/presentations/)

Generate Marp presentations from your intent specs.

**Skills:**
- `/presentation` - Create presentation slides from intent

### 💻 [Development Plugin](./plugins/development/)

Development workflow automation: formatting, session tracking, and audio feedback.

**Hooks:**
- Auto-code formatting (Prettier, phpcbf)
- Session context injection (git status, branch, commits)
- Session summaries (basic and AI-powered)
- Audio announcements for commits (macOS)

## Installation

### Install Individual Plugins

Each plugin is independent and can be installed separately:

```bash
# Install just the plugins you need
claude plugin install sejas/ai-code-skills@intents
claude plugin install sejas/ai-code-skills@notifications
claude plugin install sejas/ai-code-skills@presentations
claude plugin install sejas/ai-code-skills@development
```

### Install All Plugins

Or install everything at once by installing the main repository:
```bash
claude plugin install sejas/ai-code-skills
```

### Update Plugins

Update all installed plugins to the latest version:
```bash
# Update all plugins from this repository
claude plugin update intents
claude plugin update notifications
claude plugin update presentations
claude plugin update development
```

### Development/Testing

Load plugins during development:
```bash
# From repository root, load all plugins
claude --plugin-dir .

# Or specify path
claude --plugin-dir /path/to/ai-code-skills

# Load specific plugin
claude --plugin-dir /path/to/ai-code-skills/plugins/intents
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

Uninstall individual plugins:
```bash
# Uninstall specific plugins
claude plugin uninstall intents
claude plugin uninstall notifications

# Or uninstall all at once
claude plugin uninstall intents notifications presentations development
```

## Configuration

Each plugin is independently configured via its `plugin.json` manifest. No manual `settings.json` editing required!

### Customize Hook Behavior

To customize hook behavior, clone the repository, edit the scripts, and use development mode:
```bash
git clone https://github.com/sejas/ai-code-skills.git
cd ai-code-skills

# Edit a specific plugin's hooks
vi plugins/development/hooks/auto-format.sh

# Load with your changes
claude --plugin-dir ./plugins/development
```

### Plugin-Specific Configuration

Each plugin has its own README with configuration details:
- **Notifications** - Environment variables for Telegram, ntfy.sh, etc.
- **Development** - Code formatter preferences
- **All others** - No special configuration needed

### Available macOS Voices

For text-to-speech customization in the Development plugin, edit `plugins/development/hooks/speak-commit.sh` and change the voice:
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

### Remote Notifications Setup

Get notified on your phone or other devices when Claude needs attention!

See the [Notifications Plugin README](./plugins/notifications/) for detailed setup instructions.

**Quick Setup:**

**Step 1: Copy the environment template**
```bash
cp plugins/notifications/.env.example .env
```

**Step 2: Configure your preferred notification service(s)**

#### Option A: Telegram
1. Create a bot via [@BotFather](https://t.me/BotFather) on Telegram
2. Get your bot token and your chat ID from [@userinfobot](https://t.me/userinfobot)
3. Add to `.env`:
```bash
CLAUDE_TELEGRAM_TOKEN=your-bot-token
CLAUDE_TELEGRAM_CHAT_ID=your-chat-id
```

#### Option B: ntfy.sh
1. Choose a unique topic name
2. Subscribe on [ntfy.sh](https://ntfy.sh)
3. Add to `.env`:
```bash
CLAUDE_NTFY_TOPIC=your-topic-name
```

**Step 3:** Remote notifications will work automatically!

**Note:** The `.env` file is gitignored and will never be committed.

## Requirements

### Required
- **Git** - For all git-related skills and hooks
- **Claude Code** - Latest version with plugin support

### Optional (by plugin)
- **macOS** - For text-to-speech in Development plugin
- **terminal-notifier** - For macOS notifications in Notifications plugin
- **Node.js/npm/npx** - For prettier auto-formatting (Development) and Marp presentations (Presentations)
- **PHP/Composer** - For PHP code formatting (Development)
- **Python 3 + claude-agent-sdk** - For AI-powered session summaries (Development)

## Troubleshooting

### Plugins not loading?
```bash
# Check installed plugins
claude plugin list

# Try reinstalling a specific plugin
claude plugin uninstall intents
claude plugin install sejas/ai-code-skills@intents
```

### Hooks not running?
```bash
# Check if hooks are executable
ls -la plugins/development/hooks/

# Make hooks executable
chmod +x plugins/*/hooks/*.sh

# Debug mode to see hook execution
claude --debug
```

### Text-to-speech not working?
```bash
# Test manually
say "Hello from Claude Code"

# Check if voice exists
say -v Samantha "Test"

# Note: macOS only - won't work on Linux
```

### Notifications not working?
```bash
# Verify environment variables
echo $CLAUDE_TELEGRAM_TOKEN
echo $CLAUDE_NTFY_TOPIC

# Test Telegram manually
curl -X POST "https://api.telegram.org/bot${CLAUDE_TELEGRAM_TOKEN}/sendMessage" \
  -H "Content-Type: application/json" \
  -d "{\"chat_id\": \"${CLAUDE_TELEGRAM_CHAT_ID}\", \"text\": \"Test\"}"
```

## Development

### Project Structure

```
ai-code-skills/
├── plugins/                          # Individual plugins
│   ├── intents/                     # Intent management plugin
│   │   ├── plugin.json
│   │   ├── README.md
│   │   └── commands/
│   │       ├── intent-start/
│   │       ├── intent-finish/
│   │       └── intent-list/
│   ├── notifications/               # Notifications plugin
│   │   ├── plugin.json
│   │   ├── README.md
│   │   ├── .env.example
│   │   └── hooks/
│   ├── presentations/               # Presentations plugin
│   │   ├── plugin.json
│   │   ├── README.md
│   │   └── commands/
│   └── development/                 # Development plugin
│       ├── plugin.json
│       ├── README.md
│       ├── commands/
│       └── hooks/
├── .claude-plugin/                  # Legacy (deprecated)
├── .mcp.json                        # MCP servers configuration
└── README.md                        # This file
```

### Creating New Plugins

1. Create a new directory in `plugins/your-plugin/`
2. Add `plugin.json` with metadata and hooks configuration
3. Create `README.md` documenting the plugin
4. Add `commands/` or `hooks/` subdirectories as needed

### Creating New Hooks

1. Add script to `plugins/your-plugin/hooks/` directory
2. Make executable: `chmod +x plugins/your-plugin/hooks/your-hook.sh`
3. Register in `plugins/your-plugin/plugin.json`

### Creating New Skills

1. Create directory in `plugins/your-plugin/commands/`
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

Antonio Sejas

## Version

0.3.0

### Changelog

**v0.3.0** - Split Plugins by Single Responsibility
- 🎯 5 focused plugins (intents, notifications, presentations, development)
- 📦 Each plugin with independent plugin.json and README
- 🔄 Install only what you need or install all at once
- 📚 Comprehensive documentation for each plugin
- 🏗️ Cleaner architecture following single responsibility principle

**v0.2.0** - Simplified Installation
- ✨ Auto-configuration of all hooks via manifest
- 🚀 One-command install: `claude plugin install sejas/ai-code-skills`
- 📦 Hooks use `${CLAUDE_PLUGIN_ROOT}` for portable paths
- 📝 Updated documentation to reflect simplified workflow

**v0.1.0** - Initial Release
- 8 hooks (commit validator, auto-format, text-to-speech, notifications, etc.)
- 5 skills (commit, intent-start, intent-finish, intent-list, presentation)
- Intent-based development workflow
- MCP server integration for Playwright
