---
name: travel-routes
description: Use when user wants to extract travel routes from Apple Photos geolocation (via osxphotos), build interactive maps, list visited cities, or prepare data for summer vacation blog posts and year-in-review summaries. Triggers "travel route", "trip map", "what cities did I visit", "vacation recap", "/travel-routes <start> <end>", "/travel-routes --year YYYY".
user-invocable: true
---

# Travel Routes

Extracts geolocation from Apple Photos library (via `osxphotos`), clusters photos by place, and renders an interactive map + markdown summary for a date range or a full year.

Two use cases:

1. **Per-trip mode** — summer vacation blog posts. Self-contained `map.html` with route polyline + place markers + base64-inlined photo thumbnails.
2. **Year-review mode** — list of cities visited per month. Same map output, no thumbnails.

## Prerequisites

- macOS only.
- `osxphotos` installed: `uv tool install osxphotos` or `pipx install osxphotos`.
- Terminal needs **Full Disk Access** in macOS System Settings → Privacy & Security → Full Disk Access. Add the Terminal app (or iTerm / Ghostty / whatever you use).
- Config file at `~/.claude/skills/travel-routes/config.json` (copy `config.example.json`).
- **Privacy**: populate `exclude_zones` in config with home/office coordinates before publishing maps.

## Workflow

### 1. Parse args

```
/travel-routes <start_date> <end_date> [title]    # trip mode (e.g. 2025-07-15 2025-08-05 "Norway")
/travel-routes --year YYYY [title]                 # year-review mode
```

If span > 180 days and no explicit `--year`, force year-review mode.

If args missing, ask user:
- Start date (YYYY-MM-DD)
- End date (YYYY-MM-DD)
- Optional title (used for output folder slug)

### 2. Check prerequisites

```bash
which osxphotos || echo "INSTALL: uv tool install osxphotos"
test -f ~/.claude/skills/travel-routes/config.json || echo "CONFIG MISSING: cp config.example.json config.json"
```

If either missing, surface the install/config command and stop.

### 3. Run pipeline

```bash
cd ~/.claude/skills/travel-routes
uv run travel_routes.py <start> <end> [title]
# or
uv run travel_routes.py --year YYYY [title]
```

The script auto-installs PEP 723 deps (`osxphotos`, `jinja2`, `Pillow`) on first run.

### 4. Report results

Output folder: `~/claude.nosync/travel-routes/<slug>/`

Print:
- Photo count, place count, country count
- Path to `map.html`
- Path to `summary.md`
- Path to `data.json`

Offer: `open <slug>/map.html` to view in browser.

## Output structure

```
~/claude.nosync/travel-routes/<slug>/
├── points.json        # debug: post-exclude raw points
├── clusters.json      # debug: enriched clusters
├── data.json          # canonical dataset (consumed by /blog-post)
├── map.html           # self-contained MapLibre map, base64 thumbs inline
├── summary.md         # trip mode or year mode
└── _thumbs/<uuid>.jpg # debug-only thumbnails
```

## Interactive viewer

After generating per-year data, launch the unified viewer:

```bash
uv run ~/.claude/skills/travel-routes/build_viewer.py    # one-time / after new years
uv run ~/.claude/skills/travel-routes/serve.py           # local HTTP server + opens browser
```

The viewer (`viewer.html`) supports:
- Date range pickers (year/month/day for start + end).
- URL deep-linking: `viewer.html?start=YYYY-MM-DD&end=YYYY-MM-DD`. Default: latest year with data.
- Per-year toggle checkboxes with color legend.
- "Download JSON" — emits filtered dataset as a JSON file.
- Per-year `map.html` files remain for blog-post embedding (with photo thumbnails).

## Reuse with /blog-post

After running this skill, `data.json` contains the canonical trip dataset. To draft a blog post:

```
/blog-post  # then point it at ~/claude.nosync/travel-routes/<slug>/data.json
```

## Troubleshooting

- **`PhotosDB` permission denied** — grant Full Disk Access to Terminal.
- **Empty result** — verify Photos library has photos in the range with location data. Check `points.json`.
- **Blank map in browser** — MapLibre + OpenFreeMap require internet. Offline use not yet supported.
- **Home leaks on map** — populate `exclude_zones` in config and re-run.
