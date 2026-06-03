# travel-routes

Personal Claude Code skill that extracts geolocation from Apple Photos and produces:

- Interactive HTML map (MapLibre GL JS + OpenFreeMap tiles)
- Markdown summary of cities visited
- JSON dataset for blog-post drafting

macOS only. Single source: Apple Photos via `osxphotos`.

## Install

```bash
# 1. Install osxphotos
uv tool install osxphotos
# or: pipx install osxphotos

# 2. Grant Full Disk Access to Terminal
# System Settings → Privacy & Security → Full Disk Access
# Add the Terminal app you use (Terminal.app, iTerm, Ghostty, etc.)
# Restart the terminal after granting access.

# 3. Copy config
cp ~/.claude/skills/travel-routes/config.example.json \
   ~/.claude/skills/travel-routes/config.json

# 4. Populate exclude_zones in config.json with home/office coords (see below)
```

## Find your home coordinates for exclude_zones

Open Apple Maps, right-click your home → "Copy". Paste into a text editor to extract lat/lon. Or run this once with no exclude_zones populated, look at `points.json`, find the lat/lon cluster with the most photos, that's home.

Set `radius_m` to 500 (500m around the point). Bigger if you want to hide your neighbourhood.

Add multiple zones if needed:

```json
"exclude_zones": [
  {"name": "home", "lat": 28.1234, "lon": -15.5678, "radius_m": 500},
  {"name": "office", "lat": 28.2345, "lon": -15.6789, "radius_m": 300}
]
```

## Usage

```
/travel-routes 2025-07-15 2025-08-05 "Norway road trip"
/travel-routes --year 2025
```

Output appears under `~/claude.nosync/travel-routes/<slug>/`.

## Tests

```bash
cd ~/.claude/skills/travel-routes
uv run --with pytest pytest tests/
```

## How it works

1. Query Apple Photos library via `osxphotos.PhotosDB` for photos in date range with GPS data.
2. Filter out points inside `exclude_zones` (privacy).
3. Walk timeline, cluster consecutive photos that are within `eps_meters` AND `max_gap_hours` of each other.
4. Classify each cluster as "place" (dwell ≥ `min_dwell_minutes`) or "transit" (kept for polyline).
5. Enrich each place cluster with city/country from `PhotoInfo.place` (Apple's on-device reverse-geocode — no Nominatim needed).
6. Pick up to `per_cluster` representative photos (favorites first, then evenly spaced).
7. Export thumbnails via `path_derivatives` (works for iCloud-only photos too).
8. Render MapLibre HTML + summary markdown + data JSON.
