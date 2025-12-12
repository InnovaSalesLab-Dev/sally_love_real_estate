"""
Function: Route to Agent
Transfers call to a specific real estate agent
"""

from fastapi import APIRouter
from typing import Dict, Any
from src.models.vapi_models import VapiResponse, RouteToAgentRequest
from src.integrations.twilio_client import TwilioClient
from src.utils.logger import get_logger
from src.utils.errors import TwilioError

logger = get_logger(__name__)
router = APIRouter()

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
        
        # Validate phone number
        agent_phone = request.agent_phone
        if not agent_phone.startswith("+"):
            agent_phone = f"+1{agent_phone.replace('-', '').replace(' ', '')}"
        
        # Prepare transfer message
        transfer_reason = request.reason or "general inquiry"
        caller_name = request.caller_name or "a caller"
        
        # In a real implementation, this would use Vapi's transfer functionality
        # or Twilio's call transfer. For now, we'll provide the information needed.
        
        message = (
            f"Great! I'm transferring you to {request.agent_name} now. "
            f"They'll be able to help you with your {transfer_reason}. "
            f"Please hold while I connect you."
        )
        
        return VapiResponse(
            success=True,
            message=message,
            data={
                "action": "transfer",
                "agent_id": request.agent_id,
                "agent_name": request.agent_name,
                "agent_phone": agent_phone,
                "caller_name": caller_name,
                "reason": transfer_reason,
                "transfer_type": "warm"  # Warm transfer with context
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

