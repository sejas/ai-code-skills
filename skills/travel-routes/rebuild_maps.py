#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["jinja2>=3.1"]
# ///
"""Regenerate per-year map.html files from existing data.json.

Skips the slow Photos query — reuses cached clusters/data from a previous run.
Use after editing templates/map.html.j2 or lib/render.py rendering logic.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SKILL_DIR))

from lib import render  # noqa: E402


YEAR_DIR_RE = re.compile(r"^(\d{4})-")


def load_config() -> dict:
    return json.loads((SKILL_DIR / "config.json").read_text(encoding="utf-8"))


def rebuild_one(folder: Path, templates_dir: Path) -> tuple[int, int] | None:
    """Rebuild map.html in `folder` using its data.json. Returns (markers, photos)."""
    data_path = folder / "data.json"
    if not data_path.exists():
        return None
    data = json.loads(data_path.read_text(encoding="utf-8"))
    meta = data.get("meta", {})
    mode = meta.get("mode", "year")
    title = meta.get("title", folder.name)

    # data.json stores photo_uuids only (no full photo records). Reconstruct minimal
    # cluster shape from photo_uuids — we have centroid/start_ts/end_ts already.
    # For polyline we need per-photo lat/lon, which we DON'T have in data.json.
    # Fall back: polyline uses cluster centroids in chronological order.
    clusters = []
    for c in data.get("clusters", []):
        n = len(c.get("photo_uuids", []))
        # Synthesize a single "photo" at the centroid carrying the cluster's start_ts
        # so the polyline traces centroid → centroid in chrono order.
        synth_photo = {"ts": c["start_ts"], "lat": c["centroid"][0], "lon": c["centroid"][1]}
        clusters.append({
            "id": c["id"],
            "kind": c["kind"],
            "centroid": c["centroid"],
            "start_ts": c["start_ts"],
            "end_ts": c["end_ts"],
            "photo_count": c["photo_count"],
            "dwell_minutes": c.get("dwell_minutes", 0),
            "place": c.get("place"),
            "photos": [synth_photo] * max(1, n),  # polyline only reads .ts/.lat/.lon
            "representative_thumbs": [],  # thumbs not re-rendered (skipped in year mode anyway)
        })

    include_thumbs = mode == "trip"
    render.render_map_html(
        clusters=clusters,
        title=title,
        templates_dir=templates_dir,
        out_path=folder / "map.html",
        include_thumbs=include_thumbs,
    )
    place_count = sum(1 for c in clusters if c["kind"] == "place")
    return place_count, sum(c["photo_count"] for c in clusters)


def main() -> int:
    cfg = load_config()
    output_root = Path(os.path.expanduser(cfg["output_dir"]))
    templates_dir = SKILL_DIR / "templates"
    if not output_root.is_dir():
        print(f"No output dir at {output_root}.")
        return 1
    count = 0
    for child in sorted(output_root.iterdir()):
        if not child.is_dir() or not YEAR_DIR_RE.match(child.name):
            continue
        result = rebuild_one(child, templates_dir)
        if result is None:
            continue
        places, photos = result
        print(f"  {child.name}: {photos:,} photos, {places} places → map.html")
        count += 1
    print(f"DONE — rebuilt {count} maps.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
