"""
Function: Create Buyer Lead
Captures and stores buyer lead information in CRM
"""

from fastapi import APIRouter
from typing import Dict, Any
from src.models.vapi_models import VapiResponse, CreateBuyerLeadRequest
from src.models.crm_models import Contact, BuyerLead, ContactType, LeadStatus
from src.integrations.boldtrail import BoldTrailClient
from src.integrations.twilio_client import TwilioClient
from src.utils.logger import get_logger
from src.utils.errors import BoldTrailError
from src.utils.validators import validate_phone, validate_email

logger = get_logger(__name__)
router = APIRouter()

crm_client = BoldTrailClient()
twilio_client = TwilioClient()


@router.post("/create_buyer_lead")
async def create_buyer_lead(request: CreateBuyerLeadRequest) -> VapiResponse:
    """
    Create a buyer lead in the CRM
    
    This function captures buyer information including:
    - Contact details (name, phone, email)
    - Property preferences (type, location, price range)
    - Requirements (bedrooms, bathrooms, features)
    - Timeline and pre-approval status
    
    The lead is automatically assigned to an appropriate agent and
    a confirmation SMS is sent to the buyer.
    """
    try:
        logger.info(f"Creating buyer lead: {request.first_name} {request.last_name}")
        
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
            last_name=request.last_name or "",  # Handle None/empty
            phone=phone,
            email=email,
            contact_type=ContactType.BUYER,
            tags=["voice_agent", "buyer_lead"],
            source="AI Concierge",
            notes=request.notes
        )
        
        # Create buyer lead with all information
        buyer_lead = BuyerLead(
            contact=contact,
            property_type=request.property_type,
            location_preference=request.location_preference,
            min_price=request.min_price,
            max_price=request.max_price,
            bedrooms=request.bedrooms,
            bathrooms=request.bathrooms,
            timeframe=request.timeframe,
            pre_approved=request.pre_approved,
            status=LeadStatus.NEW
        )
        
        # Check if contact already exists (optional duplicate check)
        existing_contacts = []
        try:
            existing_contacts = await crm_client.search_contacts(phone=phone, email=email)
            if existing_contacts:
                logger.info(f"Found existing contact(s) for phone/email: {len(existing_contacts)}")
        except Exception as e:
            logger.warning(f"Contact search failed, proceeding with lead creation: {str(e)}")
        
        # Save to CRM (creates contact with buyer lead info in one call)
        result = await crm_client.create_buyer_lead(buyer_lead)
        
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
        
        logger.info(f"Buyer lead created successfully with contact_id: {contact_id}")
        
        # Log call activity to CRM (required for tracking)
        if contact_id:
            try:
                await crm_client.log_call(
                    contact_id=contact_id,
                    direction="inbound",
                    result=3,  # 3 = Contacted
                    notes=f"Initial buyer inquiry call. Looking for {buyer_lead.property_type or 'property'} in {buyer_lead.location_preference or 'The Villages'}. Price range: ${buyer_lead.min_price or 0:,.0f} - ${buyer_lead.max_price or 0:,.0f}."
                )
                logger.info(f"Call logged successfully for contact: {contact_id}")
            except Exception as e:
                logger.warning(f"Failed to log call activity for contact {contact_id}: {str(e)}")
        else:
            logger.error("Cannot log call: contact_id is None")
        
        # Add detailed note with conversation context (required for CRM completeness)
        if contact_id:
            try:
                note_content = f"Buyer Lead from AI Voice Agent\n\n"
                note_content += f"Property Preferences:\n"
                if buyer_lead.property_type:
                    note_content += f"- Type: {buyer_lead.property_type}\n"
                if buyer_lead.location_preference:
                    note_content += f"- Location: {buyer_lead.location_preference}\n"
                if buyer_lead.min_price or buyer_lead.max_price:
                    note_content += f"- Price Range: ${buyer_lead.min_price or 0:,.0f} - ${buyer_lead.max_price or 0:,.0f}\n"
                if buyer_lead.bedrooms:
                    note_content += f"- Bedrooms: {buyer_lead.bedrooms}+\n"
                if buyer_lead.bathrooms:
                    note_content += f"- Bathrooms: {buyer_lead.bathrooms}+\n"
                if buyer_lead.timeframe:
                    note_content += f"- Timeline: {buyer_lead.timeframe}\n"
                if buyer_lead.pre_approved:
                    note_content += f"- Pre-approved: Yes\n"
                if request.notes:
                    note_content += f"\nAdditional Notes:\n{request.notes}"
                
                await crm_client.add_note(
                    contact_id=contact_id,
                    note=note_content,
                    title="AI Concierge - Buyer Lead Details"
                )
                logger.info(f"Note added successfully for contact: {contact_id}")
            except Exception as e:
                logger.warning(f"Failed to add note for contact {contact_id}: {str(e)}")
        else:
            logger.error("Cannot add note: contact_id is None")
        
        # Send confirmation SMS
        try:
            confirmation_message = (
                f"Hi {request.first_name}! Thank you for your interest. "
                f"We've received your information and one of our agents will contact you shortly. "
                f"- Sally Love Real Estate"
            )
            await twilio_client.send_sms(phone, confirmation_message)
        except Exception as e:
            logger.warning(f"Failed to send confirmation SMS: {str(e)}")
        
        # Concise response message per prompt guidelines
        message = f"Perfect, {request.first_name}! Sally or one of our agents will call you shortly. You'll get a text too."
        
        return VapiResponse(
            success=True,
            message=message,
            data={
                "contact_id": contact_id,
                "contact": contact.model_dump(),
                "preferences": buyer_lead.model_dump(exclude={"contact"})
            }
        )
        
    except BoldTrailError as e:
        logger.error(f"CRM error in create_buyer_lead: {e.message}")
        return VapiResponse(
            success=False,
            error=(
                "I'm having trouble saving your information right now. "
                "Let me take your phone number and have an agent call you back to discuss your needs."
            ),
            message=e.message
        )
    
    except Exception as e:
        logger.exception(f"Error in create_buyer_lead: {str(e)}")
        return VapiResponse(
            success=False,
            error="I encountered an error while saving your information. Let me connect you with an agent directly.",
            message=str(e)
        )

