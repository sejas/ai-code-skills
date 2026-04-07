---
name: context-window-statusline
description: This skill should be used when the user asks to "set up a status line", "configure the footer", "show context window usage", "add a statusline", "visualize context window", "customize the Claude Code footer", or wants to display token counts, cost, or session metrics in the Claude Code terminal footer.
---

# Context Window Status Line

Generate and install a customizable status line (footer bar) for Claude Code that visualizes context window usage, token counts, session cost, and more.

## What It Does

The status line displays a real-time dashboard at the bottom of the Claude Code terminal:

```
Opus 4.6 │ ████████░░░░░░░░░░░░ 42% (85.3kin 12.1kout cached:45.2k) of 200k
💰 $0.1234 │ ⏱  5m23s (api: 2m10s) │ +142 -37
```

## Installation

### Step 1: Copy the script

Copy `scripts/statusline.sh` to `~/.claude/statusline.sh` and make it executable:

```bash
cp scripts/statusline.sh ~/.claude/statusline.sh
chmod +x ~/.claude/statusline.sh
```

### Step 2: Configure settings.json

Add to `~/.claude/settings.json`:

```json
{
  "statusLine": {
    "type": "command",
    "command": "~/.claude/statusline.sh",
    "padding": 1
  }
}
```

The `padding` field adds blank lines around the status bar (0 = no padding, 1 = one line above and below).

## Available JSON Data

The script receives session data as JSON via `stdin`. Extract fields with `jq`:

### Model Information
| Field | Description |
|-------|-------------|
| `model.display_name` | Current model name (e.g. "Opus 4.6") |

### Context Window
| Field | Description |
|-------|-------------|
| `context_window.used_percentage` | Percentage of context used (0-100) |
| `context_window.remaining_percentage` | Percentage remaining |
| `context_window.context_window_size` | Total window size in tokens |
| `context_window.current_usage.input_tokens` | Input tokens consumed |
| `context_window.current_usage.output_tokens` | Output tokens generated |
| `context_window.current_usage.cache_read_input_tokens` | Tokens read from cache |
| `context_window.current_usage.cache_creation_input_tokens` | Tokens written to cache |

### Cost & Performance
| Field | Description |
|-------|-------------|
| `cost.total_cost_usd` | Total session cost in USD |
| `cost.total_duration_ms` | Total session wall time |
| `cost.total_api_duration_ms` | Time spent in API calls |
| `cost.total_lines_added` | Lines of code added |
| `cost.total_lines_removed` | Lines of code removed |

## Customization

### Minimal version (context bar only)

To display only the context window bar, remove line 2 from the script output. Keep only the `printf` that renders the model name, progress bar, and token counts.

### Color thresholds

Adjust the percentage thresholds in the color-selection block:
- Green: `< 40%` — plenty of room
- Cyan: `< 70%` — getting warm
- Yellow: `< 90%` — watch out
- Red: `>= 90%` — near compaction

### Bar width

Change `BAR_WIDTH=20` to any value. Wider bars give more granularity.

### Adding custom sections

Extend the script by reading additional JSON fields or injecting external data (git branch, active timers, etc.) into the output lines.

## Bundled Script

The ready-to-use script is at `scripts/statusline.sh`. It includes:
- Color-coded context window progress bar (20 chars wide)
- Token count formatting (auto-scales to k/M)
- Duration formatting (seconds/minutes/hours)
- Cost display with 4 decimal precision
- Lines added/removed counters

## Troubleshooting

- **No output**: Verify `jq` is installed (`brew install jq`)
- **Garbled colors**: Ensure terminal supports ANSI escape codes
- **Script not found**: Use absolute path or `~` in the command field
- **Slow updates**: The script runs on each render cycle; keep it fast (avoid network calls)
