---
name: intent-list
description: List all open intents with progress tracking. Use when the user wants to see what intents are in progress, check completion status, or get an overview of their work.
user-invocable: true
---

# Intent List

You are helping the user view their intents.

## Workflow

1. Check if `.sejas/open/` exists
2. List all folders in `.sejas/open/`
3. For each intent folder:
   - Read the spec.md file
   - Extract: title, date started, and status
   - Show a summary

4. Display in this format:
   ```
   ## Open Intents

   ### 1. [Intent Title]
   - **Folder:** .sejas/open/YYYY-MM-DD-description/
   - **Started:** YYYY-MM-DD
   - **Status:** In Progress
   - **Requirements:** X/Y completed

   ### 2. [Another Intent]
   ...
   ```

5. If no open intents exist, say: "No open intents found. Use `/intent-start` to begin a new intent."

6. Optionally, offer to show done intents if the user wants to see them

## Important Notes

- **Base path priority:** Use the git repository root (where `.git` lives) as the base path for `.sejas/`. If not in a git repo, use the current working directory.
- To find git root, run: `git rev-parse --show-toplevel 2>/dev/null || pwd`
- The `.sejas/` folder should be a sibling of `.git/` (e.g., `/path/to/repo/.sejas/`)
- Search for open intents in `<base>/.sejas/open/`
- Search for done intents in `<base>/.sejas/done/`
- Count checkboxes in spec.md to show progress (e.g., "3/5 requirements completed")
- Sort by date (newest first)
- Make the output scannable and concise
