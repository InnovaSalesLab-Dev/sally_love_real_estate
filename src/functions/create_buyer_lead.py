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
        
        # Create contact
        contact = Contact(
            first_name=request.first_name,
            last_name=request.last_name,
            phone=phone,
            email=email,
            contact_type=ContactType.BUYER,
            tags=["voice_agent", "buyer_lead"],
            source="voice_agent",
            notes=request.notes
        )
        
        # Create buyer lead
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
        
        # Save to CRM
        result = await crm_client.create_buyer_lead(buyer_lead)
        lead_id = result.get("id")
        
        logger.info(f"Buyer lead created successfully: {lead_id}")
        
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
        
        # Format price range for voice response
        price_info = ""
        if request.min_price and request.max_price:
            price_info = f" in the ${request.min_price:,.0f} to ${request.max_price:,.0f} range"
        elif request.max_price:
            price_info = f" up to ${request.max_price:,.0f}"
        
        message = (
            f"Perfect! I've recorded your information, {request.first_name}. "
            f"You're looking for a {request.bedrooms or ''} bedroom property"
            f"{price_info}"
        )
        
        if request.location_preference:
            message += f" in the {request.location_preference} area"
        
        message += (
            ". One of our experienced agents will review your preferences and "
            "contact you shortly to discuss available properties. "
            "I've also sent you a confirmation text message. "
            "Is there anything else I can help you with?"
        )
        
        return VapiResponse(
            success=True,
            message=message,
            data={
                "lead_id": lead_id,
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

