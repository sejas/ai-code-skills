# AI Code Skills

A flat collection of [Claude Code skills](https://docs.claude.com/en/docs/claude-code/skills) and supporting hooks for development, intents, presentations, and content workflows.

## Layout

```
skills/   # one folder per skill, each containing SKILL.md
hooks/    # standalone hook scripts grouped by purpose
```

No plugin manifest, no marketplace — just drop the folders where you want them.

## Install

Copy or symlink any skill into `~/.claude/skills/`:

```bash
ln -s "$PWD/skills/commit" ~/.claude/skills/commit
```

Or symlink the whole directory to expose every skill:

```bash
for d in skills/*/; do ln -s "$PWD/$d" "$HOME/.claude/skills/$(basename $d)"; done
```

## Skills

### Development
- `commit` — Write a commit message and create a git commit
- `explain` — Explain a function as if to a junior developer
- `worktree` — Create a new git worktree from origin/trunk
- `pr-review` — List PRs awaiting review, checkout, lint, generate review doc
- `quick-pr-review` — Lightweight PR review without checkout
- `react-doctor` — Catch React issues after changes
- `create-agents-md` — Generate AGENTS.md / CLAUDE.md for a repo

### Intents (spec-driven workflow)
- `intent-start` — Start a new intent with spec
- `intent-finish` — Complete and archive an intent
- `intent-list` — List open intents
- `intent-migrate` — Migrate local intents to global folder

### Standup / Daily
- `today` — Show enriched daily activity summary
- `standup` — Update Obsidian diary with PRs and Linear issues

### Content
- `blog-post` — Draft a markdown blog post
- `question` — Answer a question and render as HTML
- `presentation` — Generate Marp slides from an intent spec
- `og-inspect` — Inspect a URL's OG / Twitter Card metadata and render a multi-platform share-card preview

### Tools / UI
- `context-window-statusline` — Status line showing context window usage
- `studio-debug` — Debug WordPress Studio local sites

## Hooks

- `hooks/development/` — auto-format, session-context, save-summary, speak-commit
- `hooks/notifications/` — local + remote notification scripts
- `hooks/standup-tracker/` — end-of-session reminder
- `hooks/statusline/` — context-window status line script

Wire these into `~/.claude/settings.json` under the relevant hook events.

## License

MIT — see [LICENSE](./LICENSE).
