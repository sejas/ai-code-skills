# Git Workflow Plugin

Git commit automation and validation with conventional commits support.

## Overview

This plugin automates git commit workflows with validation to ensure commit messages follow best practices and conventions. It prevents common mistakes while keeping your git history clean and readable.

## Skills

### `/commit`

Create a well-crafted git commit with best practices.

The skill will:
1. Show your git status and recent commits
2. Analyze the changes you've made
3. Draft a semantic commit message
4. Create the commit with proper formatting
5. Verify the commit succeeded

**Usage:**
```
/commit
```

## Hooks

### `commit-validator.sh` (PreToolUse)

Validates git commits before they execute. Enforces:

1. **Conventional Commits** - Messages must start with a type prefix
   - Valid types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `perf`, `ci`, `build`, `revert`, `add`, `update`, `remove`
   - Example: `feat: add dark mode toggle`

2. **Message Length** - Max 75 characters for the first line

3. **Force Push Prevention** - Blocks `-f` flag on commits
   - Prevents accidental force commits

## Commit Message Best Practices

### Format

```
type: brief description

Optional body with more details
```

### Examples

```
feat: add authentication to API endpoints

fix: prevent null pointer exception in parser

docs: update installation instructions

refactor: extract validation logic into separate module
```

### Types

- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation changes
- `style` - Code style (formatting, semicolons, etc.)
- `refactor` - Code refactoring
- `test` - Adding or updating tests
- `chore` - Build process, dependencies, tooling
- `perf` - Performance improvements
- `ci` - CI/CD configuration
- `build` - Build system changes

## Configuration

No configuration needed! The plugin validates commits automatically.

To disable validation, uninstall this plugin.

## Installation

```bash
claude plugin install sejas/ai-code-skills@git-workflow
```

## Related Plugins

- **development** - Code formatting and session tracking
- **notifications** - Get alerted when commits are ready

## License

MIT
