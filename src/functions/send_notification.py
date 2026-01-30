"""
Function: Send Notification
Sends SMS/email notifications to contacts
"""

from fastapi import APIRouter
from typing import Dict, Any
from src.models.vapi_models import VapiResponse, SendNotificationRequest
from src.integrations.twilio_client import TwilioClient
from src.integrations.email_client import EmailClient
from src.config.settings import settings
from src.utils.logger import get_logger
from src.utils.errors import TwilioError, EmailError
from src.utils.validators import validate_phone, validate_email

logger = get_logger(__name__)
router = APIRouter()


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
        # Normalize notification_type (default to "sms" if not provided)
        notification_type = (request.notification_type or "sms").lower()
        logger.info(f"Sending {notification_type} notification to: {request.recipient_phone}")
        
        # Validate phone
        try:
            phone = validate_phone(request.recipient_phone)
        except Exception as e:
            logger.warning(f"Phone validation failed: {str(e)}")
            phone = request.recipient_phone
        
        # TEST MODE: Override recipient with test number
        if settings.TEST_MODE:
            original_phone = phone
            phone = settings.TEST_AGENT_PHONE
            logger.info(f"TEST MODE: Overriding notification recipient from {original_phone} to {phone}")
        
        sent_channels = []
        errors = []
        
        # Send SMS
        if notification_type in ["sms", "both"]:
            try:
                # Initialize Twilio client (lazy initialization)
                twilio_client = TwilioClient()
                sms_result = await twilio_client.send_sms(
                    to_number=phone,
                    message=request.message
                )
                sent_channels.append("sms")
                logger.info(f"SMS sent successfully: {sms_result.get('sid')}")
            except TwilioError as e:
                error_msg = getattr(e, 'message', str(e))
                logger.error(f"Failed to send SMS: {error_msg}")
                errors.append(f"SMS: {error_msg}")
            except Exception as e:
                error_msg = str(e)
                logger.exception(f"Unexpected error sending SMS: {error_msg}")
                errors.append(f"SMS: {error_msg}")
        
        # Send email whenever we have recipient_email (always send with SMS per requirement)
        if request.recipient_email and notification_type in ["sms", "email", "both"]:
            try:
                email = validate_email(request.recipient_email)

                email_client = EmailClient()
                if not email_client.is_configured:
                    logger.warning("SMTP not configured - skipping email notification")
                    errors.append("Email: SMTP not configured")
                else:
                    subject = f"Notification from {settings.BUSINESS_NAME}"
                    await email_client.send_email(
                        to_email=email,
                        subject=subject,
                        body=request.message,
                        html_body=f"<p>{request.message}</p>",
                    )
                    sent_channels.append("email")
                    logger.info(f"Email sent successfully to {email}")
            except EmailError as e:
                error_msg = getattr(e, "message", str(e))
                logger.error(f"Failed to send email: {error_msg}")
                errors.append(f"Email: {error_msg}")
            except Exception as e:
                logger.exception(f"Unexpected error sending email: {str(e)}")
                errors.append(f"Email: {str(e)}")
        
        # Check if at least one channel succeeded
        if not sent_channels:
            if not errors:
                # No channels attempted and no errors - invalid notification_type
                error_msg = f"Invalid notification_type '{notification_type}'. Must be 'sms', 'email', or 'both'."
                logger.error(error_msg)
            else:
                error_msg = "; ".join(errors)
            
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
                "notification_type": notification_type,
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

