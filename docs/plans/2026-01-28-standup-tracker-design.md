# Standup Tracker Plugin Design

## Overview

A Claude Code plugin that tracks daily work (PRs created, PRs reviewed, Linear issues) and updates an Obsidian daily diary file.

## Components

### 1. `/standup` Skill

A user-invoked skill with full MCP access to gather and write standup data.

**Location:** `plugins/standup-tracker/skills/standup/skill.md`

**Data sources:**
- **GitHub CLI** - PRs created today, PRs reviewed today
- **Linear (via context-a8c)** - Issues from branches, issues created today

### 2. SessionEnd Reminder Hook

A bash script that reminds the user to run `/standup` if they haven't today.

**Location:** `plugins/standup-tracker/hooks/session-end/reminder.sh`

## Output Format

Appends/merges a single block per day to the diary file:

```markdown
---
**Claude Code Session (16:45)**
- Created PRs:
    - [Fix bug #123](url)
- Reviewed:
    - [Feature #456](url)
- Issues worked on:
    - [STU-1234 - Backend refactor](url)
- Issues created:
    - [STU-5678 - New feature](url)
```

**Rules:**
- Empty sections are omitted
- URLs are used for deduplication (same URL won't appear twice)
- Timestamp updates to most recent run
- Issues linked to created/reviewed PRs don't appear in "Issues worked on"

## Merge Logic

1. Check for existing `---\n**Claude Code Session` block in file
2. Parse existing items by URL per section
3. Gather new session data
4. For each new item: skip if URL exists in ANY section, else add
5. Rebuild block with merged items
6. Replace old block (or append if none exists)

## Data Gathering

### PRs Created (GitHub CLI)
```bash
gh pr list --author=@me --state=all --json url,title,number \
  --search "created:$(date +%Y-%m-%d)"
```

### PRs Reviewed (GitHub API)
```bash
gh api graphql -f query='
  query {
    viewer {
      contributionsCollection(from: "TODAY_ISO") {
        pullRequestReviewContributions(first: 50) {
          nodes { pullRequest { url title number } }
        }
      }
    }
  }
'
```

### Issues from Branches
```bash
# Get current branch + recently checked out branches today
git reflog --date=local --since="midnight" | grep checkout
# Extract issue IDs, query Linear via context-a8c
```

### Issues Created (Linear)
Query Linear for issues created by user today via context-a8c MCP provider.

## Deduplication Logic

1. Build set of issue IDs from created PRs (parse branch names or PR body)
2. Build set of issue IDs from reviewed PRs
3. Filter "Issues worked on" to exclude those sets

## File Path

```
~/Library/Mobile Documents/iCloud~md~obsidian/Documents/sejas/🗓️ Diary/YYYY-MM-DD.md
```

**Template for new files:**
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

## Plugin Structure

```
plugins/standup-tracker/
├── plugin.json
├── skills/
│   └── standup/
│       └── skill.md
└── hooks/
    └── session-end/
        └── reminder.sh
```

## Configuration

**plugin.json:**
```json
{
  "name": "standup-tracker",
  "description": "Track daily work and update Obsidian diary",
  "settings": {
    "STANDUP_DIARY_PATH": "~/Library/Mobile Documents/iCloud~md~obsidian/Documents/sejas/🗓️ Diary"
  }
}
```
