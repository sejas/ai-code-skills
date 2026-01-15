# Notifications Plugin

Send local and remote notifications when Claude needs your attention.

## Overview

This plugin automatically notifies you when Claude Code needs input, permissions, or has been waiting for feedback. It supports multiple notification backends for flexibility.

## Hooks

### Local Notifications (macOS)

**`notify.sh`** - Sends native macOS desktop notifications when Claude needs attention.

Requires: `terminal-notifier` (install with `brew install terminal-notifier`)

### Remote Notifications

**`remote-notify.sh`** - Sends remote notifications via Telegram or ntfy.sh, perfect for long-running tasks.

Supported backends:
- **Telegram** - Real-time alerts on your phone
- **ntfy.sh** - Simple push notifications with no account needed

## Configuration

### Telegram Setup

1. Create a Telegram bot via [@BotFather](https://t.me/botfather)
2. Get your bot token
3. Get your chat ID from [@userinfobot](https://t.me/userinfobot)
4. Add to `.env`:

```bash
CLAUDE_TELEGRAM_TOKEN=your-bot-token
CLAUDE_TELEGRAM_CHAT_ID=your-chat-id
```

### ntfy.sh Setup

1. Choose a unique topic name (e.g., `claude-notifications-yourname`)
2. Subscribe to it at https://ntfy.sh/your-topic-name
3. Add to `.env`:

```bash
CLAUDE_NTFY_TOPIC=your-topic-name
```

Optional: Use your own ntfy.sh server:
```bash
CLAUDE_NTFY_SERVER=https://your-server.com
```

## Environment Variables

All environment variables are optional. The plugin gracefully handles missing backends.

```bash
# Telegram
CLAUDE_TELEGRAM_TOKEN=          # Bot token from @BotFather
CLAUDE_TELEGRAM_CHAT_ID=        # Your chat ID

# ntfy.sh
CLAUDE_NTFY_TOPIC=              # Your topic name
CLAUDE_NTFY_SERVER=             # Optional: custom server (default: https://ntfy.sh)
```

### Where to Place .env

1. **Local project**: Create `.env` in your project root
2. **Global**: Create `~/.claude/.env` for all projects
3. Both locations are supported - local takes precedence

## Installation

```bash
claude plugin install sejas/ai-code-skills@notifications
```

## Supported Events

The plugin notifies you on:
- **permission_prompt** - When Claude needs to use a tool
- **idle_prompt** - When Claude has been waiting for input (60+ seconds)

## Future Backends

The plugin is designed to be extensible. Easy to add support for:
- Discord Webhooks
- Slack Webhooks
- Pushover
- Custom webhooks

## License

MIT
