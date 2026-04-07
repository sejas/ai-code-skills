---
name: standup
description: Update daily Obsidian diary with PRs created, PRs reviewed, and Linear issues worked on. Run at end of work session to track your daily activity.
user-invocable: true
---

# Daily Standup Tracker

Update the user's daily Obsidian diary with work activity from this session.

## Configuration

- **Diary path:** `$STANDUP_DIARY_PATH` (set this env var to your Obsidian diary folder, e.g. `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/<vault>/Diary/`)
- **File format:** `YYYY-MM-DD.md`

## Workflow

### Step 1: Gather Data

Run these data gathering steps in parallel:

#### 1a. PRs Created Today (GitHub CLI)
```bash
gh pr list --author=@me --state=all --json url,title,number,headRefName --search "created:$(date +%Y-%m-%d)"
```

#### 1b. PRs Reviewed Today (GitHub API)
```bash
TODAY=$(date -u +%Y-%m-%dT00:00:00Z)
gh api graphql -f query='
query($from: DateTime!) {
  viewer {
    contributionsCollection(from: $from) {
      pullRequestReviewContributions(first: 50) {
        nodes {
          pullRequest {
            url
            title
            number
            headRefName
          }
        }
      }
    }
  }
}' -f from="$TODAY"
```

#### 1c. Branches Worked On Today (Git)
```bash
git reflog --date=local --since="midnight" --format="%gs" | grep -E "checkout: moving .* to " | sed 's/checkout: moving .* to //' | sort -u
```

#### 1d. Linear Issues Created Today (context-a8c)
Use the context-a8c Linear provider:
1. Load provider: `mcp__plugin_context-a8c_context-a8c__context-a8c-load-provider` with `provider: "linear"`
2. Execute tool to search issues created by me today

### Step 2: Extract Issue IDs

From gathered data, extract Linear issue IDs (patterns like `STU-1234`, `DEVELOPER-123`, etc.):
- From PR branch names (headRefName)
- From branches worked on
- Issues are typically prefixed with team codes followed by numbers

### Step 3: Query Linear for Issue Details

For each unique issue ID found, use context-a8c Linear provider to get:
- Issue title
- Issue URL
- Issue status

Also query for issues created by the user today.

### Step 4: Deduplicate

Build sets to avoid showing same item in multiple sections:
1. **PR issue IDs** - Issues linked to PRs you created
2. **Review issue IDs** - Issues linked to PRs you reviewed
3. **Issues worked on** = All branch issues - PR issue IDs - Review issue IDs

### Step 5: Read/Create Daily File

**File path:** `$STANDUP_DIARY_PATH/YYYY-MM-DD.md`

If file doesn't exist, create with template:
```markdown
#yolo-standup
Today:
- Created PRs:
	-
- Reviewed:
	-
Next:
-
```

### Step 6: Merge with Existing Block

Check if file already contains a `---\n**Claude Code Session` block.

**If exists:**
1. Parse existing items by extracting URLs from each section
2. Merge new items, skipping any URL that already exists in ANY section
3. Update timestamp to current time
4. Replace the old block with merged content

**If not exists:**
- Append new block at end of file

### Step 7: Write Output

Format the session block:

```markdown
---
**Claude Code Session (HH:MM)**
- Created PRs:
    - [PR title #number](url)
- Reviewed:
    - [PR title #number](url)
- Issues worked on:
    - [ISSUE-ID - Issue title](url)
- Issues created:
    - [ISSUE-ID - Issue title](url)
```

**Rules:**
- Omit any section that has no items
- Use 24-hour time format for timestamp
- PR format: `[Title #number](url)`
- Issue format: `[ISSUE-ID - Title](url)`

### Step 8: Confirm

Show the user:
1. Summary of what was added
2. The updated session block content
3. Confirm the file was updated

## Example Output

```markdown
---
**Claude Code Session (16:45)**
- Created PRs:
    - [Fix some bug #123](https://github.com/owner/repo/pull/123)
- Reviewed:
    - [Update some logic #124](https://github.com/owner/repo/pull/124)
- Issues worked on:
    - [STU-1234 - Backend refactor for site deletion](https://linear.app/...)
- Issues created:
    - [STU-5678 - Deep dive on Telex integration](https://linear.app/...)
```

## Important Notes

- Always use the context-a8c MCP provider for Linear data, not direct API calls
- The diary path contains spaces - handle properly in bash commands
- Parse branch names for issue IDs using regex: `[A-Z]+-[0-9]+`
- Deduplication is by URL, not by title
- Preserve user's manual notes - only modify the Claude Code Session block
