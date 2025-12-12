"""
Vapi.ai webhook handlers
Handles events from Vapi including call status updates, transcripts, etc.
"""

from fastapi import APIRouter, Request, HTTPException
from typing import Dict, Any
from src.models.vapi_models import VapiWebhookEvent
from src.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post("/events")
async def handle_vapi_webhook(request: Request) -> Dict[str, Any]:
    """
    Handle incoming webhooks from Vapi
    
    Event types:
    - assistant-request: When assistant needs to make a function call
    - status-update: Call status changes
    - transcript: Call transcription updates
    - end-of-call-report: Final call summary
    """
    try:
        payload = await request.json()
        event_type = payload.get("type")
        
        logger.info(f"Received Vapi webhook: {event_type}")
        logger.debug(f"Webhook payload: {payload}")
        
        # Handle different event types
        if event_type == "assistant-request":
            return await handle_assistant_request(payload)
        
        elif event_type == "status-update":
            return await handle_status_update(payload)
        
        elif event_type == "transcript":
            return await handle_transcript(payload)
        
        elif event_type == "end-of-call-report":
            return await handle_end_of_call(payload)
        
        elif event_type == "function-call":
            # Function calls are handled by individual function endpoints
            logger.info("Function call event received (handled by function endpoints)")
            return {"status": "acknowledged"}
        
        else:
            logger.warning(f"Unknown Vapi event type: {event_type}")
            return {"status": "unknown_event_type", "type": event_type}
        
    except Exception as e:
        logger.exception(f"Error handling Vapi webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def handle_assistant_request(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Handle assistant request events"""
    logger.info("Processing assistant request")
    
    # Extract relevant information
    call_id = payload.get("call", {}).get("id")
    message = payload.get("message", {})
    
    # Log for monitoring
    logger.debug(f"Assistant request for call {call_id}: {message}")
    
    return {"status": "processed"}


async def handle_status_update(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Handle call status update events"""
    status = payload.get("status")
    call_id = payload.get("call", {}).get("id")
    
    logger.info(f"Call {call_id} status update: {status}")
    
    # You can add logic here to:
    # - Update CRM with call status
    # - Notify agents
    # - Track call metrics
    
    return {"status": "processed"}


async def handle_transcript(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Handle transcript update events"""
    call_id = payload.get("call", {}).get("id")
    transcript_text = payload.get("transcript", {}).get("text", "")
    
    logger.debug(f"Transcript update for call {call_id}: {transcript_text[:100]}...")
    
    # You can add logic here to:
    # - Store transcripts in database
    # - Analyze sentiment
    # - Extract key information
    
    return {"status": "processed"}


async def handle_end_of_call(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Handle end of call report events"""
    call_id = payload.get("call", {}).get("id")
    duration = payload.get("call", {}).get("duration")
    end_reason = payload.get("endReason")
    
    logger.info(f"Call {call_id} ended: duration={duration}s, reason={end_reason}")
    
    # Extract call summary
    summary = payload.get("summary", {})
    transcript = payload.get("transcript", "")
    
    # You can add logic here to:
    # - Save call recording URL
    # - Store full transcript
    # - Update CRM with call notes
    # - Generate follow-up tasks
    # - Calculate call analytics
    
    logger.debug(f"Call summary: {summary}")
    
    return {
        "status": "processed",
        "call_id": call_id,
        "duration": duration
    }


@router.get("/health")
async def vapi_webhook_health() -> Dict[str, str]:
    """Health check endpoint for Vapi webhooks"""
    return {"status": "healthy", "service": "vapi_webhooks"}

