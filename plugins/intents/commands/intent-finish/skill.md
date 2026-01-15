---
name: intent-finish
description: Mark an intent as complete and move to done folder. Use when the user has finished working on an intent and wants to document completion, add PR links, and archive it.
user-invocable: true
---

# Intent Finish

You are helping the user mark an intent as complete.

## Workflow

1. Check `.sejas/open/` for intents - list them if multiple exist
2. Ask which intent to mark as done (if multiple) or confirm the intent
3. Read the spec.md to understand the intent
4. Generate a **pr.md** file with PR description:
   - **Title**: Brief, clear title from the spec
   - **Issue description**: Short description of what was the issue (from spec's Problem section)
   - **Proposed Changes**: How we fixed it (from spec's Solution section)
   - **Testing Instructions**: Steps to verify the fix
   - Keep it concise - extra short summary of the spec.md
5. Ask: "Was a PR created for this intent? If yes, provide the PR URL"
6. Ask: "Any final notes or learnings to document?"
7. Update the spec.md:
   - Change status from "In Progress" to "Completed"
   - Add completion date
   - Add PR link (if provided)
   - Add "## Completion Summary" section with final notes
8. Move the entire intent folder from `.sejas/open/` to `.sejas/done/`
9. Confirm the intent has been marked as complete and show the pr.md content

## Example spec.md update

```diff
- **Status:** In Progress
+ **Status:** Completed
+ **Date Completed:** YYYY-MM-DD
+ **PR:** [Link to PR](url)

+## Completion Summary
+[Final notes and learnings]
```

## Example pr.md format

```markdown
# [Title from spec]

## Issue
[Short description of what was the issue - 1-2 sentences]

## Proposed Changes
[Brief summary of how we fixed it - 2-3 bullet points]
- Change 1
- Change 2
- Change 3

## Testing Instructions
1. Step 1 to test
2. Step 2 to test
3. Expected result
```

## Important Notes

- **Base path priority:** Use the git repository root (where `.git` lives) as the base path for `.sejas/`. If not in a git repo, use the current working directory.
- To find git root, run: `git rev-parse --show-toplevel 2>/dev/null || pwd`
- The `.sejas/` folder should be a sibling of `.git/` (e.g., `/path/to/repo/.sejas/`)
- Search for intents in `<base>/.sejas/open/`
- Move completed intents to `<base>/.sejas/done/`
- Create .sejas/done/ directory if it doesn't exist
- Preserve all files when moving (spec.md, notes.md, pr.md, assets/)
- Show before/after path for confirmation
- The pr.md should be an extra short, concise summary - not a copy of the full spec
