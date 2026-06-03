from datetime import timedelta

from lib.cluster import cluster_points
from tests.fixtures.photo_mocks import linear_walk, make_photo


def test_empty_input():
    assert cluster_points([]) == []


def test_single_dwell_is_place():
    photos = linear_walk("2025-07-15T10:00:00", 60.0, 10.0, n=5, step_min=10)  # 40-min dwell
    clusters = cluster_points(photos, eps_meters=200, min_dwell_minutes=20, min_samples=3)
    assert len(clusters) == 1
    assert clusters[0]["kind"] == "place"
    assert clusters[0]["photo_count"] == 5


def test_short_dwell_is_transit():
    # Only 2 photos within 5 minutes → fails min_dwell + min_samples
    photos = linear_walk("2025-07-15T10:00:00", 60.0, 10.0, n=2, step_min=5)
    clusters = cluster_points(photos, eps_meters=200, min_dwell_minutes=20, min_samples=3)
    assert len(clusters) == 1
    assert clusters[0]["kind"] == "transit"


def test_two_dwells_separated_by_distance():
    a = linear_walk("2025-07-15T09:00:00", 60.0, 10.0, n=5, step_min=10)
    b = linear_walk("2025-07-15T14:00:00", 60.5, 10.5, n=5, step_min=10)  # ~70km away
    clusters = cluster_points(a + b, eps_meters=200)
    place_clusters = [c for c in clusters if c["kind"] == "place"]
    assert len(place_clusters) == 2


def test_time_gap_splits_cluster():
    a = linear_walk("2025-07-15T10:00:00", 60.0, 10.0, n=3, step_min=10)
    # Same coords but 24h later → gap > max_gap_hours
    b = linear_walk("2025-07-16T10:00:00", 60.0, 10.0, n=3, step_min=10)
    clusters = cluster_points(a + b, max_gap_hours=12)
    assert len(clusters) == 2


def test_unsorted_input_is_sorted():
    photos = (
        linear_walk("2025-07-15T12:00:00", 60.0, 10.0, n=3, step_min=10)
        + linear_walk("2025-07-15T09:00:00", 60.0, 10.0, n=3, step_min=10)
    )
    clusters = cluster_points(photos, max_gap_hours=12)
    # Since both bursts at same coords within 3h gap and same place → one cluster
    assert len(clusters) == 1
    # Verify start_ts is earlier of the two
    assert clusters[0]["start_ts"].startswith("2025-07-15T09:00:00")
