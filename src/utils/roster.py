"""
Agent roster service - loads and queries agent_roster.json as the source of truth for transfers.
"""

import json
from difflib import SequenceMatcher
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


def _fuzzy_score(a: str, b: str) -> float:
    """Return similarity ratio between two strings (0.0 - 1.0)."""
    return SequenceMatcher(None, a, b).ratio()


def find_agent_by_name(
    name: str,
    roster_path: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """
    Find agent by name using a multi-pass strategy:
      1. Exact / substring match (case-insensitive)
      2. Last-name-only match (handles "Ulmer" matching "Jeannie Ulmer")
      3. Fuzzy match (handles transcription variants like Jeanne→Jeannie)

    Returns the best match or None.
    """
    if not name or not name.strip():
        return None

    normalized_query = _normalize_name(name)
    if not normalized_query:
        return None

    all_agents = _get_all_transferable_agents(roster_path)

    # --- Pass 1: Exact / substring match (original logic) ---
    for agent in all_agents:
        agent_name = agent.get("name") or ""
        normalized_agent = _normalize_name(agent_name)
        # Exact match or query is contained in agent name (e.g. "sally" in "sally love")
        if normalized_query == normalized_agent or normalized_query in normalized_agent:
            return agent
        # Agent name contained in query (e.g. caller said "Sally Love")
        if normalized_agent in normalized_query:
            return agent

    # --- Pass 2: Last-name match ---
    # Extract the last token of the query as a likely last name
    query_parts = normalized_query.split()
    query_last = query_parts[-1] if query_parts else ""
    if query_last and len(query_last) >= 3:
        last_name_matches: list[Dict[str, Any]] = []
        for agent in all_agents:
            agent_name = agent.get("name") or ""
            agent_parts = _normalize_name(agent_name).split()
            agent_last = agent_parts[-1] if agent_parts else ""
            if agent_last and agent_last == query_last:
                last_name_matches.append(agent)
        if len(last_name_matches) == 1:
            # Unique last-name hit — safe to use
            logger.info(
                f"Agent '{name}' matched by last name to '{last_name_matches[0].get('name')}'"
            )
            return last_name_matches[0]

    # --- Pass 3: Fuzzy match on full name (threshold ≥ 0.80) ---
    FUZZY_THRESHOLD = 0.80
    best_agent: Optional[Dict[str, Any]] = None
    best_score = 0.0
    for agent in all_agents:
        agent_name = agent.get("name") or ""
        normalized_agent = _normalize_name(agent_name)
        score = _fuzzy_score(normalized_query, normalized_agent)
        if score > best_score:
            best_score = score
            best_agent = agent

    if best_agent and best_score >= FUZZY_THRESHOLD:
        logger.info(
            f"Agent '{name}' fuzzy-matched to '{best_agent.get('name')}' "
            f"(score={best_score:.2f})"
        )
        return best_agent

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
