"""Enrich place clusters with city/country from PhotoInfo.place.

No network calls. Apple already reverse-geocoded photos on-device.
Adds:
  cluster['place'] = {city, country, country_code, slug, poi, exists_in_vault}
"""

from __future__ import annotations

import os
import re
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Iterable


def slugify(value: str) -> str:
    """ASCII kebab-case slug. Strips accents, lowercases, collapses non-alnum to '-'."""
    if not value:
        return "unknown"
    norm = unicodedata.normalize("NFKD", value)
    ascii_only = norm.encode("ascii", "ignore").decode("ascii")
    ascii_only = ascii_only.lower().strip()
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_only).strip("-")
    return slug or "unknown"


def _mode_field(places: Iterable[dict | None], field: str) -> str | None:
    """Most common non-empty value for `field` across the photos' places."""
    values = [p[field] for p in places if p and p.get(field)]
    if not values:
        return None
    return Counter(values).most_common(1)[0][0]


def _scan_vault_slugs(vault_places_dir: str | None) -> set[str]:
    """Return slugs of existing place notes in the vault, or empty set if dir missing."""
    if not vault_places_dir:
        return set()
    path = Path(os.path.expanduser(vault_places_dir))
    if not path.is_dir():
        return set()
    return {p.stem for p in path.glob("*.md")}


def enrich_clusters(clusters: list[dict], vault_places_dir: str | None = None) -> list[dict]:
    """Mutate + return clusters: add 'place' dict to every 'place'-kind cluster."""
    vault_slugs = _scan_vault_slugs(vault_places_dir)
    for c in clusters:
        if c["kind"] != "place":
            continue
        photo_places = [p.get("place") for p in c["photos"]]
        city = _mode_field(photo_places, "city")
        country = _mode_field(photo_places, "country")
        country_code = _mode_field(photo_places, "country_code")
        poi = _mode_field(photo_places, "poi")
        slug = slugify(city) if city else "unknown"
        c["place"] = {
            "city": city or "unknown",
            "country": country,
            "country_code": country_code,
            "poi": poi,
            "slug": slug,
            "exists_in_vault": slug in vault_slugs,
        }
    return clusters
