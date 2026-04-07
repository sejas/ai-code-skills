---
name: today
description: Show enriched daily activity from Claude Code sessions — branches, PRs, Linear issues, and what you worked on. Use when the user wants to see what they did today, review their daily work, or get a summary of their sessions.
user-invocable: true
---

# Today — Daily Activity Report

Generate an enriched summary of today's Claude Code activity, showing branches, PRs, Linear issues, and session details.

## Data Sources

All data lives under `~/.claude/`:

| Source | Path | Contains |
|--------|------|----------|
| User prompts | `~/.claude/history.jsonl` | Every message you typed, with timestamp, project, sessionId |
| Session transcripts | `~/.claude/projects/<encoded-path>/<sessionId>.jsonl` | Full conversations with `gitBranch` field per message |
| Session log | `~/.claude/session-log.txt` | Session durations and project names |
| Active intents | `~/.claude-intents/in-progress/` | Intent specs with Linear issue links |
| Stats cache | `~/.claude/stats-cache.json` | Aggregate daily message/session/token counts |

## Workflow

### Step 1: Extract Today's Prompts from history.jsonl

Run a Python script to parse `~/.claude/history.jsonl` and extract all entries where the timestamp falls on today's date. Each entry has: `timestamp` (epoch ms), `project`, `sessionId`, `display` (the user's message text), `pastedContents`.

```bash
python3 << 'PYEOF'
import json
from datetime import datetime

today = datetime.now().strftime('%Y-%m-%d')

with open('__HOME__/.claude/history.jsonl') as f:
    for line in f:
        d = json.loads(line)
        ts = d.get('timestamp', '')
        if isinstance(ts, (int, float)):
            dt = datetime.fromtimestamp(ts / 1000)
            if dt.strftime('%Y-%m-%d') == today:
                project = d.get('project', '?').split('/')[-1]
                sid = d.get('sessionId', '?')[:8]
                display = d.get('display', '')[:120]
                print(f'{dt.strftime("%H:%M")} | {project} | {sid} | {display}')
PYEOF
```

Replace `__HOME__` with the actual home directory path.

### Step 2: Extract Branches from Session Transcripts

Scan all session `.jsonl` files modified today across `~/.claude/projects/*/`. Read the first line of each file to get the `gitBranch` field. Collect unique (project, branch) pairs where branch is not "main" or "trunk".

```bash
python3 << 'PYEOF'
import json, glob, os
from datetime import datetime

today = datetime.now().strftime('%Y-%m-%d')
project_dirs = glob.glob(os.path.expanduser('~/.claude/projects/*/'))

seen = set()
for pdir in project_dirs:
    for jf in glob.glob(os.path.join(pdir, '*.jsonl')):
        if os.path.basename(jf).startswith('agent-'):
            continue
        mtime = datetime.fromtimestamp(os.path.getmtime(jf))
        if mtime.strftime('%Y-%m-%d') != today:
            continue
        try:
            with open(jf) as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    d = json.loads(line)
                    branch = d.get('gitBranch', '')
                    sid = d.get('sessionId', '')
                    if not sid:
                        continue
                    project = pdir.rstrip('/').split('/')[-1]
                    key = (project, sid)
                    if key not in seen and branch:
                        seen.add(key)
                        short = project.replace('-Users-macbookpro-Documents-projects-m3-nosync-', '').replace('-Users-macbookpro', '~')
                        print(f'{short} | {branch} | {sid[:8]}')
                    break
        except:
            pass
PYEOF
```

### Step 3: Deep Scan for PR URLs, Linear Issues, and Branch References

Scan all today's session transcript `.jsonl` files for:
- **GitHub PR URLs**: regex `https://github\.com/[^\s\)"'<>]+/pull/\d+`
- **GitHub repo URLs**: regex `https://github\.com/[^\s\)"'<>]+`
- **Linear issue IDs**: regex `\b[A-Z]{2,10}-\d+\b` (exclude false positives like UTF-8, ISO-8859)
- **Branch names** with issue prefixes: extract from `gitBranch` field

Search both user messages (`display` field, `message.content`) and assistant messages.

### Step 4: Check Active Intents

Read directories under `~/.claude-intents/in-progress/`. For each intent folder, read `spec.md` to extract:
- Intent name (folder name contains date, issue ID, and description)
- Linear issue ID and URL from the spec content
- Current status

### Step 5: Format the Report

Group the output into these sections:

#### Format Template

```markdown
## Today's Activity (YYYY-MM-DD)

### Branches Worked On
- **project-name** on `branch-name`
  - HH:MM — First prompt in this session
  - HH:MM — Another prompt...

### Pull Requests
- [repo/owner#number](url) — description from first mention
  - Context from the session messages

### Linear Issues
- [ISSUE-ID](linear-url) — Issue title (from intent spec if available)
  - Linked to branch: `branch-name`
  - Intent status: In Progress

### Session Timeline
| Time | Project | What |
|------|---------|------|
| HH:MM | project | First 100 chars of prompt... |

### Stats
- X sessions, Y messages, Z tool calls (from stats-cache.json for today)
```

**Rules:**
- Omit any section that has no items
- Group prompts under their branch/PR/issue when possible
- Show the session timeline as a compact table
- Extract issue titles from intent specs when available
- For branches containing issue IDs (e.g., `stu-1287-some-description`), link them to the corresponding Linear issue
- Use 24-hour time format
- Show project names in short form (strip the home directory prefix)

### Step 6: Save Report to ~/claude-today/

After generating the report, save it as both Markdown and HTML files in `~/claude-today/`.

