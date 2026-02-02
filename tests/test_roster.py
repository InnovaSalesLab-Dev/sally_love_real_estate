"""
Unit tests for the roster service (src/utils/roster.py).
"""

import json
import tempfile
from pathlib import Path

import pytest

from src.utils.roster import (
    find_agent_by_name,
    find_agent_by_phone,
    get_any_agent,
    get_main_office_phone,
    get_roster_phone_for_name,
    is_agent_in_roster,
    load_roster,
)


@pytest.fixture
def sample_roster_file(tmp_path):
    """Create a temporary roster JSON file for testing."""
    roster = {
        "company": {"main_office_phone": "352-290-8023"},
        "agents": [
            {"name": "Kim Coffer", "cell_phone": "352-626-7671", "email": "kim@test.com"},
            {"name": "Sally Love", "cell_phone": "352-430-6960", "email": "sally@test.com"},
            {"name": "Jeff Beatty", "cell_phone": "352-600-0334", "email": "jeff@test.com"},
        ],
        "staff": [
            {"name": "Blerim Prenaj", "cell_phone": "352-626-7772", "email": "bp@test.com"},
        ],
    }
    path = tmp_path / "roster.json"
    path.write_text(json.dumps(roster), encoding="utf-8")
    return str(path)


class TestLoadRoster:
    def test_load_roster_returns_data(self, sample_roster_file):
        data = load_roster(sample_roster_file)
        assert "agents" in data
        assert "staff" in data
        assert len(data["agents"]) == 3
        assert len(data["staff"]) == 1

    def test_load_roster_idempotent(self, sample_roster_file):
        d1 = load_roster(sample_roster_file)
        d2 = load_roster(sample_roster_file)
        assert d1 == d2


class TestFindAgentByName:
    def test_find_exact_match(self, sample_roster_file):
        agent = find_agent_by_name("Kim Coffer", sample_roster_file)
        assert agent is not None
        assert agent["name"] == "Kim Coffer"
        assert agent["cell_phone"] == "352-626-7671"

    def test_find_partial_match(self, sample_roster_file):
        agent = find_agent_by_name("Sally", sample_roster_file)
        assert agent is not None
        assert "Sally" in agent["name"]

    def test_find_case_insensitive(self, sample_roster_file):
        agent = find_agent_by_name("KIM COFFER", sample_roster_file)
        assert agent is not None
        assert agent["name"] == "Kim Coffer"

    def test_find_no_match(self, sample_roster_file):
        agent = find_agent_by_name("Unknown Person", sample_roster_file)
        assert agent is None

    def test_find_empty_name(self, sample_roster_file):
        agent = find_agent_by_name("", sample_roster_file)
        assert agent is None


class TestFindAgentByPhone:
    def test_find_by_phone_dash_format(self, sample_roster_file):
        agent = find_agent_by_phone("352-626-7671", sample_roster_file)
        assert agent is not None
        assert agent["name"] == "Kim Coffer"

    def test_find_by_phone_e164_format(self, sample_roster_file):
        agent = find_agent_by_phone("+13526267671", sample_roster_file)
        assert agent is not None
        assert agent["name"] == "Kim Coffer"

    def test_find_by_phone_no_match(self, sample_roster_file):
        agent = find_agent_by_phone("555-123-4567", sample_roster_file)
        assert agent is None


class TestIsAgentInRoster:
    def test_in_roster_by_name_and_phone(self, sample_roster_file):
        assert is_agent_in_roster("Kim Coffer", "352-626-7671", sample_roster_file) is True

    def test_in_roster_by_name_only(self, sample_roster_file):
        assert is_agent_in_roster("Kim Coffer", None, sample_roster_file) is True

    def test_in_roster_by_phone_only(self, sample_roster_file):
        assert is_agent_in_roster(None, "352-626-7671", sample_roster_file) is True

    def test_not_in_roster_wrong_phone(self, sample_roster_file):
        assert is_agent_in_roster("Kim Coffer", "555-123-4567", sample_roster_file) is False

    def test_not_in_roster_unknown_name(self, sample_roster_file):
        assert is_agent_in_roster("Unknown", "352-626-7671", sample_roster_file) is False

    def test_empty_both_returns_false(self, sample_roster_file):
        assert is_agent_in_roster(None, None, sample_roster_file) is False


class TestGetAnyAgent:
    def test_returns_agent(self, sample_roster_file):
        agent = get_any_agent(sample_roster_file)
        assert agent is not None
        assert "name" in agent
        assert agent.get("cell_phone") or agent.get("phone")


class TestGetRosterPhoneForName:
    def test_returns_phone(self, sample_roster_file):
        phone = get_roster_phone_for_name("Kim Coffer", sample_roster_file)
        assert phone == "352-626-7671"

    def test_returns_none_for_unknown(self, sample_roster_file):
        phone = get_roster_phone_for_name("Unknown", sample_roster_file)
        assert phone is None


class TestGetMainOfficePhone:
    def test_returns_office_phone(self, sample_roster_file):
        phone = get_main_office_phone(sample_roster_file)
        assert phone == "352-290-8023"
