"""
Function: Create Seller Lead
Captures and stores seller lead information in CRM
"""

from fastapi import APIRouter
from typing import Dict, Any
from src.models.vapi_models import VapiResponse, CreateSellerLeadRequest
from src.models.crm_models import Contact, SellerLead, ContactType, LeadStatus
from src.integrations.boldtrail import BoldTrailClient
from src.integrations.twilio_client import TwilioClient
from src.utils.logger import get_logger
from src.utils.errors import BoldTrailError
from src.utils.validators import validate_phone, validate_email

logger = get_logger(__name__)
router = APIRouter()

crm_client = BoldTrailClient()
twilio_client = TwilioClient()


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
            last_name=request.last_name or "",  # Handle None/empty - API requires string
            phone=phone,
            email=email,
            contact_type=ContactType.SELLER,
            address=request.property_address,
            city=request.city,
            state=request.state,
            zip_code=request.zip_code,
            tags=["voice_agent", "seller_lead"],
            source="AI Concierge",
            notes=request.notes
        )
        
        # Create seller lead with all information
        seller_lead = SellerLead(
            contact=contact,
            property_address=request.property_address,
            city=request.city,
            state=request.state,
            zip_code=request.zip_code,
            property_type=request.property_type,
            bedrooms=request.bedrooms,
            bathrooms=request.bathrooms,
            square_feet=request.square_feet,
            year_built=request.year_built,
            reason_for_selling=request.reason_for_selling,
            timeframe=request.timeframe,
            estimated_value=request.estimated_value,
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
        
        # Log call activity to CRM (required for tracking)
        if contact_id:
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
        else:
            logger.error("Cannot log call: contact_id is None")
        
        # Add detailed note with conversation context (required for CRM completeness)
        if contact_id:
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
        else:
            logger.error("Cannot add note: contact_id is None")
        
        # Send confirmation SMS
        try:
            confirmation_message = (
                f"Hi {request.first_name}! Thank you for considering Sally Love Real Estate. "
                f"A listing specialist will contact you shortly to discuss your property at {request.property_address}. "
                f"We look forward to helping you!"
            )
            await twilio_client.send_sms(phone, confirmation_message)
        except Exception as e:
            logger.warning(f"Failed to send confirmation SMS: {str(e)}")
        
        # Format response message
        property_details = f"{request.property_address}, {request.city}"
        
        message = (
            f"Thank you, {request.first_name}! I've recorded your information about the property at {property_details}. "
        )
        
        if request.bedrooms and request.bathrooms:
            message += f"Your {request.bedrooms} bedroom, {request.bathrooms} bathroom property "
        
        if request.timeframe:
            message += f"and your {request.timeframe} timeframe "
        
        message += (
            "has been noted. One of our listing specialists will contact you shortly to discuss "
            "a market analysis and the next steps. I've sent you a confirmation text. "
            "Is there anything else you'd like me to note for the agent?"
        )
        
        return VapiResponse(
            success=True,
            message=message,
            data={
                "contact_id": contact_id,
                "contact": contact.model_dump(),
                "property_details": seller_lead.model_dump(exclude={"contact"})
            }
        )
        
    except BoldTrailError as e:
        logger.error(f"CRM error in create_seller_lead: {e.message}")
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

