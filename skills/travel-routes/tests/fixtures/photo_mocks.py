"""Synthetic photo fixtures (no PhotosDB dependency)."""

from __future__ import annotations

from datetime import datetime, timedelta


def make_photo(ts: str, lat: float, lon: float, *, uuid: str | None = None,
               favorite: bool = False, place: dict | None = None) -> dict:
    return {
        "uuid": uuid or f"u-{ts}-{lat:.4f}-{lon:.4f}",
        "ts": ts,
        "lat": lat,
        "lon": lon,
        "filename": f"IMG_{ts.replace(':', '')}.jpg",
        "favorite": favorite,
        "keywords": [],
        "place": place,
    }


def linear_walk(start_iso: str, lat: float, lon: float, n: int, step_min: int = 5) -> list[dict]:
    """N photos at same coords, step_min apart — simulates dwell at one place."""
    base = datetime.fromisoformat(start_iso)
    return [
        make_photo((base + timedelta(minutes=step_min * i)).isoformat(), lat, lon)
        for i in range(n)
    ]
