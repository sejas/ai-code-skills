from lib.enrich import enrich_clusters, slugify
from tests.fixtures.photo_mocks import make_photo


def test_slugify_basic():
    assert slugify("Oslo") == "oslo"


def test_slugify_accents():
    assert slugify("Sevilla") == "sevilla"
    assert slugify("María José") == "maria-jose"
    assert slugify("Las Palmas de Gran Canaria") == "las-palmas-de-gran-canaria"


def test_slugify_empty():
    assert slugify("") == "unknown"
    assert slugify(None) == "unknown"


def test_enrich_uses_mode_city():
    place_oslo = {"city": "Oslo", "country": "Norway", "country_code": "NO", "poi": None}
    place_unknown = {"city": None, "country": None, "country_code": None, "poi": None}
    cluster = {
        "kind": "place",
        "photos": [
            make_photo("2025-07-15T10:00:00", 60.0, 10.0, place=place_oslo),
            make_photo("2025-07-15T10:10:00", 60.0, 10.0, place=place_oslo),
            make_photo("2025-07-15T10:20:00", 60.0, 10.0, place=place_unknown),
        ],
    }
    out = enrich_clusters([cluster])
    assert out[0]["place"]["city"] == "Oslo"
    assert out[0]["place"]["country"] == "Norway"
    assert out[0]["place"]["slug"] == "oslo"


def test_enrich_transit_untouched():
    cluster = {"kind": "transit", "photos": []}
    out = enrich_clusters([cluster])
    assert "place" not in out[0]


def test_enrich_unknown_when_no_place():
    cluster = {
        "kind": "place",
        "photos": [
            make_photo("2025-07-15T10:00:00", 60.0, 10.0, place=None),
            make_photo("2025-07-15T10:10:00", 60.0, 10.0, place=None),
        ],
    }
    out = enrich_clusters([cluster])
    assert out[0]["place"]["city"] == "unknown"
    assert out[0]["place"]["slug"] == "unknown"
