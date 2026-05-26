# AI Code Skills

A flat collection of [Claude Code skills](https://docs.claude.com/en/docs/claude-code/skills) and supporting hooks for development, intents, presentations, and content workflows.

These are the skills I (Antonio Sejas) use day-to-day across Automattic work and personal projects. They are intentionally small, single-purpose, and composable — drop in whichever ones you find useful.

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

Each skill is invoked by typing `/<skill-name>` in Claude Code, or by triggering a phrase from the skill's description (Claude auto-routes).

### Development

| Skill | What it does | How I use it |
|---|---|---|
| `commit` | Drafts a Conventional Commit message from the staged diff and creates the commit. | `/commit` when staging is ready. Lets me skip writing commit subjects by hand. |
| `explain` | Locates a function in the codebase and explains it for a junior dev. | `/explain handleAuth` when onboarding to a new repo. |
| `worktree` | Creates an isolated git worktree from `origin/trunk` in `~/worktrees.nosync/`, copies `node_modules`. | `/worktree feat/new-thing` to start parallel feature work without polluting the main checkout. |
| `pr-review` | Lists PRs awaiting my review, checks out each branch, runs the linter, and writes a structured review doc. | Daily review pass — pick one off the list and let the skill set up the workspace. |
| `quick-pr-review` | Lightweight diff review against a GitHub PR URL (no checkout). | When I just need a fast read on a colleague's PR. |
| `ai-prs` | Lists open PRs targeting the Studio AI command with status/approval/reviewers. | Triage Studio AI PRs before standup. |
| `react-doctor` | Scans recent React changes for common issues (hook deps, key warnings, state misuse). | After finishing a React feature, before /commit. |
| `create-agents-md` | Generates `AGENTS.md` / `CLAUDE.md` for a repository documenting conventions and structure. | When starting a new repo or onboarding a coding agent. |
| `studio-debug` | Inspects WordPress Studio local sites — SQLite DB, logs, plugin/theme issues. | When a Studio site misbehaves locally. |

### Intents (spec-driven workflow)

Lightweight ticketing inside `~/claude.nosync/intents/`. Each intent is a markdown file with problem, solution, and acceptance criteria — drives focused Claude sessions.

| Skill | How I use it |
|---|---|
| `intent-start` | Begin a new intent with spec. I run this before any non-trivial work; the spec becomes the brief for follow-up sessions. |
| `intent-list` | List in-progress intents. Quick context-switch glance. |
| `intent-finish` | Mark complete, add PR links, archive to `done/`. |
| `intent-migrate` | One-shot migration of legacy local `.sejas/` intents into the global folder. |

### Standup / Daily

| Skill | How I use it |
|---|---|
| `today` | Enriched daily activity from Claude Code sessions — branches, PRs, Linear issues, what I worked on. Run at end of day. |
| `work-standup` | **Automattic-style standup** at `${STANDUP_PATH}/YYYY-MM-DD.md`. Pulls PRs from `github.com` (via `gh`) and a GitHub Enterprise host (via `context-a8c` MCP), dedupes, and appends without rewriting existing notes. Configure with `STANDUP_PATH`, `STANDUP_GH_USER`, `STANDUP_GH_USER_ENTERPRISE`, `STANDUP_ENTERPRISE_OWNER`, `STANDUP_ENTERPRISE_REPOS`. I run `/work-standup` once at end of day before posting in Slack. |
| `standup` | Older generic version of the standup tracker (Obsidian diary block with `Claude Code Session` timestamp). Kept for reference / non-a8c users. |

### Content

| Skill | How I use it |
|---|---|
| `blog-post` | Drafts a markdown blog post in `~/claude.nosync/posts/`. I outline the topic, the skill produces a first draft. |
| `question` | Answers a question and renders the answer as a styled HTML page. Useful for sharing technical explanations as a link. |
| `presentation` | Generates Marp slides from an intent spec. Turns an `intent-start` doc into a deck. |
| `og-inspect` | Inspects a URL's Open Graph / Twitter Card metadata and renders multi-platform share-card previews (Facebook, X, LinkedIn, Slack, Tumblr). |

### Productivity

| Skill | How I use it |
|---|---|
| `todo` | Adds a task to Things 3 via the `things:///` URL scheme. Voice-style: "todo: pick up groceries". |
| `context-window-statusline` | Sets up the Claude Code footer to show context window usage, token counts, and session cost. One-shot install. |

## Hooks

Standalone bash hook scripts, opt-in. Wire them into `~/.claude/settings.json` under the relevant hook events.

- `hooks/development/` — auto-format, session-context loader, save-summary, speak-commit (TTS).
- `hooks/notifications/` — local + remote notification scripts. The remote variant auto-detects Telegram / ntfy.sh from env vars (`CLAUDE_TELEGRAM_TOKEN`, `CLAUDE_TELEGRAM_CHAT_ID`, `CLAUDE_NTFY_TOPIC`). **Never commit your actual token values** — keep them in a `.env` file (gitignored) and source it from your shell rc.
- `hooks/standup-tracker/` — end-of-session reminder that nudges me to run `/work-standup` before logging off.
- `hooks/statusline/` — the script behind the `context-window-statusline` skill.

## Secrets

This repo never commits tokens, API keys, or chat IDs. The `.env` file (containing `CLAUDE_TELEGRAM_TOKEN`, `CLAUDE_TELEGRAM_CHAT_ID`, `CLAUDE_NTFY_TOPIC`) is gitignored — populate it locally on each machine.

## License

MIT — see [LICENSE](./LICENSE).
