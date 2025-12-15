"""
Function: Route to Agent
Transfers call to a specific real estate agent using Vapi's Live Call Control API

Reference: https://docs.vapi.ai/calls/call-dynamic-transfers
"""

from fastapi import APIRouter, Request
from typing import Dict, Any, Optional
import httpx
import json
from src.models.vapi_models import VapiResponse
from src.integrations.boldtrail import BoldTrailClient
from src.utils.logger import get_logger
from src.utils.errors import BoldTrailError

logger = get_logger(__name__)
router = APIRouter()

crm_client = BoldTrailClient()


@router.post("/route_to_agent")
async def route_to_agent(request: Request) -> VapiResponse:
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
                import json
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
        
        logger.info(f"Routing call to agent: {agent_name} ({agent_phone}), controlUrl: {control_url}")
        
        if not control_url:
            logger.warning("No controlUrl provided - transfer cannot be executed via Live Call Control")
            # Return data-only response if no controlUrl (for testing or non-transfer scenarios)
            return VapiResponse(
                success=False,
                error="Transfer control URL not available",
                message="I'm unable to transfer the call right now. Let me take your information and have an agent call you back.",
                data={
                    "agent_id": agent_id,
                    "agent_name": agent_name,
                    "agent_phone": agent_phone,
                    "note": "controlUrl not available in request"
                }
            )
        
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
        
        # Prepare transfer message
        transfer_reason = reason or "general inquiry"
        caller_name = caller_name or "a caller"
        transfer_message = f"Transferring you to {agent_name} now. Please hold."
        
        # Execute transfer via Vapi Live Call Control API
        # Reference: https://docs.vapi.ai/calls/call-dynamic-transfers
        transfer_payload = {
            "type": "transfer",
            "destination": {
                "type": "number",
                "number": agent_phone
            },
            "content": transfer_message
        }
        
        logger.info(f"Executing transfer to {agent_phone} via {control_url}/control")
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                transfer_response = await client.post(
                    f"{control_url}/control",
                    json=transfer_payload,
                    headers={"Content-Type": "application/json"}
                )
                transfer_response.raise_for_status()
                logger.info(f"Transfer executed successfully: {transfer_response.status_code}")
        except httpx.HTTPError as e:
            logger.error(f"Failed to execute transfer via controlUrl: {str(e)}")
            return VapiResponse(
                success=False,
                error=f"Transfer execution failed: {str(e)}",
                message="I'm having trouble connecting you right now. Let me take your information and have the agent call you back shortly.",
                data={
                    "agent_phone": agent_phone,
                    "agent_name": agent_name
                }
            )
        
        # Return success response
        return VapiResponse(
            success=True,
            message=f"Great! I'm transferring you to {agent_name} now. They'll be able to help you with your {transfer_reason}. Please hold while I connect you.",
            data={
                "agent_id": agent_id,
                "agent_name": agent_name,
                "agent_phone": agent_phone,
                "caller_name": caller_name,
                "reason": transfer_reason,
                "transfer_type": "warm",
                "verified_in_crm": bool(agent_data),
                "transfer_executed": True
            }
        )
        
    except BoldTrailError as e:
        logger.error(f"BoldTrail error in route_to_agent: {e.message}")
        # If we have controlUrl, still try to transfer with provided phone
        try:
            body = await request.json()
            message = body.get("message", {})
            call = message.get("call", {})
            monitor = call.get("monitor", {})
            control_url = monitor.get("controlUrl")
            
            # Try to get phone from request
            tool_with_tool_call_list = message.get("toolWithToolCallList", [])
            if tool_with_tool_call_list:
                tool_call = tool_with_tool_call_list[0].get("toolCall", {})
                arguments = tool_call.get("function", {}).get("arguments", {})
                if isinstance(arguments, str):
                    arguments = json.loads(arguments)
                agent_phone = arguments.get("agent_phone", "")
                agent_name = arguments.get("agent_name", "an agent")
            else:
                params = body.get("parameters", body)
                agent_phone = params.get("agent_phone", "")
                agent_name = params.get("agent_name", "an agent")
            
            if control_url and agent_phone:
                # Format phone
                if not agent_phone.startswith("+"):
                    cleaned_phone = ''.join(filter(str.isdigit, agent_phone))
                    agent_phone = f"+1{cleaned_phone}" if len(cleaned_phone) == 10 else f"+{cleaned_phone}"
                
                # Execute transfer despite CRM error
                transfer_payload = {
                    "type": "transfer",
                    "destination": {"type": "number", "number": agent_phone},
                    "content": f"Transferring you to {agent_name} now. Please hold."
                }
                
                async with httpx.AsyncClient(timeout=10.0) as client:
                    await client.post(f"{control_url}/control", json=transfer_payload)
                
                return VapiResponse(
                    success=True,
                    message=f"I'll connect you to {agent_name} now. Please hold while I transfer your call.",
                    data={
                        "agent_name": agent_name,
                        "agent_phone": agent_phone,
                        "verified_in_crm": False,
                        "note": "CRM verification failed but transfer executed"
                    }
                )
        except Exception as transfer_error:
            logger.error(f"Transfer execution also failed: {str(transfer_error)}")
        
        return VapiResponse(
            success=False,
            error="CRM verification failed",
            message="I'm having trouble verifying the agent right now. Let me take your information and have someone call you back shortly.",
        )
    
    except Exception as e:
        logger.exception(f"Error in route_to_agent: {str(e)}")
        return VapiResponse(
            success=False,
            error=f"Transfer failed: {str(e)}",
            message="I'm having trouble connecting you right now. Let me take your information and have an agent call you back shortly.",
        )


