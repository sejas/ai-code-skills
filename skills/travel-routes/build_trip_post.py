#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["jinja2>=3.1", "PyYAML>=6"]
# ///
"""Trip blog post builder + retrofitter.

Two modes:

  build_trip_post.py --retrofit <existing-post.md> [--trip-json /tmp/blog-<slug>.json]
      Restructure an existing trip-narrative post into the
      story-first-with-practical-sidebar format. Existing narrative is preserved
      verbatim under '### The story'. The trailing reflective section (matching
      keywords like 'Looking back', 'Takeaway', 'What I am taking home') is
      moved into '### Looking back' at the end. New scaffold sections (TL;DR,
      At a glance, Highlights, If you go, Photos & route) are inserted with
      auto-derivable content + TODO placeholders for you to fill in.

  build_trip_post.py --new --start YYYY-MM-DD --end YYYY-MM-DD --country <name>
                     --slug <kebab-slug> --title "..." [--out <path>]
      Render a fresh skeleton post from the matching per-year data.json, using
      templates/post-trip.md.j2. Output defaults to
      $TRAVEL_POSTS_DIR (or ~/Documents/notes/posts)/<YYYY-MM>-<slug>.md.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import date as Date
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader

SKILL_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SKILL_DIR))

from lib.geo import haversine_m  # noqa: E402

CLOSING_HEADING_RE = re.compile(
    r"^###\s+.*\b(looking back|takeaway|the takeaway|taking home|what i am taking home|reflection)\b",
    re.IGNORECASE,
)
MAP_LINK_RE = re.compile(r"^\[Open the interactive map\]\(.+?\)\s*$")
FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def load_config() -> dict:
    return json.loads((SKILL_DIR / "config.json").read_text(encoding="utf-8"))


def parse_post(text: str) -> tuple[dict, str]:
    """Return (frontmatter_dict, body_str)."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        raise SystemExit("ERROR: post has no YAML frontmatter")
    fm = yaml.safe_load(m.group(1)) or {}
    body = text[m.end():]
    return fm, body


def dump_frontmatter(fm: dict) -> str:
    out_lines = ["---"]
    # Preserve a deterministic key order, putting required-by-CLAUDE.md fields first.
    preferred = [
        "type", "slug", "title", "date",
        "trip_start", "trip_end", "country", "days",
        "languages", "status", "tags",
    ]
    keys = [k for k in preferred if k in fm] + [k for k in fm if k not in preferred]
    for k in keys:
        v = fm[k]
        if isinstance(v, list):
            inner = ", ".join(str(x) for x in v)
            out_lines.append(f"{k}: [{inner}]")
        elif isinstance(v, str) and (":" in v or v.startswith(("[", "{", "-", "!", "&", "*", "|", ">", "%", "@", "`"))):
            esc = v.replace('"', '\\"')
            out_lines.append(f'{k}: "{esc}"')
        else:
            out_lines.append(f"{k}: {v}")
    out_lines.append("---")
    out_lines.append("")
    return "\n".join(out_lines)


def find_trip_json(slug: str) -> Path | None:
    candidate = Path(f"/tmp/blog-{slug}.json")
    return candidate if candidate.exists() else None


