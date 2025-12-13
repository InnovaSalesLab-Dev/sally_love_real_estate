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
        Create a buyer lead in CRM using BoldTrail contact endpoint
        
        BoldTrail doesn't have a separate /leads endpoint. Instead, leads are contacts
        with lead_type set to "Buyer" and preferences stored in notes.
        
        Reference: https://developer.insiderealestate.com/publicv2/reference/post_v2-public-contact
        
        Args:
            buyer_lead: Buyer lead data
            
        Returns:
            Created contact with ID
        """
        logger.info(f"Creating buyer lead: {buyer_lead.contact.first_name} {buyer_lead.contact.last_name}")
        
        # Build buyer preferences summary for notes
        preferences = []
        if buyer_lead.property_type:
            preferences.append(f"Property Type: {buyer_lead.property_type}")
        if buyer_lead.location_preference:
            preferences.append(f"Location: {buyer_lead.location_preference}")
        if buyer_lead.min_price or buyer_lead.max_price:
            price_range = f"${buyer_lead.min_price or 0:,.0f} - ${buyer_lead.max_price or 0:,.0f}"
            preferences.append(f"Budget: {price_range}")
        if buyer_lead.bedrooms:
            preferences.append(f"Bedrooms: {buyer_lead.bedrooms}+")
        if buyer_lead.bathrooms:
            preferences.append(f"Bathrooms: {buyer_lead.bathrooms}+")
        if buyer_lead.timeframe:
            preferences.append(f"Timeframe: {buyer_lead.timeframe}")
        if buyer_lead.pre_approved:
            preferences.append("Pre-approved: Yes")
        
        notes = "Buyer Lead from AI Concierge\n" + "\n".join(preferences)
        if buyer_lead.contact.notes:
            notes += f"\n\nAdditional Notes: {buyer_lead.contact.notes}"
        
        # Create contact with buyer lead information
        payload = {
            "firstName": buyer_lead.contact.first_name,
            "lastName": buyer_lead.contact.last_name,
            "phone": buyer_lead.contact.phone,
            "email": buyer_lead.contact.email,
            "leadType": "Buyer",  # BoldTrail standard field
            "status": buyer_lead.status.value,
            "tags": buyer_lead.contact.tags or ["voice_agent", "buyer_lead"],
            "source": buyer_lead.contact.source or "AI Concierge",
            "notes": notes
        }
        
        # Remove None values
        payload = {k: v for k, v in payload.items() if v is not None}
        
        return await self._make_request("POST", "contact", data=payload)
    
    async def create_seller_lead(self, seller_lead: SellerLead) -> Dict[str, Any]:
        """
        Create a seller lead in CRM using BoldTrail contact endpoint
        
        BoldTrail doesn't have a separate /leads endpoint. Instead, leads are contacts
        with lead_type set to "Seller" and property details stored in notes.
        
        Reference: https://developer.insiderealestate.com/publicv2/reference/post_v2-public-contact
        
        Args:
            seller_lead: Seller lead data
            
        Returns:
            Created contact with ID
        """
        logger.info(f"Creating seller lead: {seller_lead.contact.first_name} {seller_lead.contact.last_name}")
        
        # Build property details summary for notes
        property_details = []
        property_details.append(f"Property Address: {seller_lead.property_address}")
        property_details.append(f"City: {seller_lead.city}, {seller_lead.state} {seller_lead.zip_code}")
        if seller_lead.property_type:
            property_details.append(f"Property Type: {seller_lead.property_type}")
        if seller_lead.bedrooms:
            property_details.append(f"Bedrooms: {seller_lead.bedrooms}")
        if seller_lead.bathrooms:
            property_details.append(f"Bathrooms: {seller_lead.bathrooms}")
        if seller_lead.square_feet:
            property_details.append(f"Square Feet: {seller_lead.square_feet:,}")
        if seller_lead.year_built:
            property_details.append(f"Year Built: {seller_lead.year_built}")
        if seller_lead.estimated_value:
            property_details.append(f"Estimated Value: ${seller_lead.estimated_value:,.0f}")
        if seller_lead.reason_for_selling:
            property_details.append(f"Reason for Selling: {seller_lead.reason_for_selling}")
        if seller_lead.timeframe:
            property_details.append(f"Timeframe: {seller_lead.timeframe}")
        
        notes = "Seller Lead from AI Concierge\n" + "\n".join(property_details)
        if seller_lead.contact.notes:
            notes += f"\n\nAdditional Notes: {seller_lead.contact.notes}"
        
        # Create contact with seller lead information
        payload = {
            "firstName": seller_lead.contact.first_name,
            "lastName": seller_lead.contact.last_name,
            "phone": seller_lead.contact.phone,
            "email": seller_lead.contact.email,
            "address": seller_lead.property_address,
            "city": seller_lead.city,
            "state": seller_lead.state,
            "zipCode": seller_lead.zip_code,
            "leadType": "Seller",  # BoldTrail standard field
            "status": seller_lead.status.value,
            "tags": seller_lead.contact.tags or ["voice_agent", "seller_lead"],
            "source": seller_lead.contact.source or "AI Concierge",
            "notes": notes
        }
        
        # Remove None values
        payload = {k: v for k, v in payload.items() if v is not None}
        
        return await self._make_request("POST", "contact", data=payload)
    
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
    
    async def add_note(
        self,
        contact_id: str,
        note: str,
        subject: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add a note to a contact
        
        Reference: https://developer.insiderealestate.com/publicv2/reference/put_v2-public-contact-contact-id-action-note
        
        Args:
            contact_id: Contact ID
            note: Note content
            subject: Note subject/title (optional)
            
        Returns:
            Created note data
        """
        logger.info(f"Adding note to contact: {contact_id}")
        
        payload = {"note": note}
        if subject:
            payload["subject"] = subject
        
        return await self._make_request("PUT", f"contact/{contact_id}/action/note", data=payload)
    
    async def log_call(
        self,
        contact_id: str,
        call_type: str = "Inbound",
        subject: Optional[str] = None,
        duration: Optional[int] = None,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Log a call activity to a contact
        
        Reference: https://developer.insiderealestate.com/publicv2/reference/put_v2-public-contact-contact-id-action-call
        
        Args:
            contact_id: Contact ID
            call_type: Type of call (Inbound, Outbound, Missed)
            subject: Call subject/title
            duration: Call duration in seconds
            notes: Call notes
            
        Returns:
            Created call log data
        """
        logger.info(f"Logging call for contact: {contact_id}")
        
        payload = {
            "type": call_type,
            "subject": subject or "AI Concierge Call",
            "duration": duration,
            "notes": notes
        }
        
        # Remove None values
        payload = {k: v for k, v in payload.items() if v is not None}
        
        return await self._make_request("PUT", f"contact/{contact_id}/action/call", data=payload)
    
    async def get_manual_listings(
        self,
        property_type: Optional[str] = None,
        city: Optional[str] = None,
        state: Optional[str] = None,
        address: Optional[str] = None,
        zip_code: Optional[str] = None,
        mls_number: Optional[str] = None,
        status: Optional[str] = "active",
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        min_bedrooms: Optional[int] = None,
        min_bathrooms: Optional[float] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get manual listings from BoldTrail
        
        Reference: https://developer.insiderealestate.com/publicv2/reference/get_v2-public-manuallistings
        
        Args:
            property_type: Property type filter
            city: City filter
            state: State filter
            address: Address filter (partial match)
            zip_code: ZIP code filter
            mls_number: MLS number filter
            status: Listing status filter (default: "active" to only show available properties)
                   Common values: active, pending, sold, expired
            min_price: Minimum price
            max_price: Maximum price
            min_bedrooms: Minimum bedrooms
            min_bathrooms: Minimum bathrooms
            limit: Maximum results to return
            
        Returns:
            List of manual listings (defaults to active listings only)
        """
        logger.info(f"Searching manual listings in BoldTrail (status: {status})")
        
        params = {}
        if property_type:
            params["filter[property_type]"] = property_type
        if city:
            params["filter[city]"] = city
        if state:
            params["filter[state]"] = state
        if address:
            params["filter[address]"] = address
        if zip_code:
            params["filter[zip_code]"] = zip_code
        if mls_number:
            params["filter[mls_number]"] = mls_number
        if status:
            params["filter[status]"] = status
        if min_price:
            params["filter[min_price]"] = min_price
        if max_price:
            params["filter[max_price]"] = max_price
        if min_bedrooms:
            params["filter[bedrooms][gte]"] = min_bedrooms
        if min_bathrooms:
            params["filter[bathrooms][gte]"] = min_bathrooms
        if limit:
            params["limit"] = limit
        
        result = await self._make_request("GET", "manuallistings", params=params)
        return result.get("data", []) if isinstance(result, dict) else []
    
    async def get_manual_listing(self, listing_id: str) -> Dict[str, Any]:
        """
        Get specific manual listing by ID
        
        Reference: https://developer.insiderealestate.com/publicv2/reference/get_v2-public-manuallisting-manual-listing-id
        
        Args:
            listing_id: Manual listing ID
            
        Returns:
            Manual listing details (extracted from 'data' field for consistency)
        """
        logger.info(f"Getting manual listing: {listing_id}")
        result = await self._make_request("GET", f"manuallisting/{listing_id}")
        # Extract data field for consistency with get_manual_listings
        return result.get("data", result) if isinstance(result, dict) else result
    
    async def get_manual_listing_property_types(self) -> List[str]:
        """
        Get available property types for manual listings
        
        Reference: https://developer.insiderealestate.com/publicv2/reference/get_v2-public-manuallisting-propertytypes
        
        Returns:
            List of property types
        """
        logger.info(f"Getting manual listing property types")
        result = await self._make_request("GET", "manuallisting/propertytypes")
        return result.get("data", []) if isinstance(result, dict) else []