# ============================================================================
# TEST ENDPOINT - REMOVE BEFORE PRODUCTION
# ============================================================================
# This endpoint simulates a Vapi webhook call for testing route_to_agent
# Uses test agent information (Hammas Ali) instead of real agents
# DELETE THIS ENTIRE SECTION BEFORE GOING TO PRODUCTION
# ============================================================================

@router.post("/test_route_to_agent")
async def test_route_to_agent(request: Request) -> VapiResponse:
    """
    TEST ENDPOINT - Simulates route_to_agent with test data
    
    ⚠️ REMOVE THIS ENDPOINT BEFORE PRODUCTION ⚠️
    
    This endpoint creates a mock Vapi webhook payload for testing transfers.
    Uses test agent information (Hammas Ali) instead of real agents.
    
    Test Agent Info:
    - Name: Hammas Ali
    - Phone: +923035699010
    
    To test:
    POST /functions/test_route_to_agent
    Body: {
        "test_agent_name": "Test Agent Name",  // Optional, defaults to "Hammas Ali"
        "test_agent_phone": "+1234567890",     // Optional, defaults to "+923035699010"
        "caller_name": "Test Caller",          // Optional
        "reason": "test transfer"              // Optional
    }
    """
    try:
        body = await request.json()
        
        # Test agent information (Hammas Ali - for testing only)
        TEST_AGENT_ID = "TEST_AGENT_001"
        TEST_AGENT_NAME = body.get("test_agent_name", "Hammas Ali")
        TEST_AGENT_PHONE = body.get("test_agent_phone", "+923035699010")
        TEST_CALLER_NAME = body.get("caller_name", "Test Caller")
        TEST_REASON = body.get("reason", "test transfer")
        
        # Simulate Vapi webhook format
        # Note: In real scenario, controlUrl comes from Vapi
        # For testing, we'll create a mock controlUrl or skip actual transfer
        MOCK_CONTROL_URL = body.get("mock_control_url")  # Optional: provide mock URL for testing
        
        logger.info(f"🧪 TEST MODE: Routing to test agent {TEST_AGENT_NAME} ({TEST_AGENT_PHONE})")
        logger.warning("⚠️  This is a TEST endpoint using test agent information!")
        
        # Format phone number
        agent_phone = TEST_AGENT_PHONE
        if not agent_phone.startswith("+"):
            cleaned_phone = ''.join(filter(str.isdigit, agent_phone))
            agent_phone = f"+1{cleaned_phone}" if len(cleaned_phone) == 10 else f"+{cleaned_phone}"
        
        # If mock_control_url provided, attempt actual transfer (for integration testing)
        if MOCK_CONTROL_URL:
            logger.info(f"🧪 TEST: Attempting transfer via mock controlUrl: {MOCK_CONTROL_URL}")
            
            transfer_payload = {
                "type": "transfer",
                "destination": {
                    "type": "number",
                    "number": agent_phone
                },
                "content": f"Transferring you to {TEST_AGENT_NAME} now. Please hold."
            }
            
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    transfer_response = await client.post(
                        f"{MOCK_CONTROL_URL}/control",
                        json=transfer_payload,
                        headers={"Content-Type": "application/json"}
                    )
                    transfer_response.raise_for_status()
                    logger.info(f"🧪 TEST: Transfer executed successfully: {transfer_response.status_code}")
            except httpx.HTTPError as e:
                logger.warning(f"🧪 TEST: Transfer execution failed (expected in test mode): {str(e)}")
        else:
            logger.info("🧪 TEST: No mock_control_url provided - skipping actual transfer execution")
            logger.info("🧪 TEST: In production, Vapi provides controlUrl automatically")
        
        # Return success response (simulating successful transfer)
        return VapiResponse(
            success=True,
            message=f"🧪 TEST MODE: Transfer to {TEST_AGENT_NAME} would be executed. In production, the call would be transferred to {agent_phone}.",
            data={
                "test_mode": True,
                "agent_id": TEST_AGENT_ID,
                "agent_name": TEST_AGENT_NAME,
                "agent_phone": agent_phone,
                "caller_name": TEST_CALLER_NAME,
                "reason": TEST_REASON,
                "transfer_executed": bool(MOCK_CONTROL_URL),
                "note": "⚠️ TEST ENDPOINT - Remove before production"
            }
        )
        
    except Exception as e:
        logger.exception(f"🧪 TEST: Error in test_route_to_agent: {str(e)}")
        return VapiResponse(
            success=False,
            error=f"Test transfer failed: {str(e)}",
            message="Test transfer encountered an error.",
            data={"test_mode": True}
        )