**File naming:** Use the **target date** (the date whose data was requested) for the filename, not necessarily today's date. For example, `/today 2026-02-09` produces `2026-02-09.md` and `2026-02-09.html`.

**Directory:** `~/claude-today/` — create it if it doesn't exist (`mkdir -p ~/claude-today`).

**Consolidation:** If `~/claude-today/YYYY-MM-DD.md` already exists, read it first and merge:
- Parse the existing file's Session Timeline table entries
- Combine with the newly extracted entries
- Deduplicate by (Time, Project, What) — keep unique rows only
- Re-sort the timeline by time
- Rebuild all sections (Branches, PRs, Linear Issues) as the union of old + new data
- Overwrite both `.md` and `.html` with the consolidated result

**HTML generation:** Convert the final Markdown report to a styled HTML file. Use this approach:
1. Write the `.md` file first using the Write tool
2. Then generate the `.html` file by wrapping the markdown content in a simple HTML template with:
   - A `<style>` block with clean typography (system font stack, max-width 800px, centered)
   - Table styling with borders and padding
   - Code/pre styling with background color
   - Convert markdown to HTML: headers (`#` -> `<h1>`), tables, lists, bold, code spans, links
   - Use a Python script with basic regex-based markdown-to-HTML conversion (no external dependencies)

```bash
python3 << 'PYEOF'
import re, os

date = "TARGET_DATE"  # replaced by the actual target date
md_path = os.path.expanduser(f"~/claude-today/{date}.md")
html_path = os.path.expanduser(f"~/claude-today/{date}.html")

with open(md_path) as f:
    md = f.read()

# Basic markdown to HTML conversion
html = md
html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)
html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', html)

# Convert tables
def convert_table(match):
    lines = match.group(0).strip().split('\n')
    rows = [l for l in lines if not re.match(r'^\|[-| ]+\|$', l)]
    out = '<table>\n'
    for i, row in enumerate(rows):
        cells = [c.strip() for c in row.strip('|').split('|')]
        tag = 'th' if i == 0 else 'td'
        out += '<tr>' + ''.join(f'<{tag}>{c}</{tag}>' for c in cells) + '</tr>\n'
    out += '</table>'
    return out
html = re.sub(r'(\|.+\|(?:\n\|.+\|)+)', convert_table, html)

# Convert list items
html = re.sub(r'^- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
html = re.sub(r'^  - (.+)$', r'<li class="nested">\1</li>', html, flags=re.MULTILINE)
html = re.sub(r'(<li[^>]*>.*</li>\n?)+', lambda m: '<ul>' + m.group(0) + '</ul>', html)

# Wrap paragraphs (lines not already tagged)
lines = html.split('\n')
result = []
for line in lines:
    stripped = line.strip()
    if stripped and not stripped.startswith('<'):
        result.append(f'<p>{stripped}</p>')
    else:
        result.append(line)
html = '\n'.join(result)

template = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Activity Report — {date}</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; max-width: 800px; margin: 2rem auto; padding: 0 1rem; color: #1a1a1a; line-height: 1.6; }}
  h1, h2, h3 {{ margin-top: 1.5em; }}
  h1 {{ border-bottom: 2px solid #333; padding-bottom: 0.3em; }}
  h2 {{ border-bottom: 1px solid #ddd; padding-bottom: 0.2em; }}
  table {{ border-collapse: collapse; width: 100%; margin: 1em 0; }}
  th, td {{ border: 1px solid #ddd; padding: 8px 12px; text-align: left; }}
  th {{ background: #f5f5f5; font-weight: 600; }}
  tr:nth-child(even) {{ background: #fafafa; }}
  code {{ background: #f0f0f0; padding: 2px 6px; border-radius: 3px; font-size: 0.9em; }}
  ul {{ padding-left: 1.5em; }}
  li.nested {{ margin-left: 1.5em; }}
  a {{ color: #0066cc; }}
</style>
</head>
<body>
{html}
</body>
</html>"""

with open(html_path, 'w') as f:
    f.write(template)
print(f"Saved: {html_path}")
PYEOF
```

**Output to user:** After saving, print the paths to both files:
```
Saved: ~/claude-today/YYYY-MM-DD.md
Saved: ~/claude-today/YYYY-MM-DD.html
```

### Step 7: Show Optional Argument Support

If the user passes a date argument (e.g., `/today 2026-02-09`), use that date instead of today. Filter history.jsonl and session files by that date. The output files will be named with the **requested date**, not today's date.

## Important Notes

- `history.jsonl` timestamps are epoch milliseconds — divide by 1000 for Python's `datetime.fromtimestamp()`
- Session `.jsonl` files are named `<sessionId>.jsonl` — the sessionId in history.jsonl maps to these files
- Project directory names encode the path with `-` replacing `/` (e.g., `-Users-macbookpro-Documents-projects-m3-nosync-studio`)
- Agent transcript files start with `agent-` prefix — skip these when scanning for sessions
- The `stats-cache.json` `dailyActivity` array may not include today if it hasn't been recomputed yet — fall back to counting from history.jsonl
- Always run the Python extraction scripts via Bash, do not try to read history.jsonl directly (it can be very large)
- **File output:** Always save to `~/claude-today/YYYY-MM-DD.md` and `.html` using the target date. Create the directory if needed.
- **Consolidation:** When the `.md` file already exists, merge new data with existing data — deduplicate timeline entries by (time, project, prompt text), union all branches/PRs/issues, and re-sort chronologically. Never lose previously recorded entries.
