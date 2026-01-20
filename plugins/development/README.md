# Development Plugin

Development workflow automation: code formatting, session tracking, code review, and quality checks.

## Overview

This plugin enhances your development experience with automatic code formatting, session summaries, PR code reviews, and audio feedback. It helps maintain code quality and provides helpful context at the start of each session.

## Commands

### `/pr-review` - Pull Request Review

List PRs awaiting your review, checkout the branch, run linter, and generate a structured code review document.

**Features:**
- Lists all PRs where you're requested as reviewer
- Shows review status (Needs Review / Already Reviewed)
- Prioritizes unreviewed PRs first
- Checks out selected PR branch
- Auto-detects and runs project linter
- Generates `pr-review.md` with structured feedback

**Usage:**
```
/pr-review
```

**Review Focus:**
- Readability: naming, structure, comments
- Maintainability: DRY, separation of concerns, testability
- Best Practices: error handling, security, performance

## Hooks

### Code Formatting

**`auto-format.sh`** (PostToolUse)

Automatically formats files after you write or edit them.

Supported languages:
- **TypeScript/JavaScript** - Uses Prettier (if installed)
- **PHP** - Uses phpcbf with WordPress standard (if installed)

Install formatters:
```bash
npm install -g prettier
composer global require phpstan/phpcbf
```

### Session Context

**`session-context.sh`** (SessionStart)

Injects git context at session start, showing:
- Current branch
- Uncommitted changes
- 5 most recent commits

This helps you understand the state of your repository without running commands.

### Session Summaries

**`save-summary-basic.sh`** (SessionEnd)

Logs session information when your session ends.

**`save-summary.py`** (SessionEnd) - Alternative

Advanced Python-based hook that uses Claude to generate intelligent session summaries. Features:
- Parses session transcript
- Generates 1-2 paragraph summary using Haiku
- Saves to `~/.claude/session-logs/`

Requires: `claude-agent-sdk` (installed automatically)

### Audio Feedback

**`speak-commit.sh`** (PostToolUse)

Announces commit messages using macOS text-to-speech (Samantha voice).

Makes commit announcements like:
- "Feature added to my-repo: add dark mode toggle"
- "Bug fixed in my-repo: prevent crash on null user"
- "Tests added to my-repo: add coverage for edge cases"

MacOS only. Skip on other platforms.

## Configuration

No configuration required! All hooks work out of the box.

### Optional: Customize Session Summaries

To use AI-powered summaries instead of basic logging, install:

```bash
pip install claude-agent-sdk
```

Then the `save-summary.py` hook will automatically generate intelligent session summaries.

## Features

### Auto-formatting
- **Fire and forget** - Formats files automatically after editing
- **Multi-language** - Supports TS/JS and PHP out of the box
- **Graceful degradation** - Skips if formatter not installed

### Session Context
- **Git status** - See uncommitted changes
- **Branch info** - Know which branch you're on
- **Commit history** - Last 5 commits for context

### Session Logging
- **Automatic** - No setup required
- **Smart summaries** - AI-generated insights (optional)
- **Searchable** - Logs organized by session ID

### Audio Feedback
- **Non-blocking** - Speaks in background
- **Natural language** - Parses commit types for better announcements
- **macOS only** - Gracefully skips on Linux/Windows

## Installation

```bash
claude plugin install sejas/ai-code-skills@development
```

## Related Plugins

- **git-workflow** - Git commit validation and automation
- **notifications** - Get alerted when Claude needs attention

## License

MIT
