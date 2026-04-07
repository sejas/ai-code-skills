---
name: commit
description: Write a commit message and create a git commit. Use when the user wants to commit changes, asks for a commit message, or says "commit this" or "make a commit".
user-invocable: true
---

# Commit

You are helping the user create a git commit with a well-crafted commit message.

## Workflow

1. Run these commands in parallel:
   - `git status` - See staged and unstaged files
   - `git diff --cached` - See staged changes
   - `git diff` - See unstaged changes
   - `git log --oneline -10` - See recent commit message style

2. Analyze the changes:
   - Understand what changed (new feature, bug fix, refactor, docs, etc.)
   - Identify the scope/area affected
   - Determine the "why" behind the changes

3. Draft a commit message following these principles:
   - **First line**: Concise summary (50 chars or less, imperative mood)
   - **Format**: `type: brief description` or just `brief description`
   - **Types**: feat, fix, refactor, docs, test, chore, style
   - **Match the repo's style**: Look at recent commits and follow their convention
   - **Focus on "why"**: Not just what changed, but why it matters
   - **No fluff**: Skip obvious details, be direct

4. Stage any relevant unstaged files if needed (ask user first if unclear)

5. Create the commit:
   ```bash
   git commit -m "$(cat <<'EOF'
   Your commit message here.

   Additional details if needed.
   EOF
   )"
   ```

6. CRITICAL: Run `git status` after committing to verify success

## Important Rules

- **NEVER** include `Co-Authored-By:` in the commit message
- **NEVER** add co-author tags or attribution lines
- **DO NOT** push to remote unless explicitly asked
- **DO NOT** use `--amend` unless explicitly requested
- **DO NOT** commit files with secrets (.env, credentials, etc.)
- Use HEREDOC format for multi-line messages
- Keep it simple and focused

## Examples of Good Commit Messages

```
feat: add dark mode toggle to settings

fix: prevent crash when API returns null user

refactor: extract validation logic into separate module

docs: update API authentication examples

test: add coverage for edge cases in parser
```

## Style Matching

Match the repository's commit style by examining `git log`. Common patterns:
- Conventional commits: `type(scope): description`
- Imperative mood: "add feature" not "added feature"
- Sentence case vs lowercase
- With/without type prefixes
- Single line vs multi-line

Adapt to what you observe in the recent history.
