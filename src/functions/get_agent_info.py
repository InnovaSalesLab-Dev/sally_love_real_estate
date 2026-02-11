"""
Function: Get Agent Info
Retrieves information about real estate agents from the agent roster.
"""

from fastapi import APIRouter

from src.config.settings import settings
from src.models.vapi_models import GetAgentInfoRequest, VapiResponse
from src.utils.logger import get_logger
from src.utils.roster import (
    find_agent_by_name,
    get_any_agent,
    load_roster,
)


def _get_jeff_fallback(roster_path) -> dict | None:
    """Return Jeff Beatty for fallback when requested agent not found."""
    return find_agent_by_name("Jeff Beatty", roster_path)

logger = get_logger(__name__)
router = APIRouter()


def _roster_agent_to_response(agent: dict, roster_matched: bool = True) -> dict:
    """Map roster schema to response shape for route_to_agent compatibility."""
    name = agent.get("name") or ""
    parts = name.split(None, 1)
    first_name = parts[0] if parts else name
    last_name = parts[1] if len(parts) > 1 else ""
    phone = agent.get("cell_phone") or agent.get("phone") or ""
    return {
        "name": name,
        "firstName": first_name,
        "lastName": last_name,
        "phone": phone,
        "email": agent.get("email") or "",
        "roster_matched": roster_matched,
    }


@router.post("/get_agent_info")
async def get_agent_info(request: GetAgentInfoRequest) -> VapiResponse:
    """
    Get information about real estate agents from the roster.

    Source: data/agent_roster.json (agents + staff).
    Can search by agent name. If no match, returns a fallback agent.
    """
    roster_path = settings.AGENT_ROSTER_PATH or None

    try:
        logger.info(f"Getting agent info: {request.model_dump()}")

        agents: list[dict] = []
        roster_matched = True

        if request.agent_name and request.agent_name.strip():
            # Search by name
            agent = find_agent_by_name(request.agent_name.strip(), roster_path)
            if agent:
                agents = [_roster_agent_to_response(agent, roster_matched=True)]
            else:
                # Fallback: use Jeff (not a random roster agent like Star Amador)
                fallback = _get_jeff_fallback(roster_path)
                if fallback:
                    agents = [_roster_agent_to_response(fallback, roster_matched=False)]
                    roster_matched = False
                    logger.info(f"Agent '{request.agent_name}' not in roster; using Jeff fallback: {fallback.get('name')}")
        else:
            # No name: return first N agents
            roster = load_roster(roster_path)
            all_agents = (roster.get("agents") or []) + (roster.get("staff") or [])
            # Filter to those with valid phone, take first 5
            with_phone = [a for a in all_agents if a.get("cell_phone") or a.get("phone")][:5]
            agents = [_roster_agent_to_response(a, roster_matched=True) for a in with_phone]

        if not agents:
            return VapiResponse(
                success=True,
                message="I couldn't find any available agents right now. Let me connect you with our office.",
                results=[],
                data={"count": 0, "roster_matched": False},
            )

        if len(agents) == 1:
            agent = agents[0]
            message = f"I have information about {agent.get('name', 'an agent')}. Would you like me to connect you with them?"
        else:
            message = "Let me connect you with one of our agents."

        return VapiResponse(
            success=True,
            message=message,
            results=agents,
            data={"count": len(agents), "roster_matched": roster_matched},
        )

    except Exception as e:
        logger.exception(f"Error in get_agent_info: {e}")
        return VapiResponse(
            success=False,
            error="I encountered an error while looking up agent information.",
            message=str(e),
        )