def regenerate_trip_json(slug: str, country: str, start: str, end: str, output_dir: Path) -> Path:
    """Build /tmp/blog-<slug>.json from per-year data.json files matching country + range."""
    aliases = {"Czech Republic": {"Czech Republic", "Czechia"}}
    targets = aliases.get(country, {country})
    year = int(start[:4])
    end_year = int(end[:4])
    clusters = []
    for y in range(year, end_year + 1):
        p = output_dir / f"{y}-cities-visited" / "data.json"
        if not p.exists():
            continue
        d = json.loads(p.read_text(encoding="utf-8"))
        for c in d.get("clusters", []):
            if c.get("kind") != "place":
                continue
            place = c.get("place") or {}
            if place.get("country") not in targets:
                continue
            ts_start = c["start_ts"][:10]
            ts_end = c["end_ts"][:10]
            if ts_end < start or ts_start > end:
                continue
            clusters.append({
                "start_ts": ts_start,
                "end_ts": ts_end,
                "photo_count": c["photo_count"],
                "place": place,
                "centroid": c["centroid"],
                "dwell_minutes": c.get("dwell_minutes", 0),
            })
    clusters.sort(key=lambda x: x["start_ts"])
    if not clusters:
        raise SystemExit(f"ERROR: no clusters found for {country} {start}→{end}")
    out_path = Path(f"/tmp/blog-{slug}.json")
    out_path.write_text(json.dumps({
        "country": country,
        "slug": slug,
        "start": clusters[0]["start_ts"],
        "end": clusters[-1]["end_ts"],
        "cluster_count": len(clusters),
        "total_photos": sum(c["photo_count"] for c in clusters),
        "clusters": clusters,
    }, indent=2), encoding="utf-8")
    return out_path


def trip_stats(trip: dict) -> dict:
    """Compute auto-derivable stats: distance, cities, itinerary, highlights, TL;DR seeds."""
    clusters = trip["clusters"]
    start = trip["start"]
    end = trip["end"]
    days = (Date.fromisoformat(end) - Date.fromisoformat(start)).days + 1

    # Distance: sum of Haversine between consecutive centroids.
    distance_m = 0.0
    for a, b in zip(clusters, clusters[1:]):
        distance_m += haversine_m(a["centroid"][0], a["centroid"][1],
                                  b["centroid"][0], b["centroid"][1])
    distance_km = round(distance_m / 1000)

    # Unique cities preserving first-appearance order.
    seen = set()
    cities = []
    for c in clusters:
        slug = c["place"]["slug"]
        if slug == "unknown" or slug in seen:
            continue
        seen.add(slug)
        cities.append({
            "slug": slug,
            "city": c["place"].get("city") or "unknown",
            "poi": c["place"].get("poi"),
        })

    # Itinerary: group consecutive clusters by date-range, label as Day X.
    # Simple version: one row per unique city visit (first occurrence per date).
    itinerary = []
    prev = None
    for c in clusters:
        if c["place"]["slug"] == "unknown":
            continue
        label_day = (Date.fromisoformat(c["start_ts"]) - Date.fromisoformat(start)).days + 1
        if prev and prev["slug"] == c["place"]["slug"] and prev["day"] == label_day:
            continue
        entry = {
            "day": label_day,
            "label": f"Day {label_day} ({c['start_ts']})",
            "slug": c["place"]["slug"],
            "city": c["place"].get("city"),
            "poi": c["place"].get("poi"),
        }
        itinerary.append(entry)
        prev = entry

    # Highlights: top 3 cities by total dwell minutes (sum across clusters).
    dwell_by_slug: dict[str, float] = {}
    poi_by_slug: dict[str, str] = {}
    city_by_slug: dict[str, str] = {}
    for c in clusters:
        s = c["place"]["slug"]
        if s == "unknown":
            continue
        dwell_by_slug[s] = dwell_by_slug.get(s, 0) + c.get("dwell_minutes", 0)
        if c["place"].get("poi") and s not in poi_by_slug:
            poi_by_slug[s] = c["place"]["poi"]
        if c["place"].get("city"):
            city_by_slug[s] = c["place"]["city"]
    top = sorted(dwell_by_slug.items(), key=lambda kv: kv[1], reverse=True)[:3]
    highlights = [
        {"slug": s, "city": city_by_slug.get(s, s), "poi": poi_by_slug.get(s)}
        for s, _ in top
    ]

    # TL;DR seeds: 3 of the top highlights.
    tldr_seed = []
    for h in highlights:
        bullet = f"Plan time at [[{h['slug']}|{h['city']}]]"
        if h["poi"]:
            bullet += f" — don't skip {h['poi']}."
        else:
            bullet += "."
        tldr_seed.append(bullet)

    cities_inline = ", ".join(f"[[{c['slug']}|{c['city']}]]" for c in cities)

    return {
        "days": days,
        "distance_km": distance_km,
        "cities": cities,
        "city_count": len(cities),
        "cities_inline": cities_inline,
        "itinerary": itinerary,
        "highlights": highlights,
        "tldr_seed": tldr_seed,
    }


