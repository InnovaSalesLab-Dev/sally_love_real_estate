"""
BoldTrail CRM webhook handlers
Handles events from BoldTrail including contact updates, appointments, etc.
"""

from fastapi import APIRouter, Request, HTTPException
from typing import Dict, Any
from src.utils.logger import get_logger
from src.integrations.twilio_client import TwilioClient

logger = get_logger(__name__)
router = APIRouter()

twilio_client = TwilioClient()


@router.post("/events")
async def handle_crm_webhook(request: Request) -> Dict[str, Any]:
    """
    Handle incoming webhooks from BoldTrail CRM
    
    Event types:
    - contact.created: New contact added
    - contact.updated: Contact information changed
    - lead.created: New lead created
    - lead.assigned: Lead assigned to agent
    - appointment.created: New appointment scheduled
    - appointment.updated: Appointment changed
    - appointment.reminder: Reminder for upcoming appointment
    """
    try:
        payload = await request.json()
        event_type = payload.get("event")
        
        logger.info(f"Received CRM webhook: {event_type}")
        logger.debug(f"Webhook payload: {payload}")
        
        # Handle different event types
        if event_type == "contact.created":
            return await handle_contact_created(payload)
        
        elif event_type == "contact.updated":
            return await handle_contact_updated(payload)
        
        elif event_type == "lead.created":
            return await handle_lead_created(payload)
        
        elif event_type == "lead.assigned":
            return await handle_lead_assigned(payload)
        
        elif event_type == "appointment.created":
            return await handle_appointment_created(payload)
        
        elif event_type == "appointment.reminder":
            return await handle_appointment_reminder(payload)
        
        else:
            logger.warning(f"Unknown CRM event type: {event_type}")
            return {"status": "unknown_event_type", "type": event_type}
        
    except Exception as e:
        logger.exception(f"Error handling CRM webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def handle_contact_created(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Handle new contact created event"""
    contact = payload.get("data", {})
    contact_id = contact.get("id")
    
    logger.info(f"New contact created: {contact_id}")
    
    # You can add logic here to:
    # - Send welcome message
    # - Assign to agent
    # - Add to nurture campaign
    
    return {"status": "processed", "contact_id": contact_id}


async def handle_contact_updated(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Handle contact updated event"""
    contact = payload.get("data", {})
    contact_id = contact.get("id")
    
    logger.info(f"Contact updated: {contact_id}")
    
    return {"status": "processed", "contact_id": contact_id}


async def handle_lead_created(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Handle new lead created event"""
    lead = payload.get("data", {})
    lead_id = lead.get("id")
    lead_type = lead.get("type")
    
    logger.info(f"New {lead_type} lead created: {lead_id}")
    
    # You can add logic here to:
    # - Auto-assign to agent based on criteria
    # - Send notification to sales team
    # - Create follow-up tasks
    
    return {"status": "processed", "lead_id": lead_id}


async def handle_lead_assigned(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Handle lead assigned to agent event"""
    lead = payload.get("data", {})
    lead_id = lead.get("id")
    agent_id = lead.get("assignedAgentId")
    
    logger.info(f"Lead {lead_id} assigned to agent {agent_id}")
    
    # You can add logic here to:
    # - Notify agent via SMS/email
    # - Create calendar reminder
    # - Update dashboard
    
    return {"status": "processed", "lead_id": lead_id, "agent_id": agent_id}


async def handle_appointment_created(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Handle new appointment created event"""
    appointment = payload.get("data", {})
    appointment_id = appointment.get("id")
    
    logger.info(f"New appointment created: {appointment_id}")
    
    # Send confirmation to contact if phone number available
    contact_phone = appointment.get("contactPhone")
    if contact_phone:
        try:
            message = (
                f"Your appointment has been confirmed for {appointment.get('date')}. "
                f"We'll send you a reminder before the appointment. - Sally Love Real Estate"
            )
            await twilio_client.send_sms(contact_phone, message)
        except Exception as e:
            logger.warning(f"Failed to send appointment confirmation: {str(e)}")
    
    return {"status": "processed", "appointment_id": appointment_id}


async def handle_appointment_reminder(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Handle appointment reminder event"""
    appointment = payload.get("data", {})
    appointment_id = appointment.get("id")
    contact_phone = appointment.get("contactPhone")
    
    logger.info(f"Sending reminder for appointment: {appointment_id}")
    
    # Send reminder SMS
    if contact_phone:
        try:
            property_address = appointment.get("propertyAddress", "your appointment")
            date = appointment.get("date")
            
            message = (
                f"Reminder: Your showing at {property_address} is scheduled for {date}. "
                f"See you soon! - Sally Love Real Estate"
            )
            await twilio_client.send_sms(contact_phone, message)
            logger.info(f"Reminder sent for appointment {appointment_id}")
        except Exception as e:
            logger.error(f"Failed to send appointment reminder: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    return {"status": "processed", "appointment_id": appointment_id}


@router.get("/health")
async def crm_webhook_health() -> Dict[str, str]:
    """Health check endpoint for CRM webhooks"""
    return {"status": "healthy", "service": "crm_webhooks"}

