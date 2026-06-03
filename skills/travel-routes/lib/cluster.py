"""Walking timeline clusterer.

Sorts photos by timestamp, walks chronologically, opens a new cluster when:
  - distance from running centroid exceeds `eps_meters`, OR
  - time gap from previous photo exceeds `max_gap_hours`.

After clustering, each cluster is classified:
  - 'place' if dwell >= min_dwell_minutes AND len(photos) >= min_samples
  - 'transit' otherwise (still kept; consumed by the route polyline)
"""

from __future__ import annotations

from datetime import datetime
from typing import Sequence

from .geo import haversine_m, weighted_centroid


def _parse_ts(ts: str) -> datetime:
    return datetime.fromisoformat(ts)


def cluster_points(
    points: Sequence[dict],
    eps_meters: float = 200.0,
    min_dwell_minutes: float = 20.0,
    min_samples: int = 3,
    max_gap_hours: float = 12.0,
) -> list[dict]:
    """Return clusters in chronological order.

    Each cluster: {
        id: int,
        photos: [<photo dict>, ...],
        centroid: (lat, lon),
        start_ts, end_ts: ISO strings,
        photo_count: int,
        kind: 'place' | 'transit',
    }
    """
    if not points:
        return []

    sorted_pts = sorted(points, key=lambda p: p["ts"])
    clusters: list[list[dict]] = []
    current: list[dict] = []

    def flush() -> None:
        if current:
            clusters.append(list(current))
            current.clear()

    for p in sorted_pts:
        if not current:
            current.append(p)
            continue
        ts_prev = _parse_ts(current[-1]["ts"])
        ts_now = _parse_ts(p["ts"])
        gap_h = (ts_now - ts_prev).total_seconds() / 3600.0
        if gap_h > max_gap_hours:
            flush()
            current.append(p)
            continue
        # centroid of current cluster (uniform weight)
        cent_lat, cent_lon = weighted_centroid([(c["lat"], c["lon"], 1) for c in current])
        dist = haversine_m(cent_lat, cent_lon, p["lat"], p["lon"])
        if dist > eps_meters:
            flush()
            current.append(p)
        else:
            current.append(p)
    flush()

    out: list[dict] = []
    for idx, group in enumerate(clusters):
        start_ts = group[0]["ts"]
        end_ts = group[-1]["ts"]
        dwell_min = (_parse_ts(end_ts) - _parse_ts(start_ts)).total_seconds() / 60.0
        kind = "place" if (dwell_min >= min_dwell_minutes and len(group) >= min_samples) else "transit"
        cent = weighted_centroid([(p["lat"], p["lon"], 1) for p in group])
        out.append({
            "id": idx,
            "photos": group,
            "centroid": cent,
            "start_ts": start_ts,
            "end_ts": end_ts,
            "photo_count": len(group),
            "dwell_minutes": dwell_min,
            "kind": kind,
        })
    return out
