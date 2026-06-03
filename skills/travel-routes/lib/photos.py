"""Apple Photos query wrapper around osxphotos.

Returns plain dicts so downstream code is test-friendly (no PhotosDB needed in tests).
"""

from __future__ import annotations

from datetime import datetime
from typing import Iterator, Sequence

from .geo import in_excluded_zone


def _place_to_dict(place) -> dict | None:
    """Flatten an osxphotos PlaceInfo into a plain dict."""
    if place is None:
        return None
    # osxphotos PlaceInfo has .name (full address-ish), .country_code, .names dict
    names = getattr(place, "names", None)
    country = getattr(place, "country", None) or (names.country[0] if names and names.country else None)
    country_code = getattr(place, "country_code", None)
    city = None
    if names:
        for attr in ("city", "sub_administrative_area", "administrative_area", "area_of_interest"):
            vals = getattr(names, attr, None)
            if vals:
                city = vals[0]
                break
    poi = None
    if names and getattr(names, "area_of_interest", None):
        poi = names.area_of_interest[0]
    return {
        "name": getattr(place, "name", None),
        "country": country,
        "country_code": country_code,
        "city": city,
        "poi": poi,
    }


def query_photos(
    db,
    start: datetime,
    end: datetime,
    exclude_zones: Sequence[dict],
) -> Iterator[dict]:
    """Yield photo dicts in [start, end] with GPS, filtered by exclude_zones.

    `db` is an osxphotos.PhotosDB (or any object with `.query(QueryOptions)`).
    """
    import osxphotos

    opts = osxphotos.QueryOptions(
        from_date=start,
        to_date=end,
        location=True,
        movies=False,
    )
    for p in db.query(opts):
        lat, lon = p.latitude, p.longitude
        if lat is None or lon is None:
            continue
        if in_excluded_zone(lat, lon, exclude_zones):
            continue
        yield photo_to_dict(p)


def photo_to_dict(p) -> dict:
    """Convert an osxphotos PhotoInfo to a serializable dict."""
    ts = p.date.isoformat() if p.date else None
    return {
        "uuid": p.uuid,
        "ts": ts,
        "lat": p.latitude,
        "lon": p.longitude,
        "filename": p.original_filename,
        "favorite": bool(p.favorite),
        "keywords": list(p.keywords) if p.keywords else [],
        "place": _place_to_dict(p.place),
    }


def resolve_local_path(photo) -> str | None:
    """Return a usable local JPEG path for thumbnail purposes.

    Order: original (.path) > preview derivative (.path_derivatives[0]) > None.
    Handles iCloud-only photos.
    """
    if photo.path:
        return photo.path
    derivs = photo.path_derivatives or []
    return derivs[0] if derivs else None


def pick_representative_uuids(cluster: dict, per_cluster: int) -> list[str]:
    """Pick representative photo UUIDs for a cluster.

    Strategy: favourites first (sorted by ts), then evenly-spaced fill from non-favourites.
    """
    photos = cluster.get("photos", [])
    if not photos:
        return []
    favourites = [p for p in photos if p.get("favorite")]
    favourites.sort(key=lambda p: p["ts"])
    chosen = favourites[:per_cluster]
    if len(chosen) >= per_cluster:
        return [p["uuid"] for p in chosen]
    remaining = [p for p in photos if not p.get("favorite")]
    remaining.sort(key=lambda p: p["ts"])
    need = per_cluster - len(chosen)
    if remaining:
        if len(remaining) <= need:
            chosen.extend(remaining)
        else:
            step = len(remaining) / need
            chosen.extend(remaining[int(i * step)] for i in range(need))
    chosen.sort(key=lambda p: p["ts"])
    return [p["uuid"] for p in chosen]
