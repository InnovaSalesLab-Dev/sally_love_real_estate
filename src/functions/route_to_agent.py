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
from src.integrations.twilio_client import TwilioClient
from src.integrations.email_client import EmailClient
from src.config.settings import settings
from src.utils.logger import get_logger
from src.utils.roster import get_any_agent, get_main_office_phone, is_agent_in_roster

logger = get_logger(__name__)
router = APIRouter()

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
        notification_email = settings.JEFF_NOTIFICATION_EMAIL or settings.OFFICE_NOTIFICATION_EMAIL
        if notification_email:
            try:
                email_client = EmailClient()
                if email_client.is_configured:
                    await email_client.send_email(
                        to_email=notification_email,
                        subject="⚠️ Failed Transfer Alert",
                        body=notification_message,
                        html_body=f"<pre>{notification_message}</pre>",
                    )
                    logger.info(f"Failed transfer notification email sent to: {notification_email}")
            except Exception as e:
                logger.warning(f"Failed to send failed transfer notification email: {str(e)}")
        if not notification_phone:
            logger.warning("No notification phone configured for failed transfer alert")

    except Exception as e:
        logger.warning(f"Failed to send transfer failure notification: {str(e)}")


async def send_no_answer_notification_to_jeff(
    caller_name: Optional[str] = None,
    caller_phone: Optional[str] = None,
    attempted_agent_name: Optional[str] = None,
    attempted_agent_phone: Optional[str] = None,
):
    """
    Send SMS and email to Jeff when a transfer was attempted but no one picked up.
    Called from Vapi webhook when end-of-call or status-update indicates no-answer.
    """
    try:
        if not settings.LEAD_NOTIFICATION_ENABLED:
            return

        notification_message = (
            "⚠️ TRANSFER NO-ANSWER ALERT\n\n"
            f"Attempted transfer to: {attempted_agent_name or 'Unknown'} ({attempted_agent_phone or 'Unknown'})\n"
            f"Caller: {caller_name or 'Unknown'}\n"
            f"Caller phone: {caller_phone or 'Unknown'}\n"
            "\nNo one picked up. Please call the caller back."
        )

        notification_phone = settings.TEST_AGENT_PHONE if settings.TEST_MODE else (
            settings.JEFF_NOTIFICATION_PHONE or settings.OFFICE_NOTIFICATION_PHONE
        )
        if notification_phone:
            await twilio_client.send_sms(notification_phone, notification_message)
            logger.info(f"No-answer notification SMS sent to: {notification_phone}")

        notification_email = settings.JEFF_NOTIFICATION_EMAIL or settings.OFFICE_NOTIFICATION_EMAIL
        if notification_email:
            try:
                email_client = EmailClient()
                if email_client.is_configured:
                    await email_client.send_email(
                        to_email=notification_email,
                        subject="⚠️ Transfer No-Answer Alert",
                        body=notification_message,
                        html_body=f"<pre>{notification_message}</pre>",
                    )
                    logger.info(f"No-answer notification email sent to: {notification_email}")
            except Exception as e:
                logger.warning(f"Failed to send no-answer notification email: {str(e)}")

        if not notification_phone:
            logger.warning("No notification phone configured for no-answer alert")

    except Exception as e:
        logger.warning(f"Failed to send no-answer notification to Jeff: {str(e)}")


