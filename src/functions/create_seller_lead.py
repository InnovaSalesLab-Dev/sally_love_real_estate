"""
Function: Create Seller Lead
Captures and stores seller lead information in CRM
"""

import asyncio
from fastapi import APIRouter
from typing import Dict, Any, Optional
from src.models.vapi_models import VapiResponse, CreateSellerLeadRequest
from src.models.crm_models import Contact, SellerLead, ContactType, LeadStatus
from src.integrations.boldtrail import BoldTrailClient
from src.integrations.twilio_client import TwilioClient
from src.integrations.email_client import EmailClient
from src.config.settings import settings
from src.utils.logger import get_logger
from src.utils.errors import BoldTrailError
from src.utils.validators import validate_phone, validate_email

logger = get_logger(__name__)
router = APIRouter()

crm_client = BoldTrailClient()
twilio_client = TwilioClient()


async def _handle_seller_lead_background_tasks(
    contact_id: str,
    request: CreateSellerLeadRequest,
    seller_lead: SellerLead,
    phone: str,
    email: Optional[str]
) -> None:
    """
    Handle non-critical background tasks for seller lead creation.
    These run after the API response is returned to reduce latency.
    
    Tasks:
    - Log call activity to CRM
    - Add detailed note
    - Send confirmation SMS to seller
    - Send notification SMS to office
    """
    try:
        # Log call activity to CRM (required for tracking)
        try:
            await crm_client.log_call(
                contact_id=contact_id,
                direction="inbound",
                result=3,  # 3 = Contacted
                notes=f"Initial seller inquiry call for property at {seller_lead.property_address}. Timeline: {seller_lead.timeframe or 'Not specified'}."
            )
            logger.info(f"Call logged successfully for contact: {contact_id}")
        except Exception as e:
            logger.warning(f"Failed to log call activity for contact {contact_id}: {str(e)}")
        
        # Add detailed note with conversation context (required for CRM completeness)
        try:
            note_content = f"Seller Lead from AI Voice Agent\n\n"
            note_content += f"Property Details:\n"
            note_content += f"- Address: {seller_lead.property_address}\n"
            if seller_lead.property_type:
                note_content += f"- Type: {seller_lead.property_type}\n"
            if seller_lead.bedrooms:
                note_content += f"- Bedrooms: {seller_lead.bedrooms}\n"
            if seller_lead.bathrooms:
                note_content += f"- Bathrooms: {seller_lead.bathrooms}\n"
            if seller_lead.square_feet:
                note_content += f"- Square Feet: {seller_lead.square_feet:,}\n"
            if seller_lead.year_built:
                note_content += f"- Year Built: {seller_lead.year_built}\n"
            if seller_lead.condition:
                note_content += f"- Condition: {seller_lead.condition}\n"
            if seller_lead.previously_listed is not None:
                note_content += f"- Previously Listed: {'Yes' if seller_lead.previously_listed else 'No'}\n"
            if seller_lead.currently_occupied is not None:
                note_content += f"- Currently Occupied: {'Yes' if seller_lead.currently_occupied else 'No'}\n"
            if seller_lead.reason_for_selling:
                note_content += f"- Reason for Selling: {seller_lead.reason_for_selling}\n"
            if seller_lead.timeframe:
                note_content += f"- Timeline: {seller_lead.timeframe}\n"
            if seller_lead.estimated_value:
                note_content += f"- Estimated Value: ${seller_lead.estimated_value:,.0f}\n"
            if request.notes:
                note_content += f"\nAdditional Notes:\n{request.notes}"
            
            await crm_client.add_note(
                contact_id=contact_id,
                note=note_content,
                title="AI Concierge - Seller Lead Details"
            )
            logger.info(f"Note added successfully for contact: {contact_id}")
        except Exception as e:
            logger.warning(f"Failed to add note for contact {contact_id}: {str(e)}")
        
        # Send confirmation SMS and email to seller
        try:
            confirmation_message = (
                f"Hi {request.first_name}! Thank you for considering Sally Love Real Estate. "
                f"A listing specialist will contact you shortly to discuss your property at {request.property_address}. "
                f"We look forward to helping you!"
            )
            await twilio_client.send_sms(phone, confirmation_message)
            logger.info(f"Confirmation SMS sent to seller: {phone}")
            if email:
                try:
                    email_client = EmailClient()
                    if not email_client.is_configured:
                        logger.warning(
                            "SMTP not configured - skipping seller confirmation email. "
                            "Set SMTP_HOST, SMTP_USERNAME, SMTP_PASSWORD in Fly secrets."
                        )
                    else:
                        await email_client.send_email(
                            to_email=email,
                            subject=f"Thank you from {settings.BUSINESS_NAME}",
                            body=confirmation_message,
                            html_body=f"<p>{confirmation_message}</p>",
                        )
                        logger.info(f"Confirmation email sent to seller: {email}")
                except Exception as e:
                    logger.error(
                        f"Failed to send confirmation email to seller {email}: {type(e).__name__}: {e}",
                        exc_info=True,
                    )
        except Exception as e:
            logger.warning(f"Failed to send confirmation SMS to seller: {str(e)}")
        
        # Send notification to office/Jeff about new seller lead (respects TEST_MODE)
        if settings.LEAD_NOTIFICATION_ENABLED:
            try:
                # Build notification message for office
                office_notification = (
                    f"🏡 NEW SELLER LEAD from AI Agent\n\n"
                    f"Name: {request.first_name} {request.last_name}\n"
                    f"Phone: {phone}\n"
                    f"Email: {email or 'Not provided'}\n"
                    f"Property: {request.property_address}, {request.city}, {(request.state or 'FL')} {(request.zip_code or '')}\n"
                    f"Type: {seller_lead.property_type or 'Not specified'}\n"
                    f"Beds/Baths: {seller_lead.bedrooms or '?'} bed / {seller_lead.bathrooms or '?'} bath\n"
                )
                
                # Add optional fields if provided
                if seller_lead.condition:
                    office_notification += f"Condition: {seller_lead.condition}\n"
                if seller_lead.previously_listed is not None:
                    office_notification += f"Previously Listed: {'Yes' if seller_lead.previously_listed else 'No'}\n"
                if seller_lead.currently_occupied is not None:
                    office_notification += f"Occupied: {'Yes' if seller_lead.currently_occupied else 'No'}\n"
                if seller_lead.timeframe:
                    office_notification += f"Timeline: {seller_lead.timeframe}\n"
                if seller_lead.estimated_value:
                    office_notification += f"Est. Value: ${seller_lead.estimated_value:,.0f}\n"
                if seller_lead.reason_for_selling:
                    office_notification += f"Reason: {seller_lead.reason_for_selling}\n"
                    
                office_notification += f"\nContact ID: {contact_id}\nAction: Schedule consultation ASAP"
                
                # Determine notification recipient (TEST_MODE overrides)
                notification_phone = settings.TEST_AGENT_PHONE if settings.TEST_MODE else (
                    settings.JEFF_NOTIFICATION_PHONE or settings.OFFICE_NOTIFICATION_PHONE
                )
                
                if notification_phone:
                    await twilio_client.send_sms(notification_phone, office_notification)
                    logger.info(f"Office notification sent to: {notification_phone} (TEST_MODE: {settings.TEST_MODE})")
                if settings.OFFICE_NOTIFICATION_EMAIL:
                    try:
                        email_client = EmailClient()
                        if email_client.is_configured:
                            await email_client.send_email(
                                to_email=settings.OFFICE_NOTIFICATION_EMAIL,
                                subject=f"🏡 New Seller Lead - {request.first_name} {request.last_name}",
                                body=office_notification,
                                html_body=f"<pre>{office_notification}</pre>",
                            )
                            logger.info(f"Office notification email sent to: {settings.OFFICE_NOTIFICATION_EMAIL}")
                    except Exception as e:
                        logger.warning(f"Failed to send office notification email: {str(e)}")
                if not notification_phone:
                    logger.warning("No notification phone configured (JEFF_NOTIFICATION_PHONE or OFFICE_NOTIFICATION_PHONE)")
                    
            except Exception as e:
                logger.warning(f"Failed to send office notification: {str(e)}")
                
    except Exception as e:
        logger.exception(f"Error in seller lead background tasks: {str(e)}")


