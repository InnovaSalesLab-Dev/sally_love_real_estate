"""
Function: Get Agent Info
Retrieves information about real estate agents
"""

from fastapi import APIRouter
from typing import Dict, Any
from src.models.vapi_models import VapiResponse, GetAgentInfoRequest
from src.integrations.boldtrail import BoldTrailClient
from src.utils.logger import get_logger
from src.utils.errors import BoldTrailError

logger = get_logger(__name__)
router = APIRouter()

crm_client = BoldTrailClient()


@router.post("/get_agent_info")
async def get_agent_info(request: GetAgentInfoRequest) -> VapiResponse:
    """
    Get information about real estate agents
    
    This function retrieves agent details including:
    - Contact information
    - Specialties (buyer's agent, listing agent, commercial, etc.)
    - Service areas
    - Availability
    - Languages spoken
    
    Can search by agent name, ID, specialty, or city.
    """
    try:
        logger.info(f"Getting agent info: {request.model_dump()}")
        
        # Search for agents
        if request.agent_id:
            # Get specific agent by ID
            agent_data = await crm_client.get_agent(request.agent_id)
            agents = [agent_data] if agent_data else []
        else:
            # Search agents by criteria
            agents = await crm_client.get_agents(
                specialty=request.specialty,
                city=request.city,
                available=True
            )
        
        if not agents:
            return VapiResponse(
                success=True,
                message="I couldn't find any available agents matching that criteria. Let me connect you with our office.",
                results=[]
            )
        
        # Format response for voice
        if len(agents) == 1:
            agent = agents[0]
            message = (
                f"I have information about {agent.get('firstName')} {agent.get('lastName')}. "
            )
            
            if agent.get('specialties'):
                specialties = ", ".join(agent.get('specialties', [])[:2])
                message += f"They specialize in {specialties}. "
            
            if agent.get('serviceAreas'):
                areas = ", ".join(agent.get('serviceAreas', [])[:2])
                message += f"They service the {areas} area. "
            
            if agent.get('yearsExperience'):
                message += f"They have {agent.get('yearsExperience')} years of experience. "
            
            message += "Would you like me to connect you with them?"
            
        else:
            message = (
                f"I found {len(agents)} available agents. "
                f"Would you like me to tell you about each one, or connect you with the first available agent?"
            )
        
        return VapiResponse(
            success=True,
            message=message,
            results=agents,
            data={"count": len(agents)}
        )
        
    except BoldTrailError as e:
        logger.error(f"CRM error in get_agent_info: {e.message}")
        return VapiResponse(
            success=False,
            error="I'm having trouble accessing our agent directory. Let me transfer you to our office.",
            message=e.message
        )
    
    except Exception as e:
        logger.exception(f"Error in get_agent_info: {str(e)}")
        return VapiResponse(
            success=False,
            error="I encountered an error while looking up agent information.",
            message=str(e)
        )

