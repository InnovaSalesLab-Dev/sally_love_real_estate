"""
GoHighLevel (GHL) webhook handlers
Handles inbound call events from GHL and triggers Vapi voice agent
"""

from fastapi import APIRouter, Request, HTTPException, Header
from typing import Dict, Any, Optional
from src.utils.logger import get_logger
from src.integrations.vapi_client import VapiClient
from src.config.settings import settings
import hmac
import hashlib

logger = get_logger(__name__)
router = APIRouter()

vapi_client = VapiClient()


def verify_ghl_signature(payload: bytes, signature: str, secret: str) -> bool:
    """
    Verify GHL webhook signature for security
    
    Args:
        payload: Raw request body
        signature: Signature from GHL header
        secret: Your GHL webhook secret
        
    Returns:
        True if signature is valid
    """
    if not secret or not signature:
        return False
    
    expected_signature = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)


@router.post("/form-submission")
async def handle_ghl_form_submission(
    request: Request,
    x_ghl_signature: Optional[str] = Header(None)
) -> Dict[str, Any]:
    """
    Handle form submission webhook from GoHighLevel
    
    When a user submits a form in GHL (e.g., property inquiry form):
    1. GHL sends form submission data to this webhook
    2. We extract the user's phone number and form data
    3. We trigger Vapi to make an OUTBOUND call to the user
    4. Vapi AI calls the user back and handles the conversation
    
    GHL Form Submission Payload Example:
    {
        "type": "FormSubmit",
        "locationId": "xxx",
        "contactId": "xxx",
        "submittedAt": "2025-12-22T10:30:00Z",
        "contact": {
            "id": "xxx",
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "+13525551234"
        },
        "formData": {
            "name": "John Doe",
            "phone": "+13525551234",
            "email": "john@example.com",
            "property_interest": "1738 Augustine Drive",
            "budget": "$500k-$750k",
            "timeframe": "1-3 months"
        }
    }
    """
    try:
        # Get raw body for signature verification
        body = await request.body()
        payload = await request.json()
        
        logger.info(f"Received GHL inbound call webhook")
        logger.debug(f"Payload: {payload}")
        
        # Signature verification disabled (GHL_WEBHOOK_SECRET not configured)
        logger.debug("Skipping signature verification")
        
        # Extract form submission details
        form_type = payload.get("type")
        contact_id = payload.get("contactId")
        location_id = payload.get("locationId")
        submitted_at = payload.get("submittedAt")
        
        # Extract contact details
        contact = payload.get("contact", {})
        contact_name = contact.get("name", "Unknown")
        contact_email = contact.get("email")
        contact_phone = contact.get("phone")
        
        # Extract form data
        form_data = payload.get("formData", {})
        
        # Get phone number (try multiple sources)
        user_phone = (
            contact_phone or 
            form_data.get("phone") or 
            payload.get("phone")
        )
        
        # Validate required fields
        if not user_phone:
            logger.error("Missing phone number in GHL form submission")
            raise HTTPException(status_code=400, detail="Missing phone number in form submission")
        
        logger.info(f"Form submitted by {contact_name} ({user_phone})")
        logger.info(f"Form data: {form_data}")
        
        # Trigger Vapi to make an OUTBOUND call to the user
        try:
            vapi_response = await vapi_client.create_outbound_call(
                phone_number=user_phone,
                assistant_id=settings.VAPI_ASSISTANT_ID,
                customer_name=contact_name,
                customer_email=contact_email,
                metadata={
                    "source": "ghl_form_submission",
                    "ghl_contact_id": contact_id,
                    "ghl_location_id": location_id,
                    "submitted_at": submitted_at,
                    "form_data": form_data,
                    "call_type": "outbound",
                    "trigger": "form_submission"
                }
            )
            vapi_call_id = vapi_response.get("id")
            
            logger.info(f"Successfully triggered Vapi outbound call: {vapi_call_id}")
            logger.info(f"Vapi will call {user_phone} in a few seconds")
            
            return {
                "status": "success",
                "message": "Outbound call initiated - user will receive a call shortly",
                "ghl_contact_id": contact_id,
                "vapi_call_id": vapi_call_id,
                "user": {
                    "phone": user_phone,
                    "name": contact_name,
                    "email": contact_email
                },
                "form_data": form_data
            }
            
        except Exception as vapi_error:
            logger.error(f"Failed to trigger Vapi call: {str(vapi_error)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to trigger Vapi agent: {str(vapi_error)}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error handling GHL inbound call webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/call-status")
async def handle_ghl_call_status(
    request: Request,
    x_ghl_signature: Optional[str] = Header(None)
) -> Dict[str, Any]:
    """
    Handle call status updates from GoHighLevel
    
    This endpoint receives call status updates (answered, completed, failed, etc.)
    
    GHL Payload Example:
    {
        "type": "CallStatus",
        "callId": "xxx",
        "status": "completed",
        "duration": 120,
        "recordingUrl": "https://..."
    }
    """
    try:
        body = await request.body()
        payload = await request.json()
        
        logger.info(f"Received GHL call status update")
        logger.debug(f"Payload: {payload}")
        
        # Signature verification disabled (GHL_WEBHOOK_SECRET not configured)
        logger.debug("Skipping signature verification")
        
        call_id = payload.get("callId")
        status = payload.get("status")
        duration = payload.get("duration")
        recording_url = payload.get("recordingUrl")
        
        logger.info(f"Call {call_id} status: {status}, duration: {duration}s")
        
        # Log or process call status update
        # You can add logic here to update your CRM, send notifications, etc.
        
        return {
            "status": "acknowledged",
            "call_id": call_id,
            "call_status": status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error handling GHL call status webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test")
async def handle_ghl_test_webhook(request: Request) -> Dict[str, Any]:
    """
    Test endpoint for GHL webhook configuration
    
    Use this to verify your GHL webhook is configured correctly
    """
    try:
        payload = await request.json()
        
        logger.info("Received GHL test webhook")
        logger.debug(f"Test payload: {payload}")
        
        return {
            "status": "success",
            "message": "GHL webhook test successful",
            "received": payload,
            "webhook_url": str(request.url),
            "timestamp": payload.get("timestamp") if payload else None
        }
        
    except Exception as e:
        logger.exception(f"Error handling GHL test webhook: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }

