---
name: work-standup
description: Create or update today's work standup file. Pulls PR activity from a GitHub Enterprise host (via context-a8c MCP) and github.com (via gh CLI), deduplicates across sources and sections, preserves existing content. Use when the user says "update my standup", "today standup", "fill my standup", or invokes /work-standup.
user-invocable: true
---

# Work Standup Tracker

Maintains a daily standup markdown file. Designed for users who work across a GitHub Enterprise host (e.g. Automattic's `github.a8c.com`) and `github.com`, but works with either source alone.

## Configuration (env vars)

Set these once (e.g. in your shell rc):

| Env var | Purpose | Example |
|---|---|---|
| `STANDUP_PATH` | Directory where daily files live | `~/Documents/notes/work/standup/` |
| `STANDUP_GH_USER` | Your `github.com` login | `your-handle` |
| `STANDUP_GH_USER_ENTERPRISE` | Your Enterprise host login (optional) | `your-handle-a8c` |
| `STANDUP_ENTERPRISE_OWNER` | Enterprise org/owner (optional) | `Automattic` |
| `STANDUP_ENTERPRISE_REPOS` | Comma-separated repo list to scan (optional) | `wpcom,studio,jetpack` |

The file is written to `${STANDUP_PATH}/YYYY-MM-DD.md` using today's local date.

## Output format (match exactly)

```
#yolo-standup 
Today:

- Created PRs:
    - [<auto-title>](<pr-url>)
- Merged:
    - [<auto-title>](<pr-url>)
- Reviewed:
    - [<auto-title>](<pr-url>)

<free-form bullets / notes at top level, no header>

Next:
- <bullet>
```

**Auto-title pattern:** `<PR title> by <author> · Pull Request #<number> · <owner>/<repo>` — matches GitHub's own `<title>` element.

**Style rules:**

- Section headers are top-level `- ` bullets ending in `:` (e.g. `- Created PRs:`).
- PR links nest one level deeper as `- ` bullets, indented with 4 spaces (or one tab).
- No inline state annotations (`— open`, `— merged`, timestamps). Section placement carries that info.
- No "Other:" header — free-form lines live at top level between Reviewed and Next.
- Sections are omitted when empty; never leave empty headers.
- Trailing space after `#yolo-standup` is intentional (file convention).

## Section rules

| Section | Inclusion rule |
|---|---|
| **Created PRs** | PRs authored by the user whose `created_at` is today (local tz). Includes PRs created today that were also merged today. |
| **Merged** | PRs authored by the user with `merged_at` today AND `created_at` < today. |
| **Reviewed** | PRs NOT authored by the user that have a review by the user with `submitted_at` today. Exclude PRs already in Created or Merged. |
| Free-form | Manual notes (meetings, blockers, learnings). Preserved verbatim. |
| **Next:** | Manual TODO bullets for tomorrow. Preserved verbatim. |

## Dedupe rules

- **Cross-section:** a PR URL appears in at most one section, priority: Created > Merged > Reviewed.
- **Cross-source:** the same PR URL must not appear twice even if it surfaces from both `gh` and the Enterprise MCP. Normalize URLs (strip trailing slash, query string) before comparing.
- **Append-aware:** if the file already lists a PR URL anywhere, do not add it again. Manually-written free-form lines stay untouched.

## Workflow

### Step 1 — Gather data, in parallel

#### 1a. GitHub Enterprise via context-a8c MCP (optional)

If `STANDUP_GH_USER_ENTERPRISE` is set, load the provider once per session:

```
mcp__context-a8c__context-a8c-load-provider  provider: "github-a8c"
```

For each repo in `STANDUP_ENTERPRISE_REPOS`:

```
mcp__context-a8c__context-a8c-execute-tool
  provider: "github-a8c"
  tool: "search-pull-requests"
  params: { query: "author:${STANDUP_GH_USER_ENTERPRISE} updated:YYYY-MM-DD", owner: "${STANDUP_ENTERPRISE_OWNER}", repo: "<repo>", perPage: 50 }
```

Then the same with `reviewed-by:${STANDUP_GH_USER_ENTERPRISE}`.

> Note: global queries return 0 results on this host; always scope by `owner` + `repo`.

If output exceeds the response limit, the MCP server saves JSON to a file path — use `jq` to extract `{number, title, state, created_at, updated_at, closed_at, merged_at, html_url, user.login, pull_request.merged_at}`.

#### 1b. github.com via gh CLI

```bash
gh pr list --author=@me --state=all \
  --json url,title,number,createdAt,mergedAt,state,headRepository,headRepositoryOwner \
  --search "created:$(date +%Y-%m-%d) OR updated:$(date +%Y-%m-%d)"
```

Reviews via GraphQL:

```bash
TODAY=$(date +%Y-%m-%d)
FROM="${TODAY}T00:00:00Z"
gh api graphql -f query='
query($from: DateTime!) {
  viewer {
    contributionsCollection(from: $from) {
      pullRequestReviewContributions(first: 50) {
        nodes { pullRequest { url title number author { login } merged createdAt } }
      }
      pullRequestContributions(first: 50) {
        nodes { pullRequest { url title number merged mergedAt createdAt state } }
      }
    }
  }
}' -f from="$FROM"
```

### Step 2 — Classify each PR

For PRs authored by the user (login = `$STANDUP_GH_USER` or `$STANDUP_GH_USER_ENTERPRISE`):

- `created_at` == today → **Created PRs**.
- `created_at` < today AND `merged_at` == today → **Merged**.
- Otherwise (still open from before today, or closed-not-merged) → ignore unless explicitly mentioned in free-form.

For PRs not authored by the user with a review submitted today → **Reviewed**, only if the URL isn't already in Created or Merged.

### Step 3 — Resolve auto-title

Build the link using the auto-title pattern. Pull `title`, `user.login`, `number`, owner/repo (from `html_url` or `repository_url`).

Example:

```
[Some PR title by your-handle · Pull Request #12345 · owner/repo](https://github.com/owner/repo/pull/12345)
```

### Step 4 — Read existing file

Path: `${STANDUP_PATH}/YYYY-MM-DD.md`. Quote the path in bash (folders may contain spaces or emoji).

If the file doesn't exist, scaffold:

```
#yolo-standup 
Today:

Next:

```

If the file exists, parse section-by-section. Collect every PR URL already present into a known-set for dedup.

### Step 5 — Merge

- For each new PR URL not in the known-set, append it to its target section in classification order (Created → Merged → Reviewed).
- Preserve every existing PR line, free-form line, and Next: bullet exactly as-is. The skill is additive — never rewrites or reorders existing content.
- If the file is missing one of the headers and there's content for it, insert the header in canonical order.
- Never insert an empty header.

### Step 6 — Write

Write the merged file. Confirm with the user:

1. New PRs added per section.
2. Duplicates skipped (per source).
3. Hosts that errored (note `github-a8c` 422 errors for repos that don't exist or are inaccessible).

## Pitfalls

- **Timezone:** GitHub returns UTC. Convert to the user's local date before comparing to "today". A PR at `2026-05-14T23:30:00Z` is `2026-05-15` for UTC+1.
- **Search index lag:** Enterprise search can lag by minutes for very fresh PRs. Retry once after a short pause; fall back to fetching by number with the `pull-request` tool if still missing.
- **Multiple repos:** when a repo returns nothing and the user expected activity, ask which repo to query rather than guessing.
- **Path quoting:** `STANDUP_PATH` may contain spaces or emoji (e.g. `💼 work/standup`). Quote everywhere in bash.
- **No revert of user edits:** if the user previously trimmed annotations, do not re-add them on the next run.

## Done criteria

- File at `${STANDUP_PATH}/YYYY-MM-DD.md` exists with today's PR activity split into Created / Merged / Reviewed.
- No URL appears in more than one section.
- No URL appears twice within a section.
- All pre-existing free-form bullets and `Next:` entries are untouched.
- Short summary printed listing what was added and what was deduped.
