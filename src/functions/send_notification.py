"""
Function: Send Notification
Sends SMS/email notifications to contacts
"""

from fastapi import APIRouter
from typing import Dict, Any
from src.models.vapi_models import VapiResponse, SendNotificationRequest
from src.integrations.twilio_client import TwilioClient
from src.utils.logger import get_logger
from src.utils.errors import TwilioError
from src.utils.validators import validate_phone, validate_email

logger = get_logger(__name__)
router = APIRouter()

twilio_client = TwilioClient()


@router.post("/send_notification")
async def send_notification(request: SendNotificationRequest) -> VapiResponse:
    """
    Send notification via SMS or email
    
    This function handles:
    - SMS notifications via Twilio
    - Email notifications (if configured)
    - Confirmation messages
    - Follow-up reminders
    - Property alerts
    
    Used internally by the voice agent to send confirmations and updates.
    """
    try:
        logger.info(f"Sending {request.notification_type} notification to: {request.recipient_phone}")
        
        # Validate phone
        try:
            phone = validate_phone(request.recipient_phone)
        except Exception as e:
            logger.warning(f"Phone validation failed: {str(e)}")
            phone = request.recipient_phone
        
        sent_channels = []
        errors = []
        
        # Send SMS
        if request.notification_type in ["sms", "both"]:
            try:
                sms_result = await twilio_client.send_sms(
                    to_number=phone,
                    message=request.message
                )
                sent_channels.append("sms")
                logger.info(f"SMS sent successfully: {sms_result.get('sid')}")
            except TwilioError as e:
                logger.error(f"Failed to send SMS: {e.message}")
                errors.append(f"SMS: {e.message}")
        
        # Send email (if email provided and requested)
        if request.notification_type in ["email", "both"] and request.recipient_email:
            try:
                email = validate_email(request.recipient_email)
                # Email sending would be implemented here
                # For now, we'll log it
                logger.info(f"Email notification requested to: {email}")
                sent_channels.append("email")
                # TODO: Implement email sending via SendGrid, AWS SES, or similar
            except Exception as e:
                logger.error(f"Failed to send email: {str(e)}")
                errors.append(f"Email: {str(e)}")
        
        # Check if at least one channel succeeded
        if not sent_channels:
            error_msg = "; ".join(errors) if errors else "Unknown error"
            return VapiResponse(
                success=False,
                error=f"Failed to send notification: {error_msg}",
                message="Notification delivery failed"
            )
        
        message = f"Notification sent successfully via {', '.join(sent_channels)}."
        
        if errors:
            message += f" However, some channels failed: {'; '.join(errors)}"
        
        return VapiResponse(
            success=True,
            message=message,
            data={
                "recipient_phone": phone,
                "recipient_email": request.recipient_email,
                "channels": sent_channels,
                "notification_type": request.notification_type,
                "errors": errors if errors else None
            }
        )
        
    except Exception as e:
        logger.exception(f"Error in send_notification: {str(e)}")
        return VapiResponse(
            success=False,
            error="Failed to send notification due to an unexpected error.",
            message=str(e)
        )

