# Intents Plugin

Spec-driven development with intent-based task management for Claude Code.

## Overview

This plugin provides a structured workflow for managing development work using intent-based specifications. It helps you break down complex tasks into manageable pieces with clear documentation of problems, solutions, requirements, and acceptance criteria.

## Skills

### `/intent-start`

Start a new intent with spec-driven development. Use this when you want to begin working on a new feature, bug fix, or task.

The skill will:
1. Ask what you're working on
2. Create a folder with today's date
3. Guide you through building a comprehensive spec
4. Set up a `spec.md` file with problem/solution/requirements
5. Create a `notes.md` file for development notes

**Usage:**
```
/intent-start
```

### `/intent-list`

List all open intents with progress tracking. See what's in progress and monitor completion.

**Usage:**
```
/intent-list
```

### `/intent-finish`

Mark an intent as complete and archive it. This skill will:
1. Generate a PR summary from your spec
2. Ask for PR URL and final notes
3. Move the intent to the done folder
4. Create a completion summary

**Usage:**
```
/intent-finish
```

## Directory Structure

Intents are stored in `.sejas/` (at your git repository root):

```
.sejas/
├── open/
│   └── YYYY-MM-DD-description/
│       ├── spec.md
│       ├── notes.md
│       └── assets/
└── done/
    └── YYYY-MM-DD-description/
        ├── spec.md
        ├── notes.md
        ├── pr.md
        └── assets/
```

## Installation

```bash
claude plugin install sejas/ai-code-skills@intents
```

Or combine with other plugins from this repository.

## Configuration

No configuration required! The plugin works out of the box. Intents are stored in `.sejas/` at your repository root, automatically adding to `.gitignore`.

## Related Plugins

- **presentations** - Generate Marp presentations from intent specs
- **development** - Development workflow automation

## License

MIT
