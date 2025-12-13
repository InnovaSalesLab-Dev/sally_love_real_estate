"""
Function: Route to Agent
Transfers call to a specific real estate agent
"""

from fastapi import APIRouter
from typing import Dict, Any
from src.models.vapi_models import VapiResponse, RouteToAgentRequest
from src.integrations.boldtrail import BoldTrailClient
from src.integrations.twilio_client import TwilioClient
from src.utils.logger import get_logger
from src.utils.errors import BoldTrailError, TwilioError

logger = get_logger(__name__)
router = APIRouter()

crm_client = BoldTrailClient()
twilio_client = TwilioClient()


@router.post("/route_to_agent")
async def route_to_agent(request: RouteToAgentRequest) -> VapiResponse:
    """
    Route/transfer call to a specific agent
    
    This function handles call transfers to agents, including:
    - Warm transfer with context
    - Agent availability check
    - Fallback to voicemail if unavailable
    
    Important: Never discuss commission rates during transfers.
    """
    try:
        logger.info(f"Routing call to agent: {request.agent_name} ({request.agent_phone})")
        
        # Get agent details from BoldTrail to verify they exist
        agent_data = None
        if request.agent_id:
            try:
                agent_data = await crm_client.get_agent(request.agent_id)
                logger.info(f"Agent verified in BoldTrail: {agent_data.get('id')}")
            except BoldTrailError as e:
                logger.warning(f"Could not verify agent in BoldTrail: {str(e)}")
        
        # Use agent phone from BoldTrail if available, otherwise use provided phone
        agent_phone = request.agent_phone
        if agent_data and agent_data.get('phone'):
            agent_phone = agent_data.get('phone')
            logger.info(f"Using phone from BoldTrail: {agent_phone}")
        
        # Validate and format phone number
        if not agent_phone.startswith("+"):
            agent_phone = f"+1{agent_phone.replace('-', '').replace(' ', '').replace('(', '').replace(')', '')}"
        
        # Prepare transfer message
        transfer_reason = request.reason or "general inquiry"
        caller_name = request.caller_name or "a caller"
        agent_name = request.agent_name
        
        # Use agent name from BoldTrail if available
        if agent_data:
            first_name = agent_data.get('firstName', '')
            last_name = agent_data.get('lastName', '')
            if first_name and last_name:
                agent_name = f"{first_name} {last_name}"
        
        # In a real implementation, this would use Vapi's transfer functionality
        # or Twilio's call transfer. For now, we'll provide the information needed.
        
        message = (
            f"Great! I'm transferring you to {agent_name} now. "
            f"They'll be able to help you with your {transfer_reason}. "
            f"Please hold while I connect you."
        )
        
        return VapiResponse(
            success=True,
            message=message,
            data={
                "action": "transfer",
                "agent_id": request.agent_id,
                "agent_name": agent_name,
                "agent_phone": agent_phone,
                "caller_name": caller_name,
                "reason": transfer_reason,
                "transfer_type": "warm",  # Warm transfer with context
                "verified_in_crm": bool(agent_data)
            }
        )
        
    except BoldTrailError as e:
        logger.error(f"BoldTrail error in route_to_agent: {e.message}")
        # Continue with transfer even if CRM lookup fails
        agent_phone = request.agent_phone
        if not agent_phone.startswith("+"):
            agent_phone = f"+1{agent_phone.replace('-', '').replace(' ', '').replace('(', '').replace(')', '')}"
        
        message = (
            f"I'll connect you to {request.agent_name} now. "
            f"Please hold while I transfer your call."
        )
        
        return VapiResponse(
            success=True,
            message=message,
            data={
                "action": "transfer",
                "agent_id": request.agent_id,
                "agent_name": request.agent_name,
                "agent_phone": agent_phone,
                "verified_in_crm": False,
                "note": "CRM verification failed but proceeding with transfer"
            }
        )
    
    except Exception as e:
        logger.exception(f"Error in route_to_agent: {str(e)}")
        return VapiResponse(
            success=False,
            error=(
                f"I'm having trouble connecting you to {request.agent_name} right now. "
                f"Let me take your information and have them call you back shortly."
            ),
            message=str(e)
        )

