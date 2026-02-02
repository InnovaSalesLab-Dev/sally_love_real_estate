"""
Agent roster service - loads and queries agent_roster.json as the source of truth for transfers.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.utils.logger import get_logger

logger = get_logger(__name__)

# Default roster path relative to project root
_DEFAULT_ROSTER_PATH = "data/agent_roster.json"

# Cached roster data (loaded on first access)
_cached_roster: Optional[Dict[str, Any]] = None


def clear_roster_cache() -> None:
    """Clear the roster cache (for testing)."""
    global _cached_roster
    _cached_roster = None


def _normalize_phone(phone: str) -> str:
    """Strip non-digits and return last 10 digits for comparison."""
    if not phone:
        return ""
    digits = "".join(c for c in str(phone) if c.isdigit())
    if len(digits) >= 10:
        return digits[-10:]
    return digits


def _normalize_name(name: str) -> str:
    """Normalize name for comparison: lowercase, strip."""
    if not name:
        return ""
    return " ".join(str(name).strip().lower().split())


def _agent_has_valid_phone(agent: Dict[str, Any]) -> bool:
    """Check if agent has a non-empty cell_phone."""
    phone = agent.get("cell_phone") or agent.get("phone") or ""
    return bool(phone and _normalize_phone(phone))


def load_roster(roster_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load agent roster from JSON file. Caches result for subsequent calls (when using default path).
    Uses agents + staff; excludes trusted_partner_title_staff for transfers.
    """
    global _cached_roster
    # Only use cache when loading default path (no custom path)
    if _cached_roster is not None and roster_path is None:
        return _cached_roster

    path = Path(roster_path or _DEFAULT_ROSTER_PATH)
    if not path.is_absolute():
        # Resolve relative to project root (parent of src)
        project_root = Path(__file__).resolve().parent.parent.parent
        path = project_root / path

    if not path.exists():
        logger.warning(f"Roster file not found: {path}")
        data = {"agents": [], "staff": [], "company": {}}
        if roster_path is None:
            _cached_roster = data
        return data

    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if roster_path is None:
            _cached_roster = data
        return data
    except Exception as e:
        logger.exception(f"Failed to load roster from {path}: {e}")
        data = {"agents": [], "staff": [], "company": {}}
        if roster_path is None:
            _cached_roster = data
        return data


def _get_all_transferable_agents(roster_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Return agents + staff with valid phone numbers (no TPT staff)."""
    roster = load_roster(roster_path)
    agents = roster.get("agents", []) or []
    staff = roster.get("staff", []) or []
    combined = agents + staff
    return [a for a in combined if _agent_has_valid_phone(a)]


def find_agent_by_name(
    name: str,
    roster_path: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """
    Find agent by name (case-insensitive, partial match).
    E.g. "Sally" matches "Sally Love".
    """
    if not name or not name.strip():
        return None

    normalized_query = _normalize_name(name)
    if not normalized_query:
        return None

    for agent in _get_all_transferable_agents(roster_path):
        agent_name = agent.get("name") or ""
        normalized_agent = _normalize_name(agent_name)
        # Exact match or query is contained in agent name (e.g. "sally" in "sally love")
        if normalized_query == normalized_agent or normalized_query in normalized_agent:
            return agent
        # Agent name contained in query (e.g. caller said "Sally Love")
        if normalized_agent in normalized_query:
            return agent

    return None


def find_agent_by_phone(
    phone: str,
    roster_path: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Find agent by phone number (normalized last 10 digits)."""
    if not phone:
        return None

    target = _normalize_phone(phone)
    if not target or len(target) < 10:
        return None

    for agent in _get_all_transferable_agents(roster_path):
        agent_phone = agent.get("cell_phone") or agent.get("phone") or ""
        if _normalize_phone(agent_phone) == target:
            return agent

    return None


def is_agent_in_roster(
    name: Optional[str],
    phone: Optional[str],
    roster_path: Optional[str] = None,
) -> bool:
    """
    Check if the given name and/or phone match a roster agent.
    If both provided, both must match the same agent.
    If only one provided, that is sufficient.
    """
    if not name and not phone:
        return False

    if name and phone:
        by_name = find_agent_by_name(name, roster_path)
        if not by_name:
            return False
        return _normalize_phone(by_name.get("cell_phone") or by_name.get("phone") or "") == _normalize_phone(phone)

    if name:
        return find_agent_by_name(name, roster_path) is not None
    if phone:
        return find_agent_by_phone(phone, roster_path) is not None

    return False


def get_any_agent(roster_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Return first agent from roster with valid phone (fallback when requested agent not found)."""
    agents = _get_all_transferable_agents(roster_path)
    return agents[0] if agents else None


def get_roster_phone_for_name(
    name: str,
    roster_path: Optional[str] = None,
) -> Optional[str]:
    """
    Get roster cell_phone for an agent by name.
    Returns None if no match or no valid phone.
    """
    agent = find_agent_by_name(name, roster_path)
    if not agent:
        return None
    return agent.get("cell_phone") or agent.get("phone") or None


def get_main_office_phone(roster_path: Optional[str] = None) -> Optional[str]:
    """Get main office phone from roster company info."""
    roster = load_roster(roster_path)
    company = roster.get("company") or {}
    return company.get("main_office_phone")
