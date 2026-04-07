---
name: todo
description: This skill should be used when the user asks to "add a todo", "add a task", "remind me to", "add to things", "create a todo", "save a task", "todo", or wants to add items to their Things 3 task manager.
user-invocable: true
---

# Things 3 Todo Skill

Add tasks to Things 3 on macOS using the `things:///add` URL scheme.

## Usage

When the user provides a task (and optionally extra details), construct and open a Things URL to create the todo.

## URL Scheme

Things 3 supports the `things:///add` URL scheme with these parameters:

| Parameter      | Description                                      |
|----------------|--------------------------------------------------|
| `title`        | Task title (required)                            |
| `notes`        | Notes/description (optional)                     |
| `when`         | Due date: `today`, `tomorrow`, `evening`, `anytime`, `someday`, or YYYY-MM-DD (optional) |
| `deadline`     | Deadline date in YYYY-MM-DD format (optional)    |
| `tags`         | Comma-separated tag names (optional)             |
| `list`         | Project name to add the task to (optional)       |
| `heading`      | Heading within the project (optional)            |
| `checklist-items` | Newline-separated checklist items (optional)  |
| `show-quick-entry` | Set to `true` to show Things quick entry dialog (optional) |

## Procedure

1. Extract the task title from the user's message.
2. Identify any optional details: notes, due date, tags, project, checklist items.
3. URL-encode all parameter values.
4. Run `open "things:///add?title=...&notes=...&when=..."` via Bash.
5. Confirm the task was added.

## Encoding

Use the `scripts/encode.sh` script to properly URL-encode parameter values:

```bash
source /Users/macbookpro/.claude/skills/todo/scripts/encode.sh
encoded=$(urlencode "My task title")
```

## Examples

**Simple task:**
```bash
open "things:///add?title=Buy%20groceries"
```

**Task with due date and notes:**
```bash
open "things:///add?title=Review%20PR%20%23456&notes=Check%20edge%20cases&when=today"
```

**Task with a URL in notes:**
```bash
open "things:///add?title=Watch%20video&notes=https%3A%2F%2Fyoutube.com%2Fwatch%3Fv%3Dabc123"
```

**Task with checklist:**
```bash
open "things:///add?title=Deploy%20checklist&checklist-items=Run%20tests%0AMerge%20PR%0ADeploy"
```

**Task in a specific project:**
```bash
open "things:///add?title=Fix%20login%20bug&list=Studio&when=today"
```

## Important

- Always URL-encode special characters in all parameter values (spaces, ampersands, colons, slashes, etc.).
- If the user provides a URL, place it in the `notes` field and encode it fully.
- If no due date is specified, omit the `when` parameter (defaults to Inbox).
- Keep task titles concise; put details in notes.
