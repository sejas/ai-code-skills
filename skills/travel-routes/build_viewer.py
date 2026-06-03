#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["jinja2>=3.1"]
# ///
"""Build the unified interactive travel-routes viewer.

Scans <output_dir>/<year>-cities-visited/data.json files, writes:
  - manifest.json   (years available, date bounds, color palette, defaults)
  - viewer.html     (single-page MapLibre app with date range + URL params)

Replaces the older `global-map.html` workflow.
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

SKILL_DIR = Path(__file__).resolve().parent
YEAR_DIR_RE = re.compile(r"^(\d{4})-")

# 11-step Tableau / d3 categorical palette.
YEAR_PALETTE = [
    "#4e79a7", "#f28e2b", "#e15759", "#76b7b2", "#59a14f",
    "#edc948", "#b07aa1", "#ff9da7", "#9c755f", "#bab0ac",
    "#2563eb",
]


def load_config() -> dict:
    return json.loads((SKILL_DIR / "config.json").read_text(encoding="utf-8"))


def scan_year(folder: Path) -> dict | None:
    data_path = folder / "data.json"
    if not data_path.exists():
        return None
    data = json.loads(data_path.read_text(encoding="utf-8"))
    meta = data.get("meta", {})
    clusters = data.get("clusters", [])
    place_clusters = [
        c for c in clusters
        if c.get("kind") == "place"
        and c.get("place") and c["place"].get("slug") and c["place"]["slug"] != "unknown"
    ]
    if not place_clusters and not clusters:
        return None
    timestamps = [c["start_ts"] for c in clusters] + [c["end_ts"] for c in clusters]
    timestamps = [t for t in timestamps if t]
    first_ts = min(timestamps)[:10] if timestamps else None
    last_ts = max(timestamps)[:10] if timestamps else None
    return {
        "year": int(meta.get("start", "0001")[:4]) if meta.get("start") else None,
        "folder": folder.name,
        "photos": meta.get("total_photos", sum(c.get("photo_count", 0) for c in clusters)),
        "places": len(place_clusters),
        "first_ts": first_ts,
        "last_ts": last_ts,
        "data_url": f"{folder.name}/data.json",
    }


def main() -> int:
    cfg = load_config()
    output_root = Path(os.path.expanduser(cfg["output_dir"]))
    if not output_root.is_dir():
        print(f"No output dir at {output_root}.")
        return 1

    entries: list[dict] = []
    for child in sorted(output_root.iterdir()):
        if not child.is_dir():
            continue
        m = YEAR_DIR_RE.match(child.name)
        if not m:
            continue
        entry = scan_year(child)
        if entry is None:
            continue
        if entry["year"] is None:
            entry["year"] = int(m.group(1))
        entries.append(entry)

    if not entries:
        print("No year data found.")
        return 1

    entries.sort(key=lambda e: e["year"])
    years_sorted = [e["year"] for e in entries]
    colors = {str(y): YEAR_PALETTE[i % len(YEAR_PALETTE)] for i, y in enumerate(years_sorted)}

    first_dates = [e["first_ts"] for e in entries if e["first_ts"]]
    last_dates = [e["last_ts"] for e in entries if e["last_ts"]]
    earliest_date = min(first_dates) if first_dates else f"{years_sorted[0]}-01-01"
    latest_date = max(last_dates) if last_dates else f"{years_sorted[-1]}-12-31"

    # Default = latest year with ≥1 place. Fall back to plain latest year.
    candidates = [e for e in entries if e["places"] > 0]
    target = max(candidates, key=lambda e: e["year"]) if candidates else entries[-1]
    default_start = f"{target['year']}-01-01"
    default_end = f"{target['year']}-12-31"

    manifest = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "earliest_date": earliest_date,
        "latest_date": latest_date,
        "default_start": default_start,
        "default_end": default_end,
        "years": entries,
        "year_colors": colors,
    }

    (output_root / "manifest.json").write_text(
        json.dumps(manifest, indent=2, default=str), encoding="utf-8"
    )

    env = Environment(
        loader=FileSystemLoader(str(SKILL_DIR / "templates")),
        autoescape=select_autoescape(enabled_extensions=("html", "htm")),
        keep_trailing_newline=True,
    )
    tpl = env.get_template("viewer.html.j2")
    (output_root / "viewer.html").write_text(tpl.render(), encoding="utf-8")

    print(f"DONE — {len(entries)} years.")
    print(f"  manifest: {output_root / 'manifest.json'}")
    print(f"  viewer:   {output_root / 'viewer.html'}")
    print(f"  default range: {default_start} → {default_end}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
