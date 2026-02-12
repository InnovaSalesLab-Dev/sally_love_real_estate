"""
Unit tests for BoldTrail address matching (phonetic + number-first logic)
and city matching (The Villages area).
"""

import pytest
from src.integrations.boldtrail import BoldTrailClient


@pytest.fixture
def client():
    return BoldTrailClient()


def test_gallenoll_matches_gallinule(client):
    """3016 Gallenoll Court (misheard) should match 3016 Gallinule Court (actual)."""
    assert client._address_matches(
        "3016 Gallinule Court",
        "3016 Gallenoll Court"
    ) is True


def test_bella_vista_matches_bellavista(client):
    """Street name only: Bella Vista should match Bellavista Circle."""
    assert client._address_matches(
        "16642 SE 80th Bellavista Circle",
        "Bella Vista"
    ) is True


def test_exact_match(client):
    """Exact address match."""
    assert client._address_matches(
        "2121 Auburn Lane",
        "2121 Auburn Lane"
    ) is True


def test_partial_address_match(client):
    """Partial address: street number + name."""
    assert client._address_matches(
        "3016 Gallinule Court",
        "3016 Gallinule"
    ) is True


def test_no_false_positive_different_number(client):
    """Different street number should NOT match."""
    assert client._address_matches(
        "3016 Gallinule Court",
        "3017 Gallenoll Court"
    ) is False


def test_no_false_positive_different_street_type(client):
    """Same number but different street type should NOT match when number-first."""
    assert client._address_matches(
        "3016 Gallinule Court",
        "3016 Gallenoll Drive"
    ) is False


def test_gallonol_spelling(client):
    """Another common mishearing: Gallonol vs Gallinule."""
    assert client._address_matches(
        "3016 Gallinule Court",
        "3016 Gallonol Court"
    ) is True


def test_belle_vista_matches_bellavista(client):
    """Belle Vista (2 words) or Belvista (1 word) should match Bellavista Circle."""
    assert client._address_matches(
        "16642 SE 80th Bellavista Circle",
        "Belle Vista Circle"
    ) is True
    assert client._address_matches(
        "16642 SE 80th Bellavista Circle",
        "Belvista Circle"
    ) is True


def test_city_the_villages_matches_lady_lake(client):
    """Search city 'The Villages' should match listing in Lady Lake."""
    assert client._city_matches("Lady Lake", "The Villages") is True


def test_city_the_villages_matches_oxford(client):
    """Search city 'The Villages' should match listing in Oxford."""
    assert client._city_matches("Oxford", "The Villages") is True


def test_city_exact_match(client):
    """Exact city match."""
    assert client._city_matches("Lady Lake", "Lady Lake") is True


def test_city_villages_short_form(client):
    """Search city 'Villages' (short form) should match The Villages area."""
    assert client._city_matches("Summerfield", "Villages") is True
