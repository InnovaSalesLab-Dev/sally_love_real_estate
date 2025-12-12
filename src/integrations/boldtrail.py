"""
BoldTrail CRM API client
"""

import httpx
from typing import Dict, Any, Optional, List
from datetime import datetime
from src.config.settings import settings
from src.utils.logger import get_logger
from src.utils.errors import BoldTrailError
from src.models.crm_models import Contact, BuyerLead, SellerLead, Agent, Appointment

logger = get_logger(__name__)


class BoldTrailClient:
    """Client for BoldTrail CRM API"""
    
    def __init__(self):
        self.api_key = settings.BOLDTRAIL_API_KEY
        self.base_url = settings.BOLDTRAIL_API_URL
        self.account_id = settings.BOLDTRAIL_ACCOUNT_ID
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make HTTP request to BoldTrail API
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            data: Request body
            params: Query parameters
            
        Returns:
            Response data
            
        Raises:
            BoldTrailError: If request fails
        """
        url = f"{self.base_url}/{endpoint}"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    json=data,
                    params=params,
                    timeout=30.0,
                )
                
                if response.status_code >= 400:
                    error_detail = response.text
                    logger.error(f"BoldTrail API error: {response.status_code} - {error_detail}")
                    raise BoldTrailError(
                        message=f"BoldTrail API error: {error_detail}",
                        status_code=response.status_code,
                        details={"response": error_detail}
                    )
                
                return response.json() if response.text else {}
                
        except httpx.RequestError as e:
            logger.exception(f"BoldTrail request failed: {str(e)}")
            raise BoldTrailError(
                message=f"Failed to connect to BoldTrail: {str(e)}",
                details={"error": str(e)}
            )
    
    async def create_contact(self, contact: Contact) -> Dict[str, Any]:
        """
        Create a new contact in CRM
        
        Args:
            contact: Contact data
            
        Returns:
            Created contact with ID
        """
        logger.info(f"Creating BoldTrail contact: {contact.first_name} {contact.last_name}")
        
        payload = {
            "firstName": contact.first_name,
            "lastName": contact.last_name,
            "phone": contact.phone,
            "email": contact.email,
            "address": contact.address,
            "city": contact.city,
            "state": contact.state,
            "zipCode": contact.zip_code,
            "type": contact.contact_type.value,
            "tags": contact.tags,
            "source": contact.source,
            "notes": contact.notes,
            "customFields": contact.custom_fields,
        }
        
        # Remove None values
        payload = {k: v for k, v in payload.items() if v is not None}
        
        return await self._make_request("POST", "contacts", data=payload)
    
    async def get_contact(self, contact_id: str) -> Dict[str, Any]:
        """
        Get contact by ID
        
        Args:
            contact_id: Contact ID
            
        Returns:
            Contact data
        """
        return await self._make_request("GET", f"contacts/{contact_id}")
    
    async def search_contacts(
        self,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        name: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for contacts
        
        Args:
            phone: Phone number
            email: Email address
            name: Contact name
            
        Returns:
            List of matching contacts
        """
        params = {}
        if phone:
            params["phone"] = phone
        if email:
            params["email"] = email
        if name:
            params["name"] = name
        
        result = await self._make_request("GET", "contacts/search", params=params)
        return result.get("contacts", []) if isinstance(result, dict) else []
    
    async def create_buyer_lead(self, buyer_lead: BuyerLead) -> Dict[str, Any]:
        """
        Create a buyer lead in CRM
        
        Args:
            buyer_lead: Buyer lead data
            
        Returns:
            Created lead with ID
        """
        logger.info(f"Creating buyer lead: {buyer_lead.contact.first_name} {buyer_lead.contact.last_name}")
        
        # First create or get contact
        contact_data = await self.create_contact(buyer_lead.contact)
        contact_id = contact_data.get("id")
        
        # Create lead
        payload = {
            "contactId": contact_id,
            "type": "buyer",
            "propertyType": buyer_lead.property_type,
            "locationPreference": buyer_lead.location_preference,
            "minPrice": buyer_lead.min_price,
            "maxPrice": buyer_lead.max_price,
            "bedrooms": buyer_lead.bedrooms,
            "bathrooms": buyer_lead.bathrooms,
            "squareFeetMin": buyer_lead.square_feet_min,
            "squareFeetMax": buyer_lead.square_feet_max,
            "timeframe": buyer_lead.timeframe,
            "preApproved": buyer_lead.pre_approved,
            "lenderName": buyer_lead.lender_name,
            "mustHaves": buyer_lead.must_haves,
            "niceToHaves": buyer_lead.nice_to_haves,
            "status": buyer_lead.status.value,
            "assignedAgentId": buyer_lead.assigned_agent_id,
        }
        
        payload = {k: v for k, v in payload.items() if v is not None}
        
        return await self._make_request("POST", "leads", data=payload)
    
    async def create_seller_lead(self, seller_lead: SellerLead) -> Dict[str, Any]:
        """
        Create a seller lead in CRM
        
        Args:
            seller_lead: Seller lead data
            
        Returns:
            Created lead with ID
        """
        logger.info(f"Creating seller lead: {seller_lead.contact.first_name} {seller_lead.contact.last_name}")
        
        # First create or get contact
        contact_data = await self.create_contact(seller_lead.contact)
        contact_id = contact_data.get("id")
        
        # Create lead
        payload = {
            "contactId": contact_id,
            "type": "seller",
            "propertyAddress": seller_lead.property_address,
            "city": seller_lead.city,
            "state": seller_lead.state,
            "zipCode": seller_lead.zip_code,
            "propertyType": seller_lead.property_type,
            "bedrooms": seller_lead.bedrooms,
            "bathrooms": seller_lead.bathrooms,
            "squareFeet": seller_lead.square_feet,
            "lotSize": seller_lead.lot_size,
            "yearBuilt": seller_lead.year_built,
            "condition": seller_lead.condition,
            "reasonForSelling": seller_lead.reason_for_selling,
            "timeframe": seller_lead.timeframe,
            "estimatedValue": seller_lead.estimated_value,
            "mortgageBalance": seller_lead.mortgage_balance,
            "improvements": seller_lead.improvements,
            "status": seller_lead.status.value,
            "assignedAgentId": seller_lead.assigned_agent_id,
        }
        
        payload = {k: v for k, v in payload.items() if v is not None}
        
        return await self._make_request("POST", "leads", data=payload)
    
    async def get_agents(
        self,
        specialty: Optional[str] = None,
        city: Optional[str] = None,
        available: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Get list of agents (users in BoldTrail)
        
        Args:
            specialty: Agent specialty filter
            city: Service area filter
            available: Filter by availability
            
        Returns:
            List of agents
        """
        params = {}
        if specialty:
            params["filter[specialty]"] = specialty
        if city:
            params["filter[city]"] = city
        
        result = await self._make_request("GET", "users", params=params)
        return result.get("data", []) if isinstance(result, dict) else []
    
    async def get_agent(self, agent_id: str) -> Dict[str, Any]:
        """
        Get agent by ID (user in BoldTrail)
        
        Args:
            agent_id: Agent/User ID
            
        Returns:
            Agent data
        """
        return await self._make_request("GET", f"users/{agent_id}")
    
    async def create_appointment(self, appointment: Appointment) -> Dict[str, Any]:
        """
        Create an appointment
        
        Args:
            appointment: Appointment data
            
        Returns:
            Created appointment with ID
        """
        logger.info(f"Creating appointment for contact {appointment.contact_id}")
        
        payload = {
            "contactId": appointment.contact_id,
            "agentId": appointment.agent_id,
            "appointmentType": appointment.appointment_type,
            "date": appointment.date.isoformat(),
            "durationMinutes": appointment.duration_minutes,
            "location": appointment.location,
            "propertyAddress": appointment.property_address,
            "mlsNumber": appointment.mls_number,
            "status": appointment.status,
            "notes": appointment.notes,
        }
        
        payload = {k: v for k, v in payload.items() if v is not None}
        
        return await self._make_request("POST", "appointments", data=payload)
    
    async def update_contact(
        self,
        contact_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update contact information
        
        Args:
            contact_id: Contact ID
            updates: Fields to update
            
        Returns:
            Updated contact data
        """
        logger.info(f"Updating contact: {contact_id}")
        return await self._make_request("PATCH", f"contacts/{contact_id}", data=updates)

