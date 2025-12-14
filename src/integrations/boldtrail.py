"""
BoldTrail CRM API client
"""

import httpx
import xml.etree.ElementTree as ET
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
from src.config.settings import settings
from src.utils.logger import get_logger
from src.utils.errors import BoldTrailError
from src.models.crm_models import Contact, BuyerLead, SellerLead, Agent, Appointment

logger = get_logger(__name__)

# Cache for XML listings feed
_listings_cache: Optional[List[Dict[str, Any]]] = None
_cache_timestamp: Optional[float] = None
CACHE_DURATION = 7200  # 2 hours in seconds


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
        
        return await self._make_request("POST", "contact", data=payload)
    
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
            # Note: status field removed - BoldTrail expects integer, will use default
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
            # Note: status field removed - BoldTrail expects integer, will use default
            "tags": seller_lead.contact.tags or ["voice_agent", "seller_lead"],
            "source": seller_lead.contact.source or "AI Concierge",
            "notes": notes
        }
        
        # Remove None values
        payload = {k: v for k, v in payload.items() if v is not None}
        
        return await self._make_request("POST", "contact", data=payload)
    
    async def get_agents(
        self,
        name: Optional[str] = None,
        specialty: Optional[str] = None,
        city: Optional[str] = None,
        available: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Get list of agents (users in BoldTrail)
        
        Reference: https://developer.insiderealestate.com/publicv2/reference/get_v2-public-users
        
        Args:
            name: Agent name search
            specialty: Agent specialty filter
            city: Service area filter
            available: Filter by availability
            
        Returns:
            List of agents
        """
        params = {}
        if name:
            params["search"] = name  # BoldTrail uses 'search' parameter for name
        if specialty:
            params["filter[specialty]"] = specialty
        if city:
            params["filter[city]"] = city
        if available:
            params["filter[status]"] = "active"  # Only return active agents
        
        result = await self._make_request("GET", "users", params=params)
        return result.get("data", []) if isinstance(result, dict) else []
    
    async def get_agent(self, agent_id: str) -> Dict[str, Any]:
        """
        Get agent by ID (user in BoldTrail)
        
        Reference: https://developer.insiderealestate.com/publicv2/reference/get_v2-public-user-user-id
        
        Args:
            agent_id: Agent/User ID
            
        Returns:
            Agent data
        """
        result = await self._make_request("GET", f"user/{agent_id}")
        return result.get("data", result) if isinstance(result, dict) else result
    
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
        
        # BoldTrail API requires "details" field, not "note"
        payload = {"details": note}
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
    
    async def _fetch_xml_listings_feed(self) -> List[Dict[str, Any]]:
        """
        Fetch and parse all listings from BoldTrail XML feed
        
        This method accesses the full MLS listings feed, not just manual listings.
        Uses caching to avoid hitting the API on every request.
        
        Returns:
            List of all listings from the XML feed
        """
        global _listings_cache, _cache_timestamp
        
        current_time = time.time()
        
        # Return cached data if still valid
        if _listings_cache and _cache_timestamp:
            if (current_time - _cache_timestamp) < CACHE_DURATION:
                logger.info(f"Returning cached listings ({len(_listings_cache)} listings)")
                return _listings_cache
        
        if not settings.BOLDTRAIL_ZAPIER_KEY:
            logger.warning("BOLDTRAIL_ZAPIER_KEY not configured, cannot fetch XML feed")
            return []
        
        logger.info("Fetching fresh listings from BoldTrail XML feed")
        
        # XML feed URL format: https://api.kvcore.com/export/listings/{ZAPIER_KEY}/10
        # The /10 means include sold listings from last 10 days
        url = f"https://api.kvcore.com/export/listings/{settings.BOLDTRAIL_ZAPIER_KEY}/10"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=30.0)
                response.raise_for_status()
                
                # Parse XML
                root = ET.fromstring(response.text)
                listings = []
                
                # Find all listing elements - BoldTrail uses <Listing> with capital L
                # Try both lowercase and uppercase to be safe
                for listing_elem in root.findall('.//Listing') + root.findall('.//listing'):
                    listing = self._extract_listing_from_xml(listing_elem)
                    if listing:
                        listings.append(listing)
                
                logger.info(f"Fetched {len(listings)} listings from XML feed")
                
                # Update cache
                _listings_cache = listings
                _cache_timestamp = current_time
                
                return listings
                
        except httpx.RequestError as e:
            logger.exception(f"Failed to fetch XML feed: {str(e)}")
            raise BoldTrailError(
                message=f"Failed to fetch property listings: {str(e)}",
                details={"error": str(e)}
            )
        except ET.ParseError as e:
            logger.exception(f"Failed to parse XML feed: {str(e)}")
            raise BoldTrailError(
                message=f"Failed to parse property listings: {str(e)}",
                details={"error": str(e)}
            )
    
    def _extract_listing_from_xml(self, listing_elem: ET.Element) -> Optional[Dict[str, Any]]:
        """
        Extract property data from a single listing XML element
        
        Args:
            listing_elem: XML element for one listing
            
        Returns:
            Dictionary with property details or None if invalid
        """
        def get_text(path: str, default: str = "") -> str:
            """Helper to get text from XML element - supports nested paths"""
            # Try nested path first (e.g., "Location/StreetAddress")
            if "/" in path:
                parts = path.split("/")
                elem = listing_elem
                for part in parts:
                    elem = elem.find(part) if elem is not None else None
                    if elem is None:
                        break
                return elem.text if elem is not None and elem.text else default
            else:
                # Try direct child
                elem = listing_elem.find(path)
                return elem.text if elem is not None and elem.text else default
        
        def get_number(path: str, default: float = 0) -> float:
            """Helper to safely get number from XML element"""
            try:
                text = get_text(path, "0")
                return float(text) if text else default
            except (ValueError, TypeError):
                return default
        
        # Build listing dictionary - match actual BoldTrail XML structure
        # XML structure: <Listing><Location><StreetAddress>...</Location><ListingDetails><Price>...</ListingDetails>...
        listing = {
            # Basic Info - nested under <Location>
            "address": get_text("Location/StreetAddress") or get_text("StreetAddress") or get_text("address"),
            "city": get_text("Location/City") or get_text("City") or get_text("city"),
            "state": get_text("Location/State") or get_text("State") or get_text("state"),
            "zip": get_text("Location/Zip") or get_text("Zip") or get_text("zip") or get_text("zipCode"),
            "zipCode": get_text("Location/Zip") or get_text("Zip") or get_text("zip") or get_text("zipCode"),
            
            # Property Details - nested under <ListingDetails>
            "mlsNumber": get_text("ListingDetails/MlsId") or get_text("MlsId") or get_text("mlsNumber"),
            "mls_number": get_text("ListingDetails/MlsId") or get_text("MlsId") or get_text("mlsNumber"),
            "price": get_number("ListingDetails/Price") or get_number("Price") or get_number("price"),
            "status": get_text("ListingDetails/Status") or get_text("Status") or get_text("status") or "active",
            "listDate": get_text("ListingDetails/ListedDate") or get_text("ListedDate") or get_text("listDate"),
            
            # Property Details - nested under <BasicDetails>
            "bedrooms": int(get_number("BasicDetails/Bedrooms") or get_number("Bedrooms") or get_number("bedrooms") or 0),
            "bathrooms": float(get_number("BasicDetails/Bathrooms") or get_number("Bathrooms") or get_number("bathrooms") or 0),
            "squareFeet": get_number("BasicDetails/SquareFeet") or get_number("SquareFeet") or get_number("squareFeet") or 0,
            "propertyType": get_text("BasicDetails/PropertyType") or get_text("PropertyType") or get_text("propertyType"),
            
            # Description
            "description": get_text("BasicDetails/Description") or get_text("Description") or get_text("description"),
            
            # Agent - nested under <Agent> element
            "agentFirstName": get_text("Agent/FirstName") or "",
            "agentLastName": get_text("Agent/LastName") or "",
            "agentName": "",  # Will construct below
            "agentPhone": get_text("Agent/OfficeLineNumber") or get_text("Agent/Phone") or "",
            "agentEmail": get_text("Agent/EmailAddress") or get_text("Agent/Email") or "",
            "agentLicense": get_text("Agent/LicenseNum") or "",
            "agentKvcoreId": get_text("Agent/KvcoreId") or "",
            "agentKvcoreEmail": get_text("Agent/KvcoreEmail") or "",
            
            # Office/Brokerage - nested under <Office> element
            "brokerageName": get_text("Office/BrokerageName") or "",
            "brokerPhone": get_text("Office/BrokerPhone") or "",
            "brokerEmail": get_text("Office/BrokerEmail") or "",
            "brokerWebsite": get_text("Office/BrokerWebsite") or "",
            
            # Co-Agent (optional)
            "coAgentFirstName": get_text("CoAgent/FirstName") or "",
            "coAgentLastName": get_text("CoAgent/LastName") or "",
            "coAgentName": "",  # Will construct below
            "coAgentPhone": get_text("CoAgent/OfficeLineNumber") or get_text("CoAgent/Phone") or "",
            "coAgentEmail": get_text("CoAgent/EmailAddress") or get_text("CoAgent/Email") or "",
        }
        
        # Construct full agent names
        if listing["agentFirstName"] or listing["agentLastName"]:
            listing["agentName"] = f"{listing['agentFirstName']} {listing['agentLastName']}".strip()
        
        if listing["coAgentFirstName"] or listing["coAgentLastName"]:
            listing["coAgentName"] = f"{listing['coAgentFirstName']} {listing['coAgentLastName']}".strip()
        
        # Only return if we have at least an address and price
        if listing["address"] and listing["price"] > 0:
            return listing
        
        return None
    
    def _normalize_address(self, address: str) -> str:
        """
        Normalize address for comparison
        
        Args:
            address: Raw address string
            
        Returns:
            Normalized address (lowercase, no punctuation)
        """
        return (address.lower()
                .replace(",", "")
                .replace(".", "")
                .replace("street", "st")
                .replace("avenue", "ave")
                .replace("boulevard", "blvd")
                .replace("road", "rd")
                .replace("drive", "dr")
                .replace("lane", "ln")
                .replace("court", "ct")
                .strip())
    
    async def search_listings_from_xml(
        self,
        address: Optional[str] = None,
        city: Optional[str] = None,
        state: Optional[str] = None,
        zip_code: Optional[str] = None,
        mls_number: Optional[str] = None,
        property_type: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        bedrooms: Optional[int] = None,
        bathrooms: Optional[float] = None,
        status: Optional[str] = "active",
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search listings from XML feed by various criteria
        
        Args:
            address: Address to search for
            city: City filter
            state: State filter
            zip_code: ZIP code filter
            mls_number: MLS number filter
            property_type: Property type filter
            min_price: Minimum price
            max_price: Maximum price
            bedrooms: Exact number of bedrooms (not minimum)
            bathrooms: Exact number of bathrooms (not minimum)
            status: Listing status (active, pending, sold, etc.)
            limit: Maximum results to return
            
        Returns:
            List of matching listings
        """
        # Fetch all listings from XML feed
        all_listings = await self._fetch_xml_listings_feed()
        
        if not all_listings:
            return []
        
        # Filter listings
        matches = []
        
        for listing in all_listings:
            # Address filter (normalized partial match)
            if address:
                listing_addr = self._normalize_address(listing.get("address", ""))
                search_addr = self._normalize_address(address)
                if search_addr not in listing_addr and listing_addr not in search_addr:
                    continue
            
            # City filter (case-insensitive)
            if city and listing.get("city", "").lower() != city.lower():
                continue
            
            # State filter (case-insensitive)
            if state and listing.get("state", "").lower() != state.lower():
                continue
            
            # ZIP filter
            if zip_code and listing.get("zip", "") != zip_code and listing.get("zipCode", "") != zip_code:
                continue
            
            # MLS number filter
            if mls_number and listing.get("mlsNumber", "") != mls_number and listing.get("mls_number", "") != mls_number:
                continue
            
            # Property type filter (case-insensitive partial match)
            if property_type and property_type.lower() not in listing.get("propertyType", "").lower():
                continue
            
            # Price filters
            price = listing.get("price", 0)
            if min_price and price < min_price:
                continue
            if max_price and price > max_price:
                continue
            
            # Bedrooms filter (exact match)
            if bedrooms is not None and listing.get("bedrooms", 0) != bedrooms:
                continue
            
            # Bathrooms filter (exact match)
            if bathrooms is not None and listing.get("bathrooms", 0) != bathrooms:
                continue
            
            # Status filter (only show active listings by default)
            # Exception: If searching by specific address or MLS number, include pending/sold properties too
            if status and status.lower() == "active":
                listing_status = listing.get("status", "").lower()
                # If searching by specific address or MLS, be more lenient with status
                if address or mls_number:
                    # Include active, pending, and available properties when searching by address/MLS
                    if listing_status not in ["active", "available", "pending", "sold", ""]:
                        continue
                else:
                    # For general searches, only show active/available
                    if listing_status not in ["active", "available", ""]:
                        continue
            
            matches.append(listing)
        
        # Limit results
        return matches[:limit]
