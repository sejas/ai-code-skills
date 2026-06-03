#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "osxphotos>=0.69",
#   "jinja2>=3.1",
#   "Pillow>=10.0",
# ]
# ///
"""Travel-routes entrypoint.

Usage:
  travel_routes.py <start_date> <end_date> [title]
  travel_routes.py --year YYYY [title]

Reads config from ~/.claude/skills/travel-routes/config.json.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import unicodedata
from datetime import datetime
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SKILL_DIR))

from lib import cluster as cluster_mod  # noqa: E402
from lib import enrich, photos, render, thumbs  # noqa: E402


def slugify_title(title: str) -> str:
    norm = unicodedata.normalize("NFKD", title)
    ascii_only = norm.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", ascii_only).strip("-").lower()
    return slug or "trip"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="travel-routes")
    parser.add_argument("--year", type=int, default=None, help="Year-review mode (e.g. 2025).")
    parser.add_argument("start", nargs="?", help="Start date YYYY-MM-DD (omit when using --year).")
    parser.add_argument("end", nargs="?", help="End date YYYY-MM-DD (omit when using --year).")
    parser.add_argument("title", nargs="?", default=None, help="Optional title (used for output slug).")
    return parser.parse_args(argv)


def resolve_mode(args: argparse.Namespace) -> tuple[str, datetime, datetime, str]:
    if args.year is not None:
        start = datetime(args.year, 1, 1)
        end = datetime(args.year, 12, 31, 23, 59, 59)
        title = args.title or f"{args.year} — cities visited"
        return "year", start, end, title
    if not args.start or not args.end:
        raise SystemExit("ERROR: provide <start> <end> or --year YYYY.")
    start = datetime.fromisoformat(args.start)
    end = datetime.fromisoformat(args.end)
    if (end - start).days > 180:
        mode = "year"
        title = args.title or f"{start.date()} → {end.date()} — cities visited"
    else:
        mode = "trip"
        title = args.title or f"{start.date()} → {end.date()}"
    return mode, start, end, title


def load_config() -> dict:
    cfg_path = SKILL_DIR / "config.json"
    if not cfg_path.exists():
        raise SystemExit(
            f"ERROR: missing config at {cfg_path}. "
            f"Copy {SKILL_DIR / 'config.example.json'} and edit exclude_zones."
        )
    return json.loads(cfg_path.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    mode, start, end, title = resolve_mode(args)
    cfg = load_config()

    slug = slugify_title(args.title or title)
    output_dir = Path(os.path.expanduser(cfg["output_dir"])) / slug
    output_dir.mkdir(parents=True, exist_ok=True)
    thumb_dir = output_dir / "_thumbs"

    print(f"[1/6] Loading Apple Photos library...")
    import osxphotos
    db = osxphotos.PhotosDB(dbfile=cfg.get("library_path"))

    print(f"[2/6] Querying {start.date()} → {end.date()}...")
    exclude_zones = cfg.get("exclude_zones", [])
    points = list(photos.query_photos(db, start, end, exclude_zones))
    if not points:
        print("No photos with GPS in range. Aborting.")
        return 1
    (output_dir / "points.json").write_text(json.dumps(points, indent=2, default=str), encoding="utf-8")
    print(f"  → {len(points)} photos after exclude_zones filter.")

    print(f"[3/6] Clustering...")
    cl_cfg = cfg.get("cluster", {})
    clusters = cluster_mod.cluster_points(
        points,
        eps_meters=cl_cfg.get("eps_meters", 200),
        min_dwell_minutes=cl_cfg.get("min_dwell_minutes", 20),
        min_samples=cl_cfg.get("min_samples", 3),
        max_gap_hours=cl_cfg.get("max_gap_hours", 12),
    )
    place_count = sum(1 for c in clusters if c["kind"] == "place")
    print(f"  → {len(clusters)} clusters ({place_count} places, {len(clusters) - place_count} transit).")

    print(f"[4/6] Enriching with PhotoInfo.place...")
    enrich.enrich_clusters(clusters, vault_places_dir=cfg.get("vault_places_dir"))

    include_thumbs = mode == "trip"
    if include_thumbs:
        print(f"[5/6] Rendering thumbnails (trip mode)...")
        per_cluster = cfg.get("thumbnails", {}).get("per_cluster", 6)
        max_width = cfg.get("thumbnails", {}).get("max_width", 400)
        jpeg_quality = cfg.get("thumbnails", {}).get("jpeg_quality", 0.85)
        photo_by_uuid = {p.uuid: p for p in db.photos() if p.uuid in {pt["uuid"] for pt in points}}
        for c in clusters:
            if c["kind"] != "place":
                continue
            rep_uuids = photos.pick_representative_uuids(c, per_cluster)
            c["representative_uuids"] = rep_uuids
            data_uris: list[str] = []
            for uid in rep_uuids:
                ph = photo_by_uuid.get(uid)
                if not ph:
                    continue
                src = photos.resolve_local_path(ph)
                if not src:
                    continue
                result = thumbs.render_thumb(src, uid, thumb_dir, max_width, jpeg_quality)
                if result is None:
                    continue
                data_uris.append(result[1])
            c["representative_thumbs"] = data_uris
    else:
        print(f"[5/6] Skipping thumbnails (year-review mode).")
        for c in clusters:
            if c["kind"] == "place":
                c["representative_uuids"] = []
                c["representative_thumbs"] = []

    clusters_dump = [
        {**c, "photos": [p["uuid"] for p in c["photos"]]}  # collapse photos to uuid list
        for c in clusters
    ]
    (output_dir / "clusters.json").write_text(json.dumps(clusters_dump, indent=2, default=str), encoding="utf-8")

    print(f"[6/6] Rendering map.html + summary.md + data.json...")
    templates_dir = SKILL_DIR / "templates"
    render.render_map_html(
        clusters=clusters,
        title=title,
        templates_dir=templates_dir,
        out_path=output_dir / "map.html",
        include_thumbs=include_thumbs,
    )
    render.render_summary_md(
        clusters=clusters,
        title=title,
        mode=mode,
        templates_dir=templates_dir,
        out_path=output_dir / "summary.md",
    )
    render.write_data_json(
        clusters=clusters,
        out_path=output_dir / "data.json",
        meta={
            "title": title,
            "mode": mode,
            "start": start.isoformat(),
            "end": end.isoformat(),
            "slug": slug,
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "total_photos": len(points),
            "place_count": place_count,
        },
    )

    print()
    print(f"DONE — {len(points)} photos, {place_count} places, mode={mode}")
    print(f"  map:      {output_dir / 'map.html'}")
    print(f"  summary:  {output_dir / 'summary.md'}")
    print(f"  data:     {output_dir / 'data.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
