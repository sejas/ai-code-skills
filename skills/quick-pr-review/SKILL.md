---
name: quick-pr-review
description: >-
  This skill should be used when the user asks to "quick review a PR",
  "fast pr review", "review this PR without checkout", "review PR diff",
  or provides a GitHub PR URL for lightweight review. Reads PR description,
  fetches Linear issue context, reviews the diff, and outputs a markdown review
  file opened in Obsidian.
user-invocable: true
allowed-tools: ["Bash", "Read", "Write",
  "mcp__plugin_context-a8c_context-a8c__context-a8c-load-provider",
  "mcp__plugin_context-a8c_context-a8c__context-a8c-execute-tool"]
---

# Quick PR Review

Lightweight, remote-only code review. No worktrees, no checkouts, no linting — fetch PR data via `gh`, review the diff, write markdown, open in Obsidian.

## Configuration

- **Output folder:** `~/claude.nosync/reviews/`
- **Filename format:** `YYYY-MM-DD-{project}-{pr-number}-{linearid}-{pr-title}.md`
## Workflow

### Step 1: Parse PR Input & Parallel Fetch

The user provides either a GitHub URL (`github.com/{owner}/{repo}/pull/{number}`) or a PR number.

**If just a number:** detect repo: `gh repo view --json nameWithOwner --jq '.nameWithOwner'`

Once you have `OWNER/REPO` and `PR_NUMBER`, launch **all of these in parallel** (single message, multiple tool calls):

1. **Bash:** `gh pr view <PR_NUMBER> --repo <OWNER/REPO> --json title,body,author,baseRefName,headRefName,url,files,additions,deletions`
2. **Bash:** `gh pr diff <PR_NUMBER> --repo <OWNER/REPO>`
3. **Bash:** `mkdir -p ~/claude.nosync/reviews`

### Step 2: Extract Linear ID & Fetch Issue

From PR metadata (now available), extract a Linear ID matching `[A-Z]{2,10}-\d+` from:
1. The PR body
2. The head branch name

If found, fetch the issue using the **context-a8c Linear provider**:
1. Load provider: `mcp__plugin_context-a8c_context-a8c__context-a8c-load-provider` with `provider: "linear"`
2. Execute tool to get issue details: `mcp__plugin_context-a8c_context-a8c__context-a8c-execute-tool` with the appropriate Linear search tool
Store: `LINEAR_TITLE`, `LINEAR_URL`, `LINEAR_DESCRIPTION`.

If no Linear ID found, skip.

### Step 3: Analyze & Generate Review

Review the diff focusing on **high-impact issues only**:

- **Bugs:** Logic errors, off-by-one, null/undefined access, race conditions
- **Security:** Injection, auth bypass, data exposure, unsafe input handling
- **Data integrity:** Data loss risks, incorrect state mutations, missing validation
- **Readability:** Confusing logic, misleading names, overly complex flow (only if significant)

**Do NOT flag:** minor style, trivial naming, missing comments on clear code, linter-catchable issues.

Compose the review markdown:

```markdown
# PR Review: [#<number> - <title>](<PR_URL>)

**Author:** @<author> | **Branch:** <head> -> <base> | **Date:** <YYYY-MM-DD>
**Linear:** [<LINEAR_ID>](<LINEAR_URL>) - <LINEAR_TITLE>

## Context

<2-3 sentence summary combining PR description and Linear issue context.>

## Files Changed

<fileCount> files (+<additions> -<deletions>)

| File | Changes |
|------|---------|
| path/to/file.ts | +10 -5 |

## Findings

### Critical Issues

<Major bugs, security issues, data loss risks. If none: "No critical issues found.">

### Suggestions

**`path/to/file.ts:42`** - <description>

<Problem, fix, and why it matters.>

```suggestion
// code suggestion if applicable
```

---

### Positive Notes

<Good patterns, clean code, effective solutions. Always include at least one.>

## Verdict

**Recommendation:** <Approve | Request Changes>

<1-2 sentence summary.>
```

**Rules:**
- Omit `**Linear:**` line if no Linear ID found.
- Critical Issues = genuine blockers only.
- Include `path/to/file:line` where possible.
- Quality over quantity.

### Step 4: Write Markdown & Open in Obsidian

1. **Write** the review markdown to `~/claude.nosync/reviews/<filename>.md`

2. **Open in Obsidian** using the URI scheme so it navigates to the note:
```bash
open "obsidian://open?vault=sejas&file=claude.nosync%2Freviews%2F<filename>.md"
```

Report the `.md` file path to the user.

## Filename Convention

Format: `YYYY-MM-DD-{project}-{pr-number}-{linearid}-{pr-title}`

Use `.md` extension.

- `{project}`: repo name, lowercase
- `{linearid}`: lowercase Linear ID. **Omit segment** if none found.
- `{pr-title}`: lowercase, spaces->hyphens, alphanumeric+hyphens only, max 50 chars, trim trailing hyphens.

## Rules

- **NO checkout, NO worktrees, NO git clone.** Remote-only.
- **DO NOT post to GitHub** or approve/reject without explicit user request.
- Focus on high-impact findings. Skip trivial issues.
- Always include positive observations.
- Be specific (file paths + line numbers) and constructive.
- For large PRs (>1000 lines), note you focused on critical areas.
