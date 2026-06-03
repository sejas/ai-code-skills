#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["jinja2>=3.1"]
# ///
"""Build a master index linking all per-year travel-routes outputs.

Scans <output_dir>/*-cities-visited/ for data.json, renders:
  - index.html (grid of year cards + global cities/countries list)
  - index.md   (markdown table + cities aggregated)
"""

from __future__ import annotations

import json
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

SKILL_DIR = Path(__file__).resolve().parent


def load_config() -> dict:
    cfg_path = SKILL_DIR / "config.json"
    return json.loads(cfg_path.read_text(encoding="utf-8"))


YEAR_DIR_RE = re.compile(r"^(\d{4})-")


def scan_outputs(root: Path) -> list[dict]:
    entries: list[dict] = []
    if not root.is_dir():
        return entries
    for child in sorted(root.iterdir()):
        if not child.is_dir():
            continue
        m = YEAR_DIR_RE.match(child.name)
        if not m:
            continue
        data_path = child / "data.json"
        if not data_path.exists():
            continue
        data = json.loads(data_path.read_text(encoding="utf-8"))
        meta = data.get("meta", {})
        clusters = data.get("clusters", [])
        places = [c for c in clusters if c.get("place") and c["place"].get("slug") != "unknown" and c.get("kind") == "place"]
        countries = sorted({c["place"].get("country") for c in places if c["place"].get("country")})
        cities = []
        seen = set()
        for c in places:
            slug = c["place"]["slug"]
            if slug in seen:
                continue
            seen.add(slug)
            cities.append({
                "slug": slug,
                "display": c["place"].get("city") or "unknown",
                "country": c["place"].get("country") or "",
                "country_code": c["place"].get("country_code") or "",
            })
        entries.append({
            "year": int(m.group(1)),
            "folder": child.name,
            "title": meta.get("title", child.name),
            "photo_count": meta.get("total_photos", sum(c["photo_count"] for c in clusters)),
            "place_count": meta.get("place_count", len(places)),
            "country_count": len(countries),
            "countries": countries,
            "cities": cities,
            "map_href": f"{child.name}/map.html",
            "summary_href": f"{child.name}/summary.md",
            "data_href": f"{child.name}/data.json",
        })
    entries.sort(key=lambda e: e["year"], reverse=True)
    return entries