# ---------------------------- New mode ----------------------------

def render_new(trip: dict, title: str, country: str, slug: str, output_path: Path,
               map_html_rel: str) -> None:
    stats = trip_stats(trip)
    env = Environment(
        loader=FileSystemLoader(str(SKILL_DIR / "templates")),
        keep_trailing_newline=True,
    )
    tpl = env.get_template("post-trip.md.j2")
    rendered = tpl.render(
        slug=slug,
        title=title,
        country=country,
        trip_start=trip["start"],
        trip_end=trip["end"],
        days=stats["days"],
        distance_km=stats["distance_km"],
        total_photos=trip["total_photos"],
        city_count=stats["city_count"],
        cities_inline=stats["cities_inline"],
        itinerary=stats["itinerary"],
        highlights=stats["highlights"],
        tldr_seed=stats["tldr_seed"],
        map_html_rel=map_html_rel,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(rendered, encoding="utf-8")


# ---------------------------- Retrofit mode ----------------------------

def split_body(body: str) -> dict:
    """Locate `## English`, the footer map link, and (optionally) the closing reflective section.

    Returns:
      english_idx: index of the '## English' line, or -1 if missing
      footer_line: the map-link footer line (str) or None
      pre_footer: list of body lines up to (but not including) the footer
      closing_heading_idx: index in `pre_footer` of the closing `###` heading, or -1
    """
    lines = body.splitlines()
    english_idx = -1
    for i, line in enumerate(lines):
        if line.strip() == "## English":
            english_idx = i
            break

    footer_idx = -1
    for i in range(len(lines) - 1, -1, -1):
        if MAP_LINK_RE.match(lines[i]):
            footer_idx = i
            break
    footer_line = lines[footer_idx] if footer_idx != -1 else None
    pre_footer = lines[:footer_idx] if footer_idx != -1 else lines

    closing_idx = -1
    for i in range(len(pre_footer) - 1, english_idx if english_idx >= 0 else -1, -1):
        if CLOSING_HEADING_RE.match(pre_footer[i] or ""):
            closing_idx = i
            break

    return {
        "english_idx": english_idx,
        "footer_line": footer_line,
        "pre_footer": pre_footer,
        "closing_idx": closing_idx,
    }


def render_retrofit(post_path: Path, output_dir: Path) -> dict:
    text = post_path.read_text(encoding="utf-8")
    fm, body = parse_post(text)

    slug = fm.get("slug")
    if not slug:
        raise SystemExit(f"ERROR: {post_path} has no `slug` in frontmatter")

    trip_json = find_trip_json(slug)
    if trip_json is None:
        country = fm.get("country") or slug.replace("-", " ").title()
        # date might be the trip end
        start = fm.get("trip_start") or _infer_start(fm)
        end = fm.get("trip_end") or fm.get("date")
        trip_json = regenerate_trip_json(slug, country, start, end, output_dir)
    trip = json.loads(trip_json.read_text(encoding="utf-8"))
    stats = trip_stats(trip)

    # Augment frontmatter with new optional fields if absent.
    fm.setdefault("trip_start", trip["start"])
    fm.setdefault("trip_end", trip["end"])
    fm.setdefault("country", trip["country"])
    fm.setdefault("days", stats["days"])
    fm.setdefault("languages", ["en"])
    fm.setdefault("status", "draft")
    tags = fm.get("tags") or []
    if isinstance(tags, list):
        if "post" not in tags:
            tags = ["post"] + tags
        if "trip" not in tags:
            tags.append("trip")
        if slug not in tags:
            tags.append(slug)
        fm["tags"] = tags

    split = split_body(body)
    if split["english_idx"] == -1:
        raise SystemExit(f"ERROR: {post_path} has no '## English' heading")

    english_idx = split["english_idx"]
    pre_footer = split["pre_footer"]
    closing_idx = split["closing_idx"]

    # Existing intro: lines between `## English` and first sub-heading (or closing if no sub).
    # Existing narrative: from `## English` (exclusive) to the closing heading (exclusive) or end.
    # Closing content: from closing heading (inclusive) to end of pre_footer.
    if closing_idx != -1:
        story_lines = pre_footer[english_idx + 1:closing_idx]
        closing_lines = pre_footer[closing_idx:]  # includes the `### Looking back / Takeaway` heading
    else:
        story_lines = pre_footer[english_idx + 1:]
        closing_lines = []

    story_body = "\n".join(story_lines).strip("\n")

    # Build scaffold sections.
    deep_link = f"~/claude.nosync/travel-routes/viewer.html?start={trip['start']}&end={trip['end']}"
    map_html_rel = f"~/claude.nosync/travel-routes/{trip['start'][:4]}-cities-visited/map.html"

    tldr_lines = ["### TL;DR — 5 things to steal", ""]
    for bullet in stats["tldr_seed"]:
        tldr_lines.append(f"- {bullet}")
    tldr_lines.append("- TODO — your favourite meal, dish, or food memory")
    tldr_lines.append("- TODO — best wildlife / nature / cultural moment")

    at_glance_lines = [
        "",
        "### At a glance",
        "",
        "| | |",
        "|---|---|",
        f"| **Dates** | {trip['start']} → {trip['end']} ({stats['days']} days) |",
        f"| **Country** | {trip['country']} |",
        f"| **Cities** | {stats['city_count']} — " + ", ".join(
            f"[[{c['slug']}\\|{c['city']}]]" for c in stats["cities"]
        ) + " |",
        f"| **Distance** | ~{stats['distance_km']:,} km |",
        f"| **Photos** | {trip['total_photos']:,} |",
        "| **Best for** | TODO — road-trippers? families? slow travel? nature? |",
        "",
        f"[Open the interactive map]({deep_link})",
    ]

    highlights_lines = ["", "### Highlights — what you shouldn't miss", ""]
    for h in stats["highlights"]:
        title_part = f"[[{h['slug']}|{h['city']}]]"
        if h["poi"]:
            title_part += f" — {h['poi']}"
        highlights_lines.append(f"#### {title_part}")
        highlights_lines.append("")
        highlights_lines.append("- **What it is**: TODO — one sentence.")
        highlights_lines.append("- **Why it stuck**: TODO — one sentence.")
        highlights_lines.append("- **How to repeat**:")
        highlights_lines.append("  - TODO — timing / best time of day")
        highlights_lines.append("  - TODO — booking / operator / how to access")
        highlights_lines.append("  - TODO — what to bring or wear")
        highlights_lines.append("")

    if_you_go_lines = [
        "### If you go",
        "",
        "> [!tip] Best time to visit",
        "> TODO — month / season, weather notes, festivals or special events.",
        "",
        "> [!note] Getting around",
        "> TODO — rental car? trains? domestic flights? walking? Be specific.",
        "",
        "> [!warning] What we'd do differently",
        "> TODO — one or two honest regrets, what you'd skip or extend.",
        "",
        "#### Logistics",
        "",
        "- **Fly into**: TODO — airport code + name",
        "- **Get around**: TODO — transport mode + cost ballpark",
        "- **Sleep**: TODO — 2–3 recommended bases with neighbourhood vibe",
        "- **Eat**: TODO — 3 dishes to try, 1–2 specific places worth a detour",
        "- **Budget**: TODO — daily rate estimate (€X/day) and what drove it",
        "- **Pack**: TODO — one idiosyncratic packing tip nobody else mentions",
        "",
        "#### Sample itinerary (copy & adapt)",
        "",
    ]
    for entry in stats["itinerary"]:
        line = f"- **{entry['label']}** — [[{entry['slug']}|{entry['city']}]]"
        if entry["poi"]:
            line += f" · {entry['poi']}"
        if_you_go_lines.append(line)
    if_you_go_lines.append("")

    photos_lines = [
        "### Photos & route",
        "",
        f"[Photos and full interactive route map]({map_html_rel})",
        "",
    ]

    if closing_lines:
        # Normalise: replace the existing closing heading line with our canonical one.
        closing_body = closing_lines[1:] if closing_lines else []
        closing_body_text = "\n".join(closing_body).strip("\n")
        looking_back_lines = [
            "### Looking back",
            "",
            closing_body_text,
            "",
        ]
    else:
        looking_back_lines = [
            "### Looking back",
            "",
            "_TODO — 100–200 words. The takeaway. Why you'd go back, or what you've already moved on from._",
            "",
        ]

    pull_quote = "> _Pull quote — TODO: one line that captures the whole trip._"

    parts = [
        dump_frontmatter(fm),
        "## English",
        "",
        pull_quote,
        "",
        *tldr_lines,
        *at_glance_lines,
        "",
        "### The story",
        "",
        story_body,
        "",
        *highlights_lines,
        *if_you_go_lines,
        *photos_lines,
        *looking_back_lines,
        f"[Open the interactive map]({deep_link})",
        "",
    ]
    new_text = "\n".join(parts)
    post_path.write_text(new_text, encoding="utf-8")
    return {
        "post": str(post_path),
        "trip_json": str(trip_json),
        "days": stats["days"],
        "distance_km": stats["distance_km"],
        "cities": stats["city_count"],
        "highlights": [h["slug"] for h in stats["highlights"]],
        "closing_extracted": bool(closing_lines),
    }


def _infer_start(fm: dict) -> str:
    """Fallback: derive trip start from frontmatter — use `date` minus 7 days if no trip_start."""
    if fm.get("date"):
        d = Date.fromisoformat(str(fm["date"]))
        return str(Date.fromordinal(d.toordinal() - 7))
    raise SystemExit("ERROR: cannot infer trip_start")


# ---------------------------- CLI ----------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="build_trip_post")
    sub = parser.add_subparsers(dest="mode", required=True)

    pr = sub.add_parser("retrofit", help="Restructure existing post into story-first format.")
    pr.add_argument("post", help="Path to existing post markdown file.")

    pn = sub.add_parser("new", help="Generate a fresh skeleton post from data.json.")
    pn.add_argument("--start", required=True)
    pn.add_argument("--end", required=True)
    pn.add_argument("--country", required=True)
    pn.add_argument("--slug", required=True)
    pn.add_argument("--title", required=True)
    pn.add_argument("--out", default=None)

    args = parser.parse_args(argv or sys.argv[1:])
    cfg = load_config()
    output_dir = Path(os.path.expanduser(cfg["output_dir"]))

    if args.mode == "retrofit":
        post = Path(args.post)
        if not post.exists():
            raise SystemExit(f"not found: {post}")
        result = render_retrofit(post, output_dir)
        print(json.dumps(result, indent=2))
        return 0

    if args.mode == "new":
        slug = args.slug
        trip_json = find_trip_json(slug) or regenerate_trip_json(
            slug, args.country, args.start, args.end, output_dir
        )
        trip = json.loads(trip_json.read_text(encoding="utf-8"))
        if args.out:
            out_path = Path(os.path.expanduser(args.out))
        else:
            posts_dir = Path(os.path.expanduser(
                os.environ.get("TRAVEL_POSTS_DIR", "~/Documents/notes/posts")
            ))
            out_path = posts_dir / f"{trip['end'][:7]}-{slug}.md"
        map_html_rel = f"~/claude.nosync/travel-routes/{trip['start'][:4]}-cities-visited/map.html"
        render_new(trip, args.title, args.country, slug, out_path, map_html_rel)
        print(json.dumps({"post": str(out_path), "slug": slug, "days": (Date.fromisoformat(trip['end']) - Date.fromisoformat(trip['start'])).days + 1}, indent=2))
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
