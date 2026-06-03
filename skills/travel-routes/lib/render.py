"""Render map.html (MapLibre + OpenFreeMap), summary.md (trip/year), data.json."""

from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape


def _env(templates_dir: Path) -> Environment:
    return Environment(
        loader=FileSystemLoader(str(templates_dir)),
        autoescape=select_autoescape(enabled_extensions=("html", "htm")),
        keep_trailing_newline=True,
    )


def render_map_html(
    clusters: list[dict],
    title: str,
    templates_dir: Path,
    out_path: Path,
    include_thumbs: bool,
) -> None:
    """Render the MapLibre HTML map.

    `clusters` already enriched (place clusters have .place + .representative_thumbs);
    transit clusters retain raw photo points for the polyline.
    """
    env = _env(templates_dir)
    template = env.get_template("map.html.j2")

    # Build polyline coordinates from all photos in chronological order.
    all_photos = []
    for c in clusters:
        all_photos.extend(c["photos"])
    all_photos.sort(key=lambda p: p["ts"])
    line_coords = [[p["lon"], p["lat"]] for p in all_photos]

    markers = []
    cities: set[str] = set()
    countries: set[str] = set()
    place_count = 0
    for c in clusters:
        if c["kind"] != "place":
            continue
        place = c.get("place", {})
        thumbs = c.get("representative_thumbs", []) if include_thumbs else []
        slug = place.get("slug")
        if slug and slug != "unknown":
            cities.add(slug)
        if place.get("country"):
            countries.add(place["country"])
        place_count += 1
        markers.append({
            "lat": c["centroid"][0],
            "lon": c["centroid"][1],
            "city": place.get("city") or "unknown",
            "country": place.get("country") or "",
            "start_ts": c["start_ts"][:10],
            "end_ts": c["end_ts"][:10],
            "photo_count": c["photo_count"],
            "dwell_minutes": int(c["dwell_minutes"]),
            "thumbs": thumbs,
        })
    total_photos = sum(c["photo_count"] for c in clusters)

    # Fit-bounds: compute SW/NE corners.
    if line_coords:
        lats = [c[1] for c in line_coords]
        lons = [c[0] for c in line_coords]
        bbox = [min(lons), min(lats), max(lons), max(lats)]
    else:
        bbox = [-180, -90, 180, 90]

    out_path.write_text(
        template.render(
            title=title,
            line_coords_json=json.dumps(line_coords),
            markers_json=json.dumps(markers),
            bbox_json=json.dumps(bbox),
            total_photos=total_photos,
            place_count=place_count,
            city_count=len(cities),
            country_count=len(countries),
        ),
        encoding="utf-8",
    )


def _fmt_date(ts: str) -> str:
    return ts[:10]


def render_summary_md(
    clusters: list[dict],
    title: str,
    mode: str,                  # 'trip' | 'year'
    templates_dir: Path,
    out_path: Path,
    map_filename: str = "map.html",
) -> None:
    """Render summary.md from a Jinja template (trip or year mode)."""
    env = _env(templates_dir)
    template_name = "summary_trip.md.j2" if mode == "trip" else "summary_year.md.j2"
    template = env.get_template(template_name)

    place_clusters = [c for c in clusters if c["kind"] == "place"]
    place_clusters.sort(key=lambda c: c["start_ts"])

    total_photos = sum(c["photo_count"] for c in clusters)
    countries = sorted({c["place"].get("country") for c in place_clusters if c["place"].get("country")})
    cities_seen: list[dict] = []
    seen_slugs = set()
    for c in place_clusters:
        slug = c["place"]["slug"]
        if slug in seen_slugs:
            continue
        seen_slugs.add(slug)
        cities_seen.append({
            "slug": slug,
            "display": c["place"]["city"],
            "country": c["place"].get("country") or "",
        })

    itinerary = []
    by_month: dict[str, list[dict]] = defaultdict(list)
    for c in place_clusters:
        entry = {
            "start_date": _fmt_date(c["start_ts"]),
            "end_date": _fmt_date(c["end_ts"]),
            "city": c["place"]["city"],
            "slug": c["place"]["slug"],
            "country": c["place"].get("country") or "",
            "photo_count": c["photo_count"],
            "dwell_minutes": int(c["dwell_minutes"]),
        }
        itinerary.append(entry)
        month_key = c["start_ts"][:7]  # YYYY-MM
        by_month[month_key].append(entry)

    months_sorted = []
    for month_key in sorted(by_month.keys()):
        dt = datetime.strptime(month_key, "%Y-%m")
        months_sorted.append({
            "label": dt.strftime("%B %Y"),
            "entries": by_month[month_key],
        })

    out_path.write_text(
        template.render(
            title=title,
            total_photos=total_photos,
            place_count=len(place_clusters),
            countries=countries,
            cities=cities_seen,
            itinerary=itinerary,
            months=months_sorted,
            map_filename=map_filename,
        ),
        encoding="utf-8",
    )


def write_data_json(clusters: list[dict], out_path: Path, meta: dict) -> None:
    """Canonical dataset for /blog-post reuse."""
    payload = {
        "meta": meta,
        "clusters": [
            {
                "id": c["id"],
                "kind": c["kind"],
                "centroid": list(c["centroid"]),
                "start_ts": c["start_ts"],
                "end_ts": c["end_ts"],
                "photo_count": c["photo_count"],
                "dwell_minutes": c["dwell_minutes"],
                "place": c.get("place"),
                "representative_uuids": c.get("representative_uuids", []),
                "photo_uuids": [p["uuid"] for p in c["photos"]],
            }
            for c in clusters
        ],
    }
    out_path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