@router.post("/route_to_agent")
async def route_to_agent(request: Request) -> Union[Dict[str, Any], VapiResponse]:
    """
    Route/transfer call to a specific agent using Vapi's Live Call Control API.

    This function handles dynamic call transfers by:
    1. Receiving Vapi webhook with controlUrl and function parameters
    2. Validating agent against roster; if not in roster, uses fallback agent
    3. Executing the transfer via POST to controlUrl
    4. Returning success response

    Reference: https://docs.vapi.ai/calls/call-dynamic-transfers
    """
    # Initialize control_url before try block to avoid NameError in exception handlers
    control_url = None
    
    try:
        # Parse the request body - Vapi sends webhook format
        body = await request.json()
        
        # DEBUG: Log the full webhook payload to see what Vapi is sending
        logger.info("="*80)
        logger.info("VAPI WEBHOOK RECEIVED - route_to_agent")
        logger.info("="*80)
        logger.info(f"Full payload: {json.dumps(body, indent=2)}")
        logger.info("="*80)
        
        # Extract control URL from the call monitor (Official Vapi pattern)
        # Reference: https://docs.vapi.ai/calls/call-dynamic-transfers
        message = body.get("message", {})
        control_url = message.get("call", {}).get("monitor", {}).get("controlUrl")
        
        # Extract tool call from toolWithToolCallList (Official Vapi pattern)
        # Bug fix: Check if list has items before accessing [0] to avoid IndexError
        tool_with_tool_call_list = message.get("toolWithToolCallList", [])
        if not tool_with_tool_call_list:
            logger.error("toolWithToolCallList is empty or missing")
            return VapiResponse(
                success=False,
                error="Missing required webhook data",
                message="I'm unable to transfer the call right now. Let me take your information and have an agent call you back.",
            )
        
        tool_with_tool_call = tool_with_tool_call_list[0]
        tool_call = tool_with_tool_call.get("toolCall", {})
        
        logger.info(f"controlUrl present: {bool(control_url)}")
        logger.info(f"toolCall present: {bool(tool_call)}")
        
        if not control_url or not tool_call:
            logger.error("Missing required data - controlUrl or toolCall not found")
            logger.error("This usually means the tool was not created with async: true")
            return VapiResponse(
                success=False,
                error="Missing required webhook data",
                message="I'm unable to transfer the call right now. Let me take your information and have an agent call you back.",
            )
        
        # Extract parameters from the tool call
        arguments = tool_call.get("function", {}).get("arguments", {})
        
        # Handle both string (JSON) and dict arguments
        if isinstance(arguments, str):
            try:
                arguments = json.loads(arguments)
            except json.JSONDecodeError:
                logger.error(f"Failed to parse arguments JSON: {arguments}")
                arguments = {}
        
        agent_name = arguments.get("agent_name", "")
        agent_phone = arguments.get("agent_phone", "")
        caller_name = arguments.get("caller_name")
        caller_phone = arguments.get("caller_phone")
        lead_id = arguments.get("lead_id")
        reason = arguments.get("reason")

        roster_path = settings.AGENT_ROSTER_PATH or None

        # Roster validation: if agent not in roster, use fallback
        if not is_agent_in_roster(agent_name, agent_phone, roster_path):
            fallback = get_any_agent(roster_path)
            if fallback:
                original = f"{agent_name} ({agent_phone})" if agent_name or agent_phone else "requested agent"
                agent_name = fallback.get("name") or "an agent"
                agent_phone = fallback.get("cell_phone") or fallback.get("phone") or ""
                logger.info(f"Agent {original} not in roster; using fallback agent {agent_name}")
            else:
                main_office = get_main_office_phone(roster_path)
                if main_office:
                    agent_name = "our office"
                    agent_phone = main_office
                    logger.info(f"No roster agents available; using main office: {main_office}")

        logger.info(f"Routing call to agent: {agent_name} ({agent_phone})")

        # Enforce Lead-Before-Transfer: do not transfer unless we have a CRM contact/lead id
        # and basic caller contact info for agent context.
        if not lead_id or not caller_name or not caller_phone:
            logger.warning(
                "Transfer gate blocked: missing lead_id and/or caller contact info "
                f"(lead_id={bool(lead_id)}, caller_name={bool(caller_name)}, caller_phone={bool(caller_phone)})"
            )
            return VapiResponse(
                success=False,
                error="Missing required lead/contact information",
                message=(
                    "Before I connect you, can I get your name and the best callback number? "
                    "That way the agent has your details in case they miss you."
                ),
            )

        if not agent_phone:
            return VapiResponse(
                success=False,
                error="Agent phone number is required",
                message="I'm unable to transfer the call - agent phone number is missing. Let me take your information and have an agent call you back.",
            )

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
        
        # Execute transfer via Live Call Control (Official Vapi Pattern)
        # Reference: https://docs.vapi.ai/calls/call-dynamic-transfers
        logger.info(f"Executing transfer to {agent_name} at {agent_phone}")
        
        destination = {
            "type": "number",
            "number": agent_phone
        }
        
        # POST to controlUrl/control to execute the transfer
        # Official Vapi docs: POST to controlUrl/control
        control_endpoint = f"{control_url.rstrip('/')}/control"
        async with httpx.AsyncClient(timeout=10.0) as client:
            transfer_response = await client.post(
                control_endpoint,
                json={
                    "type": "transfer",
                    "destination": destination,
                    "content": transfer_message
                },
                headers={"Content-Type": "application/json"}
            )
            
            if transfer_response.status_code == 200:
                logger.info(f"✅ Transfer executed successfully to {agent_name} ({agent_phone})")
                return VapiResponse(
                    success=True,
                    message=f"Transfer to {agent_name} initiated successfully"
                )
            else:
                logger.error(f"❌ Transfer failed. Status: {transfer_response.status_code}, Response: {transfer_response.text}")
                raise Exception(f"Transfer API returned {transfer_response.status_code}")
        
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
        
        # Try fallback to Jeff/office line
        fallback_phone = (
            settings.TEST_AGENT_PHONE
            if settings.TEST_MODE
            else (settings.JEFF_NOTIFICATION_PHONE or settings.OFFICE_NOTIFICATION_PHONE)
        )
        if fallback_phone and control_url:
            logger.info(f"Attempting fallback transfer to office line: {fallback_phone}")
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    transfer_payload = {
                        "type": "transfer",
                        "destination": {
                            "type": "number",
                            "number": fallback_phone
                        },
                        "content": "I'm connecting you to our office now. Please hold."
                    }
                    # Official Vapi docs: POST to controlUrl/control
                    control_endpoint = f"{control_url.rstrip('/')}/control"
                    response = await client.post(control_endpoint, json=transfer_payload)
                    if response.status_code == 200:
                        logger.info(f"✅ Fallback transfer executed to {fallback_phone}")
                        return VapiResponse(success=True, message="Fallback transfer initiated")
            except Exception as e:
                logger.error(f"Fallback transfer failed: {str(e)}")
        
        # Handle Twilio errors that might be in other languages or configuration issues
        error_str = str(e)
        is_config_error = (
            "not set up" in error_str.lower() or 
            "forwarding" in error_str.lower() or
            any(ord(char) > 127 for char in error_str)  # Check for non-ASCII (likely other language)
        )
        
        if is_config_error:
            logger.error(f"Transfer failed - phone number configuration issue: {error_str}")
            return VapiResponse(
                success=False,
                error="Phone number configuration error",
                message=(
                    "I'm unable to connect you directly right now due to a phone configuration issue. "
                    "Let me have an agent call you back at the number you provided."
                ),
            )
        
        return VapiResponse(
            success=False,
            error=f"Transfer failed: {str(e)}",
            message="I'm having trouble connecting you right now. An agent will call you back shortly.",
        )