@router.post("/create_seller_lead")
async def create_seller_lead(request: CreateSellerLeadRequest) -> VapiResponse:
    """
    Create a seller lead in the CRM
    
    This function captures seller information including:
    - Contact details (name, phone, email)
    - Property details (address, type, bedrooms, bathrooms)
    - Property features (square feet, year built, condition)
    - Selling motivation and timeline
    - Estimated value
    
    Important: Never discuss commission rates. Always refer to an agent for pricing questions.
    
    The lead is assigned to a listing specialist and a confirmation is sent.
    """
    try:
        logger.info(f"Creating seller lead: {request.first_name} {request.last_name}")

        # Provide safe defaults when optional fields are missing (voice callers often omit ZIP)
        request_state = (request.state or "").strip() or "FL"
        request_zip = (request.zip_code or "").strip()

        # Normalize placeholder last names commonly produced by LLMs
        normalized_last_name = (request.last_name or "").strip()
        if normalized_last_name.lower() in {"-", "n/a", "na", "none", "null", "unknown"}:
            normalized_last_name = ""
        
        # Validate and format phone
        try:
            phone = validate_phone(request.phone)
        except Exception as e:
            logger.warning(f"Phone validation failed: {str(e)}")
            phone = request.phone
        
        # Validate email if provided
        email = None
        if request.email:
            try:
                email = validate_email(request.email)
            except Exception as e:
                logger.warning(f"Email validation failed: {str(e)}")
                email = request.email
        
        # Create contact object
        contact = Contact(
            first_name=request.first_name,
            last_name=normalized_last_name,  # Handle None/empty + normalize placeholders
            phone=phone,
            email=email,
            contact_type=ContactType.SELLER,
            address=request.property_address,
            city=request.city,
            state=request_state,
            zip_code=request_zip or None,
            tags=["voice_agent", "seller_lead"],
            source="AI Concierge",
            notes=request.notes
        )
        
        # Create seller lead with all information
        seller_lead = SellerLead(
            contact=contact,
            property_address=request.property_address,
            city=request.city,
            state=request_state,
            zip_code=request_zip,
            property_type=request.property_type,
            bedrooms=request.bedrooms,
            bathrooms=request.bathrooms,
            square_feet=request.square_feet,
            year_built=request.year_built,
            condition=request.property_condition,  # Map property_condition to condition field
            reason_for_selling=request.reason_for_selling,
            timeframe=request.timeframe,
            estimated_value=request.estimated_value,
            previously_listed=request.previously_listed,
            currently_occupied=request.currently_occupied,
            status=LeadStatus.NEW
        )
        
        # Check if contact already exists (optional duplicate check)
        existing_contacts = []
        existing_contact_id = None
        try:
            existing_contacts = await crm_client.search_contacts(phone=phone, email=email)
            if existing_contacts:
                logger.info(f"Found existing contact(s) for phone/email: {len(existing_contacts)}")
                # Use the first existing contact
                existing_contact_id = existing_contacts[0].get('id')
                logger.info(f"Will update existing contact ID: {existing_contact_id}")
        except Exception as e:
            logger.warning(f"Contact search failed, proceeding with lead creation: {str(e)}")
        
        # If contact exists, update it; otherwise create new
        if existing_contact_id:
            logger.info(f"Updating existing seller contact: {existing_contact_id}")
            # Update existing contact with new property info
            try:
                update_data = {
                    'primary_address': seller_lead.property_address,
                    'primary_city': seller_lead.city,
                    'primary_state': seller_lead.state,
                    'primary_zip': seller_lead.zip_code,
                }
                
                await crm_client.update_contact(existing_contact_id, update_data)
                result = {"id": existing_contact_id}
                logger.info(f"Successfully updated existing contact: {existing_contact_id}")
            except Exception as e:
                logger.error(f"Failed to update existing contact: {str(e)}")
                # Fall back to creating new lead
                result = await crm_client.create_seller_lead(seller_lead)
        else:
            # Save to CRM (creates contact with seller lead info in one call)
            result = await crm_client.create_seller_lead(seller_lead)
        
        # Extract contact ID (handle different response formats)
        # Try multiple paths independently to handle various API response formats
        contact_id = result.get("id")
        if not contact_id and isinstance(result.get("data"), dict):
            contact_id = result.get("data", {}).get("id")
        if not contact_id and isinstance(result.get("contact"), dict):
            contact_id = result.get("contact", {}).get("id")
        
        if not contact_id:
            logger.error(f"Failed to extract contact ID from API response: {result}")
            # Try to continue anyway - note addition will fail gracefully
        
        logger.info(f"Seller lead created successfully with contact_id: {contact_id}")
        
        # Return immediately with contact_id - non-critical operations run in background
        # Concise response message per prompt guidelines
        message = f"Thank you, {request.first_name}! Sally or Jeff will contact you to discuss your property and schedule a consultation. You'll also get a text."
        
        response = VapiResponse(
            success=True,
            message=message,
            data={
                "contact_id": contact_id,
                "contact": contact.model_dump(),
                "property_details": seller_lead.model_dump(exclude={"contact"})
            }
        )
        
        # Fire off background tasks for non-critical operations (don't await)
        if contact_id:
            asyncio.create_task(
                _handle_seller_lead_background_tasks(
                    contact_id=contact_id,
                    request=request,
                    seller_lead=seller_lead,
                    phone=phone,
                    email=email
                )
            )
        
        return response
        
    except BoldTrailError as e:
        logger.error(f"CRM error in create_seller_lead: {e.message}")
        
        # Handle duplicate email/phone gracefully
        if "already exists" in e.message.lower() or "duplicate" in e.message.lower():
            logger.info("Duplicate contact detected, attempting to handle gracefully")
            # Attempt to retrieve the existing contact id so downstream tools can still reference it.
            existing_contact_id = None
            try:
                existing_contacts = await crm_client.search_contacts(phone=phone, email=email)
                if existing_contacts:
                    existing_contact_id = existing_contacts[0].get("id")
                    logger.info(f"Resolved duplicate to existing contact_id: {existing_contact_id}")
            except Exception as lookup_error:
                logger.warning(f"Failed to lookup existing contact after duplicate error: {str(lookup_error)}")

            return VapiResponse(
                success=True,
                message=f"Thank you, {request.first_name}! We have your information on file. Sally or Jeff will contact you to discuss your property and schedule a consultation. You'll also get a text.",
                data={
                    "contact_id": existing_contact_id,
                    "note": "Duplicate contact - existing record in CRM"
                }
            )
        
        return VapiResponse(
            success=False,
            error=(
                "I'm having trouble saving your information right now. "
                "Let me take your phone number and have a listing specialist call you back."
            ),
            message=e.message
        )
    
    except Exception as e:
        logger.exception(f"Error in create_seller_lead: {str(e)}")
        return VapiResponse(
            success=False,
            error="I encountered an error while saving your information. Let me connect you with an agent directly.",
            message=str(e)
        )

