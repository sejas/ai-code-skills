---
name: intent-start
description: Start a new intent with spec-driven development. Use when the user wants to begin working on a new feature, bug fix, or task and needs to document the problem, solution, and requirements.
user-invocable: true
---

# Intent Start

You are helping the user start a new intent using spec-driven development.

## Workflow

1. Ask the user: "What are you working on?" (brief description)
2. Based on their answer, suggest a folder name in format: `YYYY-MM-DD-description` (use today's date)
3. Ask these questions to build the spec:
   - "What problem does this solve?"
   - "What's the proposed solution?"
   - "What are the key requirements?" (list 3-5 items)
   - "What are the acceptance criteria?" (how do we know it's done?)
   - "What's the implementation plan?" (break down into 3-7 concrete steps)

4. Create the folder structure:
   ```
   .sejas/open/YYYY-MM-DD-description/
   ├── spec.md
   ├── notes.md
   └── assets/
   ```

5. Write **spec.md** with this structure:
   ```markdown
   # [Intent Title]

   **Date Started:** YYYY-MM-DD
   **Status:** In Progress

   ## Problem
   [Problem statement]

   ## Solution
   [Proposed solution]

   ## Requirements
   - [ ] Requirement 1
   - [ ] Requirement 2
   - [ ] Requirement 3

   ## Acceptance Criteria
   - [ ] Criteria 1
   - [ ] Criteria 2

   ## Implementation Plan
   1. [Step 1]
   2. [Step 2]
   3. [Step 3]
   4. [Step 4]
   5. [Step 5]

   ## Notes
   [Any additional context]
   ```

6. Write **notes.md** with:
   ```markdown
   # Development Notes

   ## YYYY-MM-DD - Intent Started
   - Created spec
   - [Any initial notes from the conversation]
   ```

7. Create a todo list using TodoWrite tool:
   - Convert each step from the implementation plan into a todo item
   - Set all items to "pending" status
   - Use the imperative form for content (e.g., "Implement feature X")
   - Use the present continuous form for activeForm (e.g., "Implementing feature X")
   - This helps track progress throughout the intent lifecycle

8. Confirm intent creation and show the path

## Important Notes

- **Base path priority:** Use the git repository root (where `.git` lives) as the base path for `.sejas/`. If not in a git repo, use the current working directory.
- To find git root, run: `git rev-parse --show-toplevel 2>/dev/null || pwd`
- The `.sejas/` folder should be a sibling of `.git/` (e.g., `/path/to/repo/.sejas/`)
- Use today's date for folder name
- Keep folder name lowercase with hyphens
- Create .sejas/open/ directory if it doesn't exist
- Add .sejas to .gitignore (both global ~/.gitignore_global and local if in a repo)
