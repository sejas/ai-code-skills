"""Geo math: Haversine distance, centroid, exclude-zone filter.

Pure stdlib. No external deps.
"""

from __future__ import annotations

import math
from typing import Iterable, Sequence


EARTH_RADIUS_M = 6_371_000.0


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in metres between two lat/lon points."""
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return 2 * EARTH_RADIUS_M * math.asin(math.sqrt(a))


def weighted_centroid(points: Sequence[tuple[float, float, int]]) -> tuple[float, float]:
    """Weighted centroid of (lat, lon, weight) triples.

    Spherical-projection aware (small datasets, OK to use planar mean for personal scale).
    Returns (lat, lon).
    """
    if not points:
        raise ValueError("centroid of empty point list")
    total_w = sum(w for _, _, w in points) or 1
    lat = sum(p[0] * p[2] for p in points) / total_w
    lon = sum(p[1] * p[2] for p in points) / total_w
    return lat, lon


def in_excluded_zone(lat: float, lon: float, zones: Iterable[dict]) -> bool:
    """True if (lat,lon) is within radius_m of any zone."""
    for z in zones:
        if haversine_m(lat, lon, z["lat"], z["lon"]) <= z["radius_m"]:
            return True
    return False
