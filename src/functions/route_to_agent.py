"""
Function: Route to Agent
Transfers call to a specific real estate agent using Vapi's Live Call Control API

Reference: https://docs.vapi.ai/calls/call-dynamic-transfers
"""

from fastapi import APIRouter, Request
from typing import Dict, Any, Optional, Union
import httpx
import json
from src.models.vapi_models import VapiResponse
from src.integrations.boldtrail import BoldTrailClient
from src.integrations.twilio_client import TwilioClient
from src.config.settings import settings
from src.utils.logger import get_logger
from src.utils.errors import BoldTrailError

logger = get_logger(__name__)
router = APIRouter()

crm_client = BoldTrailClient()
twilio_client = TwilioClient()


async def send_failed_transfer_notification(
    agent_name: str,
    agent_phone: str,
    caller_name: Optional[str] = None,
    reason: Optional[str] = None
):
    """
    Send notification to office/Jeff when a transfer fails
    This helps ensure no calls are lost
    """
    try:
        if not settings.LEAD_NOTIFICATION_ENABLED:
            return
            
        notification_message = (
            f"⚠️ FAILED TRANSFER ALERT\n\n"
            f"Attempted transfer to: {agent_name} ({agent_phone})\n"
            f"Caller: {caller_name or 'Unknown'}\n"
            f"Reason: {reason or 'Not specified'}\n"
            f"\nAction: Please call back ASAP"
        )
        
        # Determine notification recipient (TEST_MODE overrides)
        notification_phone = settings.TEST_AGENT_PHONE if settings.TEST_MODE else (
            settings.JEFF_NOTIFICATION_PHONE or settings.OFFICE_NOTIFICATION_PHONE
        )
        
        if notification_phone:
            await twilio_client.send_sms(notification_phone, notification_message)
            logger.info(f"Failed transfer notification sent to: {notification_phone} (TEST_MODE: {settings.TEST_MODE})")
        else:
            logger.warning("No notification phone configured for failed transfer alert")
            
    except Exception as e:
        logger.warning(f"Failed to send transfer failure notification: {str(e)}")


