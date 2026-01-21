---
name: pr-review
description: List PRs awaiting your review, checkout the branch, run linter, and generate a structured code review document.
user-invocable: true
---

# PR Review

You are helping the user review pull requests assigned to them. This skill lists PRs awaiting review, prioritizes unreviewed ones, and generates structured review documents.

## Workflow

### Phase 1: List PRs Awaiting Review

1. Get the current GitHub user and repo:
   ```bash
   gh api user --jq '.login'
   gh repo view --json nameWithOwner --jq '.nameWithOwner'
   ```

2. Fetch PRs where user is requested as reviewer:
   ```bash
   gh pr list --search "review-requested:@me" --json number,title,author,createdAt,headRefName,reviews --limit 50
   ```

3. Process and display the PR list:
   - Parse the JSON response
   - For each PR, determine review status:
     - **Needs Review**: No reviews from current user
     - **Reviewed**: User has submitted a review
   - Sort the list: unreviewed PRs first, then by creation date (oldest first)

4. Display the list using AskUserQuestion tool with format:
   ```
   PR #123: "Fix login bug" by @author [Needs Review]
   PR #456: "Add dark mode" by @author [Reviewed]
   ```

5. Let user select a PR to review (or exit)

### Phase 2: Checkout and Prepare

6. Once user selects a PR, fetch full PR details:
   ```bash
   gh pr view <number> --json number,title,body,author,headRefName,baseRefName,files,additions,deletions,commits
   ```

7. Checkout the PR branch:
   ```bash
   gh pr checkout <number>
   ```

8. Detect and run the project linter:
   - Check for common linter configs in order:
     - `package.json` → look for `lint` script → run `npm run lint` or `yarn lint`
     - `.eslintrc*` → run `npx eslint .`
     - `pyproject.toml` with ruff/flake8 → run `ruff check .` or `flake8`
     - `setup.cfg` or `.flake8` → run `flake8`
     - `.rubocop.yml` → run `rubocop`
     - `Makefile` with lint target → run `make lint`
   - If no linter found, skip and note it in the review

9. Capture linter output for inclusion in review

### Phase 3: Code Review

10. Read the changed files:
    - Use the files list from PR details
    - Read each modified file to understand the changes
    - Run `gh pr diff <number>` to see the actual diff

11. Analyze the code focusing on:
    - **Readability**: Clear naming, logical structure, appropriate comments
    - **Maintainability**: DRY principles, separation of concerns, testability
    - **Best Practices**: Error handling, security, performance
    - **Consistency**: Follows project conventions and patterns

12. Generate the review file:
    - Create directory if needed: `mkdir -p ~/.claude-intents/reviews`
    - Generate filename using format: `YYYY-MM-DD-{repo}-{PR-ID}-{branch-name}--{description}.md`
      - `{repo}`: Repository name (e.g., `my-project`)
      - `{PR-ID}`: PR number (e.g., `123`)
      - `{branch-name}`: Head branch name, sanitized (replace `/` with `-`)
      - `{description}`: PR title, lowercase, spaces to hyphens, max 50 chars, alphanumeric only
    - Example: `2026-01-20-calypso-12345-fix-login-bug--fix-authentication-crash.md`
    - Save to: `~/.claude-intents/reviews/{filename}`

## PR Review Document Template

```markdown
# PR Review: #<number> - <title>

**Author:** @<author>
**Branch:** <head> → <base>
**Reviewed by:** @<reviewer>
**Date:** <YYYY-MM-DD>

## Summary

<Brief 2-3 sentence summary of what this PR does>

## Linter Results

<Linter output or "No linter configured" or "All checks passed">

## Files Changed

| File | Changes | Status |
|------|---------|--------|
| path/to/file.js | +10 -5 | Reviewed |

## Review Findings

### ✅ What's Good

- <Positive observation 1>
- <Positive observation 2>

### ⚠️ Suggestions

#### <File or Area 1>

**Location:** `path/to/file.js:42`

**Issue:** <Description of the concern>

**Suggestion:**
```<language>
// Suggested improvement
```

**Why:** <Explanation of why this matters for readability/maintainability>

---

#### <File or Area 2>

...

### 🔴 Blockers (if any)

<Critical issues that should be addressed before merge>

## Checklist

- [ ] Code follows project conventions
- [ ] No obvious security vulnerabilities
- [ ] Error handling is appropriate
- [ ] Changes are well-tested (or tests are not applicable)
- [ ] Documentation updated if needed

## Verdict

**Recommendation:** <Approve | Request Changes | Comment>

<Final thoughts and next steps>
```

## Important Rules

- **DO NOT** post the review to GitHub automatically - just generate the local file
- **DO NOT** approve or reject the PR on GitHub without explicit user request
- **ALWAYS** focus on constructive feedback
- **PRIORITIZE** readability and maintainability over style nitpicks
- **BE SPECIFIC** with line numbers and code suggestions
- **EXPLAIN WHY** each suggestion matters
- Skip trivial issues (formatting, minor style) unless they impact readability
- If the PR is large (>500 lines), focus on the most critical files first

## Review Principles

### Readability
- Are variable/function names descriptive?
- Is the code self-documenting?
- Are complex sections commented appropriately?
- Is the control flow easy to follow?

### Maintainability
- Is the code DRY (Don't Repeat Yourself)?
- Are responsibilities properly separated?
- Would this be easy to modify or extend?
- Are there any hidden dependencies?

### Best Practices
- Are errors handled gracefully?
- Are there potential security issues?
- Are there obvious performance concerns?
- Does it follow the project's established patterns?

## File Naming Convention

Reviews are saved to `~/.claude-intents/reviews/` with this format:

```
YYYY-MM-DD-{repo}-{PR-ID}-{branch-name}--{description}.md
```

**Components:**
- `YYYY-MM-DD`: Today's date
- `{repo}`: Repository name (from `nameWithOwner`, take part after `/`)
- `{PR-ID}`: PR number
- `{branch-name}`: Head branch, with `/` replaced by `-`
- `{description}`: PR title sanitized (lowercase, spaces→hyphens, alphanumeric, max 50 chars)

**Examples:**
```
2026-01-20-calypso-245-fix-memory-leak--fix-memory-leak-in-cache.md
2026-01-20-jetpack-1234-feature-dark-mode--add-dark-mode-toggle.md
2026-01-20-woocommerce-567-bugfix-checkout--prevent-crash-on-null-user.md
```

## Example Usage

```
User: /pr-review
Assistant: [Fetches PRs, shows list]

PRs awaiting your review:

1. PR #234: "Add user authentication" by @alice [Needs Review] - 3 days ago
2. PR #245: "Fix memory leak in cache" by @bob [Needs Review] - 1 day ago
3. PR #230: "Update dependencies" by @carol [Reviewed] - 5 days ago

Which PR would you like to review?

User: [Selects PR #245]
Assistant: [Checks out branch, runs linter, reads files, generates review]

✅ Review complete! Saved to:
   ~/.claude-intents/reviews/2026-01-20-my-repo-245-fix-memory-leak--fix-memory-leak-in-cache.md
```
