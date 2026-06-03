import json
from pathlib import Path

from lib.render import render_map_html, render_summary_md, write_data_json
from tests.fixtures.photo_mocks import make_photo

TEMPLATES = Path(__file__).resolve().parent.parent / "templates"


def make_place_cluster(idx, city, slug, country, photos, thumbs=None):
    return {
        "id": idx,
        "kind": "place",
        "centroid": (photos[0]["lat"], photos[0]["lon"]),
        "start_ts": photos[0]["ts"],
        "end_ts": photos[-1]["ts"],
        "photo_count": len(photos),
        "dwell_minutes": 60.0,
        "photos": photos,
        "place": {"city": city, "country": country, "country_code": "NO", "slug": slug, "poi": None, "exists_in_vault": False},
        "representative_uuids": [p["uuid"] for p in photos[:2]],
        "representative_thumbs": thumbs or [],
    }


def test_summary_trip_renders(tmp_path):
    photos_a = [make_photo(f"2025-07-15T1{i}:00:00", 60.0, 10.0) for i in range(0, 3)]
    photos_b = [make_photo(f"2025-07-17T1{i}:00:00", 60.5, 10.5) for i in range(0, 3)]
    clusters = [
        make_place_cluster(0, "Oslo", "oslo", "Norway", photos_a),
        make_place_cluster(1, "Bergen", "bergen", "Norway", photos_b),
    ]
    out = tmp_path / "summary.md"
    render_summary_md(clusters, "Norway trip", "trip", TEMPLATES, out)
    text = out.read_text(encoding="utf-8")
    assert "# Norway trip" in text
    assert "[[oslo|Oslo]]" in text
    assert "[[bergen|Bergen]]" in text
    assert "Itinerary" in text


def test_summary_year_renders(tmp_path):
    photos_a = [make_photo(f"2025-07-15T1{i}:00:00", 60.0, 10.0) for i in range(0, 3)]
    photos_b = [make_photo(f"2025-08-17T1{i}:00:00", 60.5, 10.5) for i in range(0, 3)]
    clusters = [
        make_place_cluster(0, "Oslo", "oslo", "Norway", photos_a),
        make_place_cluster(1, "Bergen", "bergen", "Norway", photos_b),
    ]
    out = tmp_path / "summary.md"
    render_summary_md(clusters, "2025 — cities visited", "year", TEMPLATES, out)
    text = out.read_text(encoding="utf-8")
    assert "July 2025" in text
    assert "August 2025" in text
    assert "[[oslo|Oslo]]" in text


def test_map_html_renders(tmp_path):
    photos_a = [make_photo(f"2025-07-15T1{i}:00:00", 60.0, 10.0) for i in range(0, 3)]
    clusters = [make_place_cluster(0, "Oslo", "oslo", "Norway", photos_a, thumbs=["data:image/jpeg;base64,AAAA"])]
    out = tmp_path / "map.html"
    render_map_html(clusters, "Norway trip", TEMPLATES, out, include_thumbs=True)
    text = out.read_text(encoding="utf-8")
    assert "<title>Norway trip</title>" in text
    assert "openfreemap.org" in text
    assert "Oslo" in text
    assert "data:image/jpeg;base64,AAAA" in text


def test_data_json_shape(tmp_path):
    photos_a = [make_photo(f"2025-07-15T1{i}:00:00", 60.0, 10.0) for i in range(0, 3)]
    clusters = [make_place_cluster(0, "Oslo", "oslo", "Norway", photos_a)]
    out = tmp_path / "data.json"
    write_data_json(clusters, out, meta={"title": "x", "mode": "trip"})
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["meta"]["title"] == "x"
    assert len(data["clusters"]) == 1
    assert data["clusters"][0]["place"]["slug"] == "oslo"