@router.post("/route_to_agent")
async def route_to_agent(request: Request) -> Union[Dict[str, Any], VapiResponse]:
    """
    Route/transfer call to a specific agent using Vapi's Live Call Control API
    
    This function handles dynamic call transfers by:
    1. Receiving Vapi webhook with controlUrl and function parameters
    2. Verifying agent in BoldTrail CRM
    3. Executing the transfer via POST to controlUrl
    4. Returning success response
    
    Reference: https://docs.vapi.ai/calls/call-dynamic-transfers
    """
    try:
        # Parse the request body - Vapi sends webhook format
        body = await request.json()
        
        # DEBUG: Log the full webhook payload to see what Vapi is sending
        logger.info("="*80)
        logger.info("VAPI WEBHOOK RECEIVED - route_to_agent")
        logger.info("="*80)
        logger.info(f"Full payload: {json.dumps(body, indent=2)}")
        logger.info("="*80)
        
        # Extract control URL from Vapi webhook format
        # Format: message.call.monitor.controlUrl
        message = body.get("message", {})
        call = message.get("call", {})
        monitor = call.get("monitor", {})
        control_url = monitor.get("controlUrl")
        
        # Extract tool call parameters
        # Format: message.toolWithToolCallList[0].toolCall.function.arguments
        tool_with_tool_call_list = message.get("toolWithToolCallList", [])
        
        if not tool_with_tool_call_list:
            # Fallback: Try direct parameters (backward compatibility)
            params = body.get("parameters", body)
            agent_id = params.get("agent_id", "")
            agent_name = params.get("agent_name", "")
            agent_phone = params.get("agent_phone", "")
            caller_name = params.get("caller_name")
            reason = params.get("reason")
        else:
            # Extract from tool call arguments
            tool_call = tool_with_tool_call_list[0].get("toolCall", {})
            arguments = tool_call.get("function", {}).get("arguments", {})
            
            # Handle both string (JSON) and dict arguments
            if isinstance(arguments, str):
                try:
                    arguments = json.loads(arguments)
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse arguments JSON: {arguments}")
                    arguments = {}
            
            agent_id = arguments.get("agent_id", "")
            agent_name = arguments.get("agent_name", "")
            agent_phone = arguments.get("agent_phone", "")
            caller_name = arguments.get("caller_name")
            reason = arguments.get("reason")
        
        logger.info(f"Routing call to agent: {agent_name} ({agent_phone})")
        logger.info(f"controlUrl present: {bool(control_url)}")
        
        if not agent_phone:
            return VapiResponse(
                success=False,
                error="Agent phone number is required",
                message="I'm unable to transfer the call - agent phone number is missing. Let me take your information and have an agent call you back.",
            )
        
        # Get agent details from BoldTrail to verify they exist and get phone if missing
        agent_data = None
        if agent_id:
            try:
                agent_data = await crm_client.get_agent(agent_id)
                logger.info(f"Agent verified in BoldTrail: {agent_data.get('id')}")
                
                # Use agent phone from BoldTrail if available and not provided
                if not agent_phone and agent_data.get('phone'):
                    agent_phone = agent_data.get('phone')
                    logger.info(f"Using phone from BoldTrail: {agent_phone}")
            except BoldTrailError as e:
                logger.warning(f"Could not verify agent in BoldTrail: {str(e)}")
        
        # Use agent phone from BoldTrail if available and provided phone is invalid
        if agent_data and agent_data.get('phone') and not agent_phone:
            agent_phone = agent_data.get('phone')
            logger.info(f"Using phone from BoldTrail: {agent_phone}")
        
        # Use agent name from BoldTrail if available
        if agent_data:
            first_name = agent_data.get('firstName', '')
            last_name = agent_data.get('lastName', '')
            if first_name and last_name:
                agent_name = f"{first_name} {last_name}"
        
        # Validate and format phone number (E.164 format required)
        if not agent_phone.startswith("+"):
            # Remove all non-digit characters and add +1 prefix
            cleaned_phone = ''.join(filter(str.isdigit, agent_phone))
            if len(cleaned_phone) == 10:
                agent_phone = f"+1{cleaned_phone}"
            elif len(cleaned_phone) == 11 and cleaned_phone.startswith('1'):
                agent_phone = f"+{cleaned_phone}"
            else:
                logger.warning(f"Unexpected phone format: {agent_phone}, using as-is")
                agent_phone = f"+1{cleaned_phone}"
        
        # TEST MODE: Override with test number if enabled via TEST_MODE environment variable
        if settings.TEST_MODE:
            original_agent = agent_name
            original_phone = agent_phone
            agent_name = settings.TEST_AGENT_NAME
            agent_phone = settings.TEST_AGENT_PHONE
            logger.info(f"TEST MODE: Overriding transfer from {original_agent} ({original_phone}) to {agent_name} ({agent_phone})")
        
        # Prepare transfer message
        transfer_reason = reason or "general inquiry"
        caller_name_display = caller_name or "a caller"
        transfer_message = f"Transferring you to {agent_name} now. Please hold."
        
        # Return transfer instruction - Vapi handles the actual transfer
        # Reference: https://docs.vapi.ai/calls/call-dynamic-transfers
        # IMPORTANT: Vapi expects destination at ROOT LEVEL, not nested in data.transfer
        logger.info(f"Returning transfer instruction for {agent_name} at {agent_phone}")
        
        # Return dict with destination at root level (Vapi's expected format)
        return {
            "destination": {
                "type": "number",
                "number": agent_phone,
                "message": transfer_message
            }
        }
        
    except BoldTrailError as e:
        logger.error(f"BoldTrail error in route_to_agent: {e.message}")
        # Still attempt transfer with provided phone even if CRM verification fails
        try:
            body = await request.json()
            message = body.get("message", {})
            
            # Try to get phone from request
            tool_with_tool_call_list = message.get("toolWithToolCallList", [])
            if tool_with_tool_call_list:
                tool_call = tool_with_tool_call_list[0].get("toolCall", {})
                arguments = tool_call.get("function", {}).get("arguments", {})
                if isinstance(arguments, str):
                    arguments = json.loads(arguments)
                agent_phone = arguments.get("agent_phone", "")
                agent_name = arguments.get("agent_name", "an agent")
                caller_name = arguments.get("caller_name")
                reason = arguments.get("reason")
            else:
                params = body.get("parameters", body)
                agent_phone = params.get("agent_phone", "")
                agent_name = params.get("agent_name", "an agent")
                caller_name = params.get("caller_name")
                reason = params.get("reason")
            
            if agent_phone:
                # Format phone
                if not agent_phone.startswith("+"):
                    cleaned_phone = ''.join(filter(str.isdigit, agent_phone))
                    agent_phone = f"+1{cleaned_phone}" if len(cleaned_phone) == 10 else f"+{cleaned_phone}"
                
                # Return transfer instruction despite CRM error (destination at root level)
                return {
                    "destination": {
                        "type": "number",
                        "number": agent_phone,
                        "message": f"Transferring you to {agent_name} now."
                    }
                }
        except Exception as transfer_error:
            logger.error(f"Transfer preparation also failed: {str(transfer_error)}")
        
        # Send notification about failed transfer
        await send_failed_transfer_notification(
            agent_name=agent_name if 'agent_name' in locals() else "Unknown Agent",
            agent_phone=agent_phone if 'agent_phone' in locals() else "Unknown",
            caller_name=caller_name if 'caller_name' in locals() else None,
            reason=reason if 'reason' in locals() else "CRM verification failed"
        )
        
        # Try fallback to office line
        fallback_phone = settings.TEST_AGENT_PHONE if settings.TEST_MODE else settings.OFFICE_NOTIFICATION_PHONE
        if fallback_phone:
            logger.info(f"Attempting fallback transfer to office line: {fallback_phone}")
            return {
                "destination": {
                    "type": "number",
                    "number": fallback_phone,
                    "message": "I'm connecting you to our office now. Please hold."
                }
            }
        
        return VapiResponse(
            success=False,
            error="CRM verification failed",
            message="I'm having trouble verifying the agent right now. Let me take your information and have someone call you back shortly.",
        )
    
    except Exception as e:
        logger.exception(f"Error in route_to_agent: {str(e)}")
        
        # Send notification about failed transfer
        try:
            body = await request.json()
            message = body.get("message", {})
            tool_with_tool_call_list = message.get("toolWithToolCallList", [])
            
            if tool_with_tool_call_list:
                tool_call = tool_with_tool_call_list[0].get("toolCall", {})
                arguments = tool_call.get("function", {}).get("arguments", {})
                if isinstance(arguments, str):
                    arguments = json.loads(arguments)
                agent_name = arguments.get("agent_name", "Unknown")
                agent_phone = arguments.get("agent_phone", "Unknown")
                caller_name = arguments.get("caller_name")
                reason = arguments.get("reason")
            else:
                params = body.get("parameters", body)
                agent_name = params.get("agent_name", "Unknown")
                agent_phone = params.get("agent_phone", "Unknown")
                caller_name = params.get("caller_name")
                reason = params.get("reason")
            
            await send_failed_transfer_notification(
                agent_name=agent_name,
                agent_phone=agent_phone,
                caller_name=caller_name,
                reason=f"Transfer error: {str(e)}"
            )
        except Exception as notification_error:
            logger.error(f"Failed to send notification about transfer failure: {str(notification_error)}")
        
        # Try fallback to office line
        fallback_phone = settings.TEST_AGENT_PHONE if settings.TEST_MODE else settings.OFFICE_NOTIFICATION_PHONE
        if fallback_phone:
            logger.info(f"Attempting fallback transfer to office line: {fallback_phone}")
            return {
                "destination": {
                    "type": "number",
                    "number": fallback_phone,
                    "message": "I'm connecting you to our office now. Please hold."
                }
            }
        
        return VapiResponse(
            success=False,
            error=f"Transfer failed: {str(e)}",
            message="I'm having trouble connecting you right now. Let me take your information and have an agent call you back shortly.",
        )

