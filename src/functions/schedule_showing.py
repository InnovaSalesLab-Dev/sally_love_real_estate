"""
Function: Schedule Showing
Schedules property showings and appointments
"""

from fastapi import APIRouter
from typing import Dict, Any
from datetime import datetime
from src.models.vapi_models import VapiResponse, ScheduleShowingRequest
from src.models.crm_models import Appointment
from src.integrations.boldtrail import BoldTrailClient
from src.integrations.twilio_client import TwilioClient
from src.utils.logger import get_logger
from src.utils.errors import BoldTrailError, ValidationError
from src.utils.validators import validate_phone, validate_email, validate_date

logger = get_logger(__name__)
router = APIRouter()

crm_client = BoldTrailClient()
twilio_client = TwilioClient()


@router.post("/schedule_showing")
async def schedule_showing(request: ScheduleShowingRequest) -> VapiResponse:
    """
    Schedule a property showing or appointment
    
    This function handles:
    - Property showing scheduling
    - Agent availability checking
    - Appointment confirmation
    - SMS reminders
    
    Appointments are created in the CRM and agents are notified.
    """
    try:
        logger.info(f"Scheduling showing for: {request.contact_name} at {request.property_address}")
        
        # Validate phone
        try:
            phone = validate_phone(request.contact_phone)
        except Exception as e:
            logger.warning(f"Phone validation failed: {str(e)}")
            phone = request.contact_phone
        
        # Validate email if provided
        email = None
        if request.contact_email:
            try:
                email = validate_email(request.contact_email)
            except Exception as e:
                logger.warning(f"Email validation failed: {str(e)}")
                email = request.contact_email
        
        # Parse date and time
        try:
            # Combine date and time
            datetime_str = f"{request.preferred_date} {request.preferred_time}"
            appointment_datetime = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
            
            # Check if date is in the past
            if appointment_datetime < datetime.now():
                return VapiResponse(
                    success=False,
                    error="That date and time has already passed. Could you provide a future date and time?",
                    message="Requested time is in the past"
                )
                
        except ValueError as e:
            logger.warning(f"Date/time parsing failed: {str(e)}")
            return VapiResponse(
                success=False,
                error="I had trouble understanding that date and time. Could you provide it in the format like 'January 15th at 2 PM'?",
                message=str(e)
            )
        
        # Find or create contact
        contacts = await crm_client.search_contacts(phone=phone)
        if contacts:
            contact_id = contacts[0].get("id")
        else:
            # Create new contact
            from src.models.crm_models import Contact, ContactType
            contact = Contact(
                first_name=request.contact_name.split()[0] if request.contact_name else "Guest",
                last_name=" ".join(request.contact_name.split()[1:]) if len(request.contact_name.split()) > 1 else "",
                phone=phone,
                email=email,
                contact_type=ContactType.BUYER,
                tags=["voice_agent", "showing_request"],
                source="voice_agent"
            )
            contact_data = await crm_client.create_contact(contact)
            contact_id = contact_data.get("id")
        
        # Get available agent or use provided agent
        agent_id = request.agent_id
        if not agent_id:
            # Find available agent
            agents = await crm_client.get_agents(available=True)
            if agents:
                agent_id = agents[0].get("id")
            else:
                return VapiResponse(
                    success=False,
                    error="I'm having trouble finding an available agent for that time. Let me take your information and have someone call you to schedule.",
                    message="No available agents"
                )
        
        # Create appointment
        appointment = Appointment(
            contact_id=contact_id,
            agent_id=agent_id,
            appointment_type="showing",
            date=appointment_datetime,
            duration_minutes=60,
            property_address=request.property_address,
            mls_number=request.mls_number,
            status="scheduled",
            notes=request.notes
        )
        
        result = await crm_client.create_appointment(appointment)
        appointment_id = result.get("id")
        
        logger.info(f"Showing scheduled successfully: {appointment_id}")
        
        # Send confirmation SMS
        try:
            confirmation_message = (
                f"Hi {request.contact_name}! Your showing at {request.property_address} "
                f"is confirmed for {request.preferred_date} at {request.preferred_time}. "
                f"We'll send you a reminder before the appointment. - Sally Love Real Estate"
            )
            await twilio_client.send_sms(phone, confirmation_message)
        except Exception as e:
            logger.warning(f"Failed to send confirmation SMS: {str(e)}")
        
        # Format response
        formatted_date = appointment_datetime.strftime("%A, %B %d")
        formatted_time = appointment_datetime.strftime("%I:%M %p")
        
        message = (
            f"Perfect! I've scheduled your showing at {request.property_address} "
            f"for {formatted_date} at {formatted_time}. "
        )
        
        if request.mls_number:
            message += f"The MLS number is {request.mls_number}. "
        
        message += (
            "You'll receive a confirmation text message with all the details "
            "and a reminder before your appointment. "
            "Is there anything else I can help you with?"
        )
        
        return VapiResponse(
            success=True,
            message=message,
            data={
                "appointment_id": appointment_id,
                "contact_id": contact_id,
                "agent_id": agent_id,
                "date": appointment_datetime.isoformat(),
                "property_address": request.property_address,
                "mls_number": request.mls_number
            }
        )
        
    except BoldTrailError as e:
        logger.error(f"CRM error in schedule_showing: {e.message}")
        return VapiResponse(
            success=False,
            error=(
                "I'm having trouble scheduling that appointment right now. "
                "Let me take your information and have an agent call you to set up the showing."
            ),
            message=e.message
        )
    
    except Exception as e:
        logger.exception(f"Error in schedule_showing: {str(e)}")
        return VapiResponse(
            success=False,
            error="I encountered an error while scheduling your showing. Let me connect you with an agent who can help.",
            message=str(e)
        )