INDEX_HTML_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Travel routes — index</title>
  <style>
    :root {
      --bg: #f7f7f9; --fg: #111; --muted: #555; --card: #fff;
      --accent: #2563eb; --border: #e3e3e7;
    }
    @media (prefers-color-scheme: dark) {
      :root { --bg: #0f1115; --fg: #f4f4f7; --muted: #9aa0a8; --card: #181b22; --border: #2a2d36; }
    }
    * { box-sizing: border-box; }
    html, body { margin: 0; padding: 0; background: var(--bg); color: var(--fg); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
    .wrap { max-width: 1100px; margin: 0 auto; padding: 32px 20px 64px; }
    h1 { font-size: 28px; margin: 0 0 6px; }
    .lede { color: var(--muted); margin: 0 0 28px; font-size: 15px; }
    .totals { display: flex; gap: 18px; flex-wrap: wrap; margin: 0 0 32px; padding: 14px 18px; background: var(--card); border: 1px solid var(--border); border-radius: 10px; font-size: 14px; }
    .totals b { color: var(--accent); font-size: 18px; display: block; }
    .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 14px; }
    .card { background: var(--card); border: 1px solid var(--border); border-radius: 10px; padding: 16px; transition: transform .08s ease, box-shadow .08s ease; }
    .card:hover { transform: translateY(-2px); box-shadow: 0 6px 16px rgba(0,0,0,0.08); }
    .year { font-size: 24px; font-weight: 700; margin: 0 0 6px; }
    .stats { color: var(--muted); font-size: 13px; margin: 0 0 10px; line-height: 1.4; }
    .stats b { color: var(--fg); }
    .flags { font-size: 13px; color: var(--muted); margin: 0 0 12px; min-height: 18px; }
    .actions { display: flex; gap: 6px; flex-wrap: wrap; }
    .btn { display: inline-block; padding: 5px 10px; border-radius: 6px; font-size: 12px; text-decoration: none; border: 1px solid var(--border); color: var(--fg); }
    .btn-primary { background: var(--accent); color: #fff; border-color: var(--accent); }
    .btn:hover { opacity: 0.85; }
    .section { margin-top: 36px; }
    .section h2 { font-size: 18px; margin: 0 0 10px; }
    .country-list, .city-list { display: flex; gap: 8px; flex-wrap: wrap; font-size: 13px; }
    .pill { background: var(--card); border: 1px solid var(--border); padding: 4px 10px; border-radius: 999px; }
    footer { margin-top: 48px; color: var(--muted); font-size: 12px; text-align: center; }
  </style>
</head>
<body>
  <div class="wrap">
    <h1>Travel routes — index</h1>
    <p class="lede">Per-year maps generated from Apple Photos geolocation. Click a year to open its interactive map.</p>

    <p style="margin: 0 0 24px;"><a href="viewer.html" style="display: inline-block; padding: 10px 18px; background: var(--accent); color: #fff; border-radius: 8px; text-decoration: none; font-size: 14px; font-weight: 500;">🌍 Open interactive viewer (filter by date) →</a></p>
    <p style="margin: -16px 0 24px; font-size: 12px; color: var(--muted);">Requires <code>uv run ~/.claude/skills/travel-routes/serve.py</code> running.</p>

    <div class="totals">
      <div><b>{{ total_years }}</b>years</div>
      <div><b>{{ total_photos }}</b>photos</div>
      <div><b>{{ total_places }}</b>places</div>
      <div><b>{{ total_countries }}</b>unique countries</div>
      <div><b>{{ total_cities }}</b>unique cities</div>
    </div>

    <div class="grid">
      {% for e in entries %}
      <div class="card">
        <div class="year">{{ e.year }}</div>
        <div class="stats">
          <b>{{ "{:,}".format(e.photo_count) }}</b> photos<br/>
          <b>{{ e.place_count }}</b> places · <b>{{ e.country_count }}</b> countries
        </div>
        <div class="flags">{{ e.countries | join(", ") }}</div>
        <div class="actions">
          <a class="btn btn-primary" href="{{ e.map_href }}">Map</a>
          <a class="btn" href="{{ e.summary_href }}">Summary</a>
          <a class="btn" href="{{ e.data_href }}">JSON</a>
        </div>
      </div>
      {% endfor %}
    </div>

    <div class="section">
      <h2>All countries ({{ total_countries }})</h2>
      <div class="country-list">
        {% for country in all_countries %}<span class="pill">{{ country }}</span>{% endfor %}
      </div>
    </div>

    <div class="section">
      <h2>All cities ({{ total_cities }})</h2>
      <div class="city-list">
        {% for c in all_cities %}<span class="pill">{{ c.display }}{% if c.country %} <span style="opacity:.6">· {{ c.country }}</span>{% endif %}</span>{% endfor %}
      </div>
    </div>

    <footer>Generated by <code>/travel-routes</code> · {{ generated_at }}</footer>
  </div>
</body>
</html>
"""


INDEX_MD_TEMPLATE = """# Travel routes — index

Per-year maps generated from Apple Photos geolocation.

**Total**: {{ total_years }} years · {{ "{:,}".format(total_photos) }} photos · {{ total_places }} places · {{ total_countries }} countries · {{ total_cities }} cities

[🌍 Open interactive viewer (filter by date)](viewer.html) — requires `uv run ~/.claude/skills/travel-routes/serve.py`

## Years

| Year | Photos | Places | Countries | Map |
|---|---:|---:|---:|---|
{% for e in entries -%}
| {{ e.year }} | {{ "{:,}".format(e.photo_count) }} | {{ e.place_count }} | {{ e.country_count }} | [{{ e.folder }}/map.html]({{ e.map_href }}) · [summary]({{ e.summary_href }}) |
{% endfor %}

## Countries visited

{% for country in all_countries -%}
- {{ country }}
{% endfor %}

## All cities

{% for c in all_cities -%}
- [[{{ c.slug }}|{{ c.display }}]]{% if c.country %} ({{ c.country }}){% endif %}
{% endfor %}
"""


def main() -> int:
    cfg = load_config()
    output_root = Path(os.path.expanduser(cfg["output_dir"]))
    entries = scan_outputs(output_root)
    if not entries:
        print(f"No year folders found under {output_root}.")
        return 1

    total_photos = sum(e["photo_count"] for e in entries)
    total_places = sum(e["place_count"] for e in entries)

    country_counter: Counter = Counter()
    city_dedup: dict[str, dict] = {}
    for e in entries:
        for country in e["countries"]:
            country_counter[country] += 1
        for c in e["cities"]:
            slug = c["slug"]
            if slug not in city_dedup:
                city_dedup[slug] = c
    all_countries = sorted(country_counter.keys())
    all_cities = sorted(city_dedup.values(), key=lambda c: c["display"].lower())

    from datetime import datetime
    generated_at = datetime.now().isoformat(timespec="seconds")

    env = Environment(autoescape=select_autoescape(enabled_extensions=("html",)))
    html_tpl = env.from_string(INDEX_HTML_TEMPLATE)
    md_tpl = env.from_string(INDEX_MD_TEMPLATE)

    ctx = {
        "entries": entries,
        "total_years": len(entries),
        "total_photos": total_photos,
        "total_places": total_places,
        "total_countries": len(all_countries),
        "total_cities": len(all_cities),
        "all_countries": all_countries,
        "all_cities": all_cities,
        "generated_at": generated_at,
    }

    (output_root / "index.html").write_text(html_tpl.render(**ctx), encoding="utf-8")
    (output_root / "index.md").write_text(md_tpl.render(**ctx), encoding="utf-8")

    print(f"DONE — {len(entries)} years indexed.")
    print(f"  html:  {output_root / 'index.html'}")
    print(f"  md:    {output_root / 'index.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
