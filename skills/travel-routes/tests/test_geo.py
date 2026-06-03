from lib.geo import haversine_m, in_excluded_zone, weighted_centroid


def test_haversine_zero():
    assert haversine_m(0, 0, 0, 0) == 0.0


def test_haversine_known_distance():
    # ~111 km between (0,0) and (1,0)
    d = haversine_m(0, 0, 1, 0)
    assert 110_000 < d < 112_000


def test_in_excluded_zone_hit():
    zones = [{"lat": 28.10, "lon": -15.50, "radius_m": 500}]
    assert in_excluded_zone(28.10, -15.50, zones) is True
    assert in_excluded_zone(28.1001, -15.5001, zones) is True


def test_in_excluded_zone_miss():
    zones = [{"lat": 28.10, "lon": -15.50, "radius_m": 500}]
    assert in_excluded_zone(28.20, -15.50, zones) is False


def test_in_excluded_zone_empty():
    assert in_excluded_zone(0, 0, []) is False


def test_weighted_centroid_uniform():
    lat, lon = weighted_centroid([(0.0, 0.0, 1), (2.0, 2.0, 1)])
    assert abs(lat - 1.0) < 1e-9
    assert abs(lon - 1.0) < 1e-9


def test_weighted_centroid_weighted():
    lat, lon = weighted_centroid([(0.0, 0.0, 3), (4.0, 4.0, 1)])
    assert abs(lat - 1.0) < 1e-9
    assert abs(lon - 1.0) < 1e-9
