---
name: ai-prs
description: List all open PRs targeting the Studio AI command with draft status, approval state, and requested reviewers
user_invocable: true
---

# AI Command Open PRs

List all open GitHub PRs related to the Studio AI command and display them in a table.

## Steps

1. Run this command to fetch all open PRs with "ai" in the title:

```bash
gh pr list --state open --search "ai in:title" --limit 30 --json number,title,author,url,isDraft,reviewDecision,reviewRequests --jq '.[] | "\(.number)\t\(.title)\t\(.author.login)\t\(.isDraft)\t\(.reviewDecision)\t\([.reviewRequests[]? | .login // .name] | join(", "))\t\(.url)"'
```

2. Display the results in a markdown table with these columns:

| Column | Description |
|--------|-------------|
| # | PR number |
| Title | PR title |
| Author | GitHub username |
| Draft? | "Draft" (bold) if draft, "No" otherwise |
| Approved? | "Approved" if APPROVED, "Changes Requested" if CHANGES_REQUESTED, "Pending" otherwise |
| Reviewers Requested | Comma-separated list of requested reviewers, or "—" if none |
| Link | GitHub PR URL as `[PR](url)` |

3. Add a summary line below the table with counts: how many drafts, how many ready for review, how many approved.
