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
from src.models.crm_models import Contact, BuyerLead, SellerLead

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
        
        Reference: https://developer.insiderealestate.com/publicv2/reference/get_v2-public-contact-contact-id
        
        Args:
            contact_id: Contact ID
            
        Returns:
            Contact data
        """
        result = await self._make_request("GET", f"contact/{contact_id}")
        return result.get("data", result) if isinstance(result, dict) else result
    
    async def search_contacts(
        self,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        name: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for contacts
        
        Reference: https://developer.insiderealestate.com/publicv2/reference/get_v2-public-contacts
        Uses GET /contacts with query parameters for filtering
        
        API Parameters (from official docs):
        - filter[email] - Search by email (exact or like match)
        - filter[first_name] - Search by first name (exact or like match)
        - filter[last_name] - Search by last name (exact or like match)
        - search - General search parameter (for name)
        
        Note: Phone filtering is not available in the API. Use email or name instead.
        
        Args:
            phone: Phone number (NOTE: Not supported by API - will be ignored)
            email: Email address (uses filter[email])
            name: Contact name (uses search parameter)
            first_name: First name (uses filter[first_name])
            last_name: Last name (uses filter[last_name])
            
        Returns:
            List of matching contacts
        """
        params = {}
        
        # Email filter (documented parameter)
        if email:
            params["filter[email]"] = email
        
        # Name filters (documented parameters)
        if first_name:
            params["filter[first_name]"] = first_name
        if last_name:
            params["filter[last_name]"] = last_name
        
        # General search parameter (for name if first/last not provided)
        if name and not first_name and not last_name:
            params["search"] = name
        
        # Phone is not supported by API - log warning if provided
        if phone:
            logger.warning(f"Phone search not supported by BoldTrail API. Phone parameter ignored: {phone}")
        
        result = await self._make_request("GET", "contacts", params=params)
        return result.get("data", []) if isinstance(result, dict) else []
    
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
        
        # Note: Buyer preference details (property type, location, price range, etc.) are saved
        # via separate add_note() endpoint call in create_buyer_lead.py after contact creation.
        # The POST /v2/public/contact endpoint does not accept a notes field.
        
        # Create contact with buyer lead information
        # API Documentation: https://developer.insiderealestate.com/publicv2/reference/post_v2-public-contact
        # Field names are snake_case, not camelCase!
        
        # Convert phone to integer (cell_phone_1 expects integer)
        phone_int = None
        try:
            # Remove all non-digit characters and convert to integer
            phone_digits = ''.join(filter(str.isdigit, buyer_lead.contact.phone))
            if phone_digits:
                phone_int = int(phone_digits)
        except (ValueError, AttributeError):
            logger.warning(f"Could not convert phone to integer: {buyer_lead.contact.phone}")
            # If conversion fails, we'll skip it - API may accept it anyway
        
        # Build payload with correct field names (snake_case)
        # Note: email is required by API, but if not provided, we'll use a placeholder
        email_value = buyer_lead.contact.email
        if not email_value:
            # Generate a placeholder email if not provided (API requires email field)
            # Format: noemail-{timestamp}@sallyloverealestate.ai
            email_value = f"noemail-{int(time.time())}@sallyloverealestate.ai"
            logger.warning(f"Email not provided for buyer lead, using placeholder: {email_value}")
        
        payload = {
            "first_name": buyer_lead.contact.first_name,  # Required
            "last_name": buyer_lead.contact.last_name or "",  # Required - allow empty string
            "email": email_value,  # Required by API
            "deal_type": "buyer",  # String of strings - lowercase
            "source": buyer_lead.contact.source or "AI Concierge",
            "status": 0,  # 0 = New (required integer enum: 0=New, 1=Client, 2=Closed, 3=Sphere, 4=Active, 5=Contract, 6=Archived, 7=Prospect)
        }
        
        # Add phone if available (integer)
        if phone_int:
            payload["cell_phone_1"] = phone_int
        
        # Add address fields if provided (using primary_* prefix)
        if buyer_lead.contact.address:
            payload["primary_address"] = buyer_lead.contact.address
        if buyer_lead.contact.city:
            payload["primary_city"] = buyer_lead.contact.city
        if buyer_lead.contact.state:
            payload["primary_state"] = buyer_lead.contact.state
        if buyer_lead.contact.zip_code:
            payload["primary_zip"] = buyer_lead.contact.zip_code
        
        # Add capture_method to identify this as an AI voice agent lead
        payload["capture_method"] = "AI Voice Agent - Concierge"
        
        # Log the complete payload for debugging (without sensitive phone/email data)
        payload_log = {k: ('***' if k in ['cell_phone_1', 'email'] else v) for k, v in payload.items()}
        logger.info(f"Creating buyer lead - Full payload fields: {list(payload.keys())}")
        logger.info(f"Creating buyer lead payload (sanitized): {payload_log}")
        
        result = await self._make_request("POST", "contact", data=payload)
        
        # Log what was actually saved and extract contact ID properly
        if result and isinstance(result, dict):
            # Try multiple ways to extract contact ID (API response format may vary)
            # Try multiple paths independently to handle various API response formats
            saved_id = result.get("id")
            if not saved_id and isinstance(result.get("data"), dict):
                saved_id = result.get("data", {}).get("id")
            if not saved_id and isinstance(result.get("contact"), dict):
                saved_id = result.get("contact", {}).get("id")
            logger.info(f"Buyer lead created successfully with ID: {saved_id}")
            # Log returned fields to see what API accepted
            returned_fields = list(result.keys()) if isinstance(result, dict) else []
            logger.info(f"API response fields: {returned_fields}")
            
            # Ensure ID is in result for caller to use
            if saved_id and "id" not in result:
                result["id"] = saved_id
        
        return result
    
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
        
        # Note: Property details (address, type, bedrooms, bathrooms, square feet, etc.) are saved
        # via separate add_note() endpoint call in create_seller_lead.py after contact creation.
        # The POST /v2/public/contact endpoint does not accept a notes field.
        
        # Create contact with seller lead information
        # API Documentation: https://developer.insiderealestate.com/publicv2/reference/post_v2-public-contact
        # Field names are snake_case, not camelCase!
        
        # Convert phone to integer (cell_phone_1 expects integer)
        phone_int = None
        try:
            # Remove all non-digit characters and convert to integer
            phone_digits = ''.join(filter(str.isdigit, seller_lead.contact.phone))
            if phone_digits:
                phone_int = int(phone_digits)
        except (ValueError, AttributeError):
            logger.warning(f"Could not convert phone to integer: {seller_lead.contact.phone}")
        
        # Handle required email field
        email_value = seller_lead.contact.email
        if not email_value:
            # Generate a placeholder email if not provided (API requires email field)
            email_value = f"noemail-{int(time.time())}@sallyloverealestate.ai"
            logger.warning(f"Email not provided for seller lead, using placeholder: {email_value}")
        
        # Build payload with correct field names (snake_case)
        payload = {
            "first_name": seller_lead.contact.first_name,  # Required
            "last_name": seller_lead.contact.last_name or "",  # Required
            "email": email_value,  # Required by API
            "deal_type": "seller",  # String of strings - lowercase
            "primary_address": seller_lead.property_address,
            "primary_city": seller_lead.city,
            "primary_state": seller_lead.state,
            "primary_zip": seller_lead.zip_code,
            "status": 0,  # 0 = New (integer enum)
            "source": seller_lead.contact.source or "AI Concierge",
            "capture_method": "AI Voice Agent - Concierge",
        }
        
        # Add phone if available (integer)
        if phone_int:
            payload["cell_phone_1"] = phone_int
        
        # Remove None values
        payload = {k: v for k, v in payload.items() if v is not None}
        
        # Log the complete payload for debugging (without sensitive phone/email data)
        payload_log = {k: ('***' if k in ['cell_phone_1', 'email'] else v) for k, v in payload.items()}
        logger.info(f"Creating seller lead - Full payload fields: {list(payload.keys())}")
        logger.info(f"Creating seller lead payload (sanitized): {payload_log}")
        
        result = await self._make_request("POST", "contact", data=payload)
        
        # Log what was actually saved and extract contact ID properly
        if result and isinstance(result, dict):
            # Try multiple ways to extract contact ID (API response format may vary)
            # Try multiple paths independently to handle various API response formats
            saved_id = result.get("id")
            if not saved_id and isinstance(result.get("data"), dict):
                saved_id = result.get("data", {}).get("id")
            if not saved_id and isinstance(result.get("contact"), dict):
                saved_id = result.get("contact", {}).get("id")
            logger.info(f"Seller lead created successfully with ID: {saved_id}")
            # Log returned fields to see what API accepted
            returned_fields = list(result.keys()) if isinstance(result, dict) else []
            logger.info(f"API response fields: {returned_fields}")
            
            # Ensure ID is in result for caller to use
            if saved_id and "id" not in result:
                result["id"] = saved_id
        
        return result
    
    async def get_agents(
        self,
        name: Optional[str] = None,
        specialty: Optional[str] = None,
        city: Optional[str] = None,
        available: bool = True,
        status: Optional[int] = None,
        offices: Optional[List[int]] = None,
        teams: Optional[List[int]] = None,
        mls_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get list of agents (users in BoldTrail)
        
        Reference: https://developer.insiderealestate.com/publicv2/reference/get_v2-public-users
        
        API Query Parameters (from official docs):
        - offices[] (integer array): Filter by office IDs
        - lenders[] (integer array): Filter by lender IDs
        - teams[] (integer array): Filter by team IDs
        - since (string, datetime): Filter users updated after date
        - before (string, datetime): Filter users updated before date
        - status (integer): 1 = Active, 0 = Roster Only
        - mls_id (string): Filter by MLS ID(s) - comma-separated for multiple
        
        Note: The API does NOT support searching by name, specialty, or city directly.
        If name/specialty/city are provided, we filter results in code after fetching.
        
        Args:
            name: Agent name (filtered in code, not by API)
            specialty: Agent specialty (filtered in code, not by API)
            city: Service area (filtered in code, not by API)
            available: Filter by availability (uses status=1 if True)
            status: User status - 1=Active, 0=Roster Only (default: 1 if available=True)
            offices: List of office IDs to filter by
            teams: List of team IDs to filter by
            mls_id: MLS ID(s) to filter by (comma-separated string)
            
        Returns:
            List of agents (filtered by name/specialty/city if provided)
        """
        params = {}
        
        # API-supported filters
        if status is not None:
            params["status"] = status
        elif available:
            params["status"] = 1  # 1 = Active (default when available=True)
        
        if offices:
            # API expects offices[] as array parameter (multiple values)
            # httpx will format this as offices[]=1&offices[]=2 when passed as list
            params["offices[]"] = offices
        
        if teams:
            # API expects teams[] as array parameter (multiple values)
            # httpx will format this as teams[]=1&teams[]=2 when passed as list
            params["teams[]"] = teams
        
        if mls_id:
            params["mls_id"] = mls_id
        
        # Get agents from API
        result = await self._make_request("GET", "users", params=params)
        agents = result.get("data", []) if isinstance(result, dict) else []
        
        # Filter by name, specialty, or city in code (API doesn't support these)
        filtered_agents = agents
        
        if name:
            name_lower = name.lower()
            filtered_agents = [
                agent for agent in filtered_agents
                if name_lower in agent.get("firstName", "").lower() or
                   name_lower in agent.get("lastName", "").lower() or
                   name_lower in agent.get("name", "").lower()
            ]
            logger.info(f"Filtered {len(agents)} agents to {len(filtered_agents)} by name '{name}'")
        
        if specialty and filtered_agents:
            specialty_lower = specialty.lower()
            filtered_agents = [
                agent for agent in filtered_agents
                if specialty_lower in str(agent.get("specialties", [])).lower() or
                   specialty_lower in str(agent.get("specialty", "")).lower()
            ]
            logger.info(f"Filtered to {len(filtered_agents)} agents by specialty '{specialty}'")
        
        if city and filtered_agents:
            city_lower = city.lower()
            filtered_agents = [
                agent for agent in filtered_agents
                if city_lower in str(agent.get("serviceAreas", [])).lower() or
                   city_lower in str(agent.get("city", "")).lower() or
                   city_lower in str(agent.get("serviceArea", "")).lower()
            ]
            logger.info(f"Filtered to {len(filtered_agents)} agents by city '{city}'")
        
        return filtered_agents
    
    async def get_agent(self, agent_id: str) -> Dict[str, Any]:
        """
        Get agent by ID (user in BoldTrail)
        
        Reference: https://developer.insiderealestate.com/publicv2/reference/get_v2-public-user-user-id
        
        API Parameters:
        - user_id (integer, required): User ID in URL path: GET /v2/public/user/{user_id}
        
        Args:
            agent_id: Agent/User ID (integer as string - will be used in URL path)
            
        Returns:
            Agent data (user details from BoldTrail)
        """
        logger.info(f"Getting agent details for ID: {agent_id}")
        result = await self._make_request("GET", f"user/{agent_id}")
        return result.get("data", result) if isinstance(result, dict) else result
    
    async def update_contact(
        self,
        contact_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update contact information
        
        Reference: https://developer.insiderealestate.com/publicv2/reference/put_v2-public-contact-contact-id
        
        API Parameters (from official docs - all optional, use snake_case):
        - first_name, last_name, email
        - cell_phone_1 (integer), home_phone (integer), work_phone (integer), fax (string)
        - deal_type (string of strings: "buyer", "seller", "renter")
        - primary_address, primary_city, primary_state, primary_zip
        - status (integer enum: 0=New, 1=Client, 2=Closed, 3=Sphere, 4=Active, 5=Contract, 6=Archived, 7=Prospect)
        - source, capture_method
        - email_optin, phone_on, text_on (integers: 0 or 1)
        - rating (integer: 0-5)
        - assigned_agent_id, assigned_agent_external_id (strings)
        - avg_price, avg_beds, avg_baths (integers)
        - poi_address, poi_city, poi_state, poi_zip (property of interest)
        - spouse_first_name, spouse_last_name, spouse_phone, spouse_title
        - title, birthday, gender, second_email
        - external_vendor_id, active_mls_id
        - skip_new_notification (boolean)
        - last_closing_date (string)
        
        Note: Field names must be snake_case (e.g., first_name, cell_phone_1, primary_address)
        Note: Phone fields (cell_phone_1, home_phone, work_phone) must be integers (digits only)
        
        Args:
            contact_id: Contact ID (integer, required in URL path)
            updates: Dictionary of fields to update (use snake_case field names)
            
        Returns:
            Updated contact data
        """
        logger.info(f"Updating contact: {contact_id}")
        
        # Convert phone fields to integers if they're strings
        phone_fields = ["cell_phone_1", "home_phone", "work_phone"]
        for field in phone_fields:
            if field in updates and updates[field] is not None:
                try:
                    if isinstance(updates[field], str):
                        # Remove all non-digit characters and convert to integer
                        phone_digits = ''.join(filter(str.isdigit, str(updates[field])))
                        if phone_digits:
                            updates[field] = int(phone_digits)
                        else:
                            # If no digits found, remove the field
                            del updates[field]
                            logger.warning(f"Could not convert {field} to integer, removing from update")
                except (ValueError, TypeError):
                    logger.warning(f"Could not convert {field} to integer: {updates[field]}")
                    del updates[field]
        
        # Remove None values
        updates = {k: v for k, v in updates.items() if v is not None}
        
        result = await self._make_request("PUT", f"contact/{contact_id}", data=updates)
        return result.get("data", result) if isinstance(result, dict) else result
    
    async def add_note(
        self,
        contact_id: str,
        note: str,
        title: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add a note to a contact
        
        Reference: https://developer.insiderealestate.com/publicv2/reference/put_v2-public-contact-contact-id-action-note
        
        API Parameters:
        - details (string, required): The content/body of the note
        - title (string, optional): The title of the note
        - date (date-time, optional): Date to specify with the note. Default is current date/time
        - action_owner_user_id (string, optional): Owner user id (company admin only)
        
        Args:
            contact_id: Contact ID (integer, required)
            note: Note content/body (will be sent as "details")
            title: Note title (optional)
            
        Returns:
            Created note data
        """
        logger.info(f"Adding note to contact: {contact_id}")
        
        # BoldTrail API expects "details" field for note content, "title" for note title
        payload = {"details": note}
        if title:
            payload["title"] = title
        
        return await self._make_request("PUT", f"contact/{contact_id}/action/note", data=payload)
    
    async def log_call(
        self,
        contact_id: str,
        direction: str = "inbound",
        result: Optional[int] = None,
        notes: Optional[str] = None,
        date: Optional[str] = None,
        recording_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Log a call activity to a contact
        
        Reference: https://developer.insiderealestate.com/publicv2/reference/put_v2-public-contact-contact-id-action-call
        
        API Parameters (from official docs):
        - direction (string, optional): 'outbound' or 'inbound'. Defaults to 'outbound' if not specified
        - result (integer enum, optional): 1=Bad Number, 2=Not Home, 3=Contacted. Defaults to 3 if not specified
        - notes (string, optional): Notes about the call
        - date (date-time, optional): Date the call occurred. Default is current date/time
        - recording_url (string, optional): URL to the call recording audio file
        - action_owner_user_id (string, optional): Owner user id (company admin only)
        
        Args:
            contact_id: Contact ID (integer, required in URL path)
            direction: Call direction - 'inbound' or 'outbound' (default: 'inbound')
            result: Call result - 1=Bad Number, 2=Not Home, 3=Contacted (default: 3)
            notes: Notes about the call
            date: Date the call occurred (date-time format, optional)
            recording_url: URL to call recording (optional)
            
        Returns:
            Created call log data
        """
        logger.info(f"Logging call for contact: {contact_id}, direction: {direction}")
        
        # Normalize direction to lowercase
        direction_lower = direction.lower() if direction else "inbound"
        if direction_lower not in ["inbound", "outbound"]:
            logger.warning(f"Invalid direction '{direction}', defaulting to 'inbound'")
            direction_lower = "inbound"
        
        # Build payload with correct field names
        payload = {
            "direction": direction_lower,
            "notes": notes
        }
        
        # Add result if provided (must be 1, 2, or 3 per API docs)
        if result is not None:
            if result in [1, 2, 3]:
                payload["result"] = result
            else:
                logger.warning(f"Invalid result value {result}, must be 1 (Bad Number), 2 (Not Home), or 3 (Contacted). Using default (3)")
                payload["result"] = 3
        else:
            # Default to 3 (Contacted) if not specified
            payload["result"] = 3
        
        # Add optional fields
        if date:
            payload["date"] = date
        if recording_url:
            payload["recording_url"] = recording_url
        
        # Remove None values
        payload = {k: v for k, v in payload.items() if v is not None}
        
        return await self._make_request("PUT", f"contact/{contact_id}/action/call", data=payload)
    
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
    
    async def search_manual_listings(
        self,
        address: Optional[str] = None,
        city: Optional[str] = None,
        state: Optional[str] = None,
        zip_code: Optional[str] = None,
        property_type: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        bedrooms: Optional[int] = None,
        bathrooms: Optional[float] = None,
        status: Optional[str] = "active",
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search manual listings from BoldTrail API endpoint
        
        Uses: GET /v2/public/manuallistings
        Reference: https://developer.insiderealestate.com/publicv2/reference/get_v2-public-manuallistings
        
        This searches properties that are manually added to BoldTrail,
        which may not be in the MLS XML feed.
        
        Args:
            address: Address to search for
            city: City filter
            state: State filter
            zip_code: ZIP code filter
            property_type: Property type filter
            min_price: Minimum price
            max_price: Maximum price
            bedrooms: Minimum number of bedrooms
            bathrooms: Minimum number of bathrooms
            status: Listing status (active, pending, sold, etc.)
            limit: Maximum results to return
            
        Returns:
            List of matching manual listings
        """
        logger.info(f"Searching manual listings with address={address}, city={city}")
        
        # Build query parameters
        params = {}
        
        # API supports filtering by status
        if status:
            params["status"] = status
        
        # Get all manual listings (API has limited filtering options)
        result = await self._make_request("GET", "manuallistings", params=params)
        
        # Extract listings from response
        listings = result.get("data", []) if isinstance(result, dict) else []
        
        if not listings:
            logger.info("No manual listings found")
            return []
        
        logger.info(f"Retrieved {len(listings)} manual listings, applying filters")
        
        # Apply filters in code (API has limited query parameter support)
        matches = []
        
        for listing in listings:
            # Address filter (case-insensitive partial match)
            if address:
                listing_addr = str(listing.get("address", "")).lower()
                search_addr = address.lower()
                if search_addr not in listing_addr and listing_addr not in search_addr:
                    continue
            
            # City filter (case-insensitive)
            if city:
                listing_city = str(listing.get("city", "")).lower()
                if city.lower() != listing_city:
                    continue
            
            # State filter (case-insensitive)
            if state:
                listing_state = str(listing.get("state", "")).lower()
                if state.lower() != listing_state:
                    continue
            
            # ZIP filter
            if zip_code:
                listing_zip = str(listing.get("zipCode", "")) or str(listing.get("zip_code", ""))
                if zip_code != listing_zip:
                    continue
            
            # Property type filter (case-insensitive partial match)
            if property_type:
                listing_type = str(listing.get("propertyType", "")).lower()
                if property_type.lower() not in listing_type:
                    continue
            
            # Price filters
            price = float(listing.get("price", 0) or 0)
            if min_price and price < min_price:
                continue
            if max_price and price > max_price:
                continue
            
            # Bedrooms filter (minimum)
            if bedrooms is not None:
                listing_beds = int(listing.get("bedrooms", 0) or 0)
                if listing_beds < bedrooms:
                    continue
            
            # Bathrooms filter (minimum)
            if bathrooms is not None:
                listing_baths = float(listing.get("bathrooms", 0) or 0)
                if listing_baths < bathrooms:
                    continue
            
            # Normalize listing data to match XML feed format
            normalized = {
                "address": listing.get("address", ""),
                "city": listing.get("city", ""),
                "state": listing.get("state", ""),
                "zip": listing.get("zipCode") or listing.get("zip_code", ""),
                "zipCode": listing.get("zipCode") or listing.get("zip_code", ""),
                "mlsNumber": listing.get("mlsNumber") or listing.get("mls_number", "N/A"),
                "mls_number": listing.get("mlsNumber") or listing.get("mls_number", "N/A"),
                "price": price,
                "status": listing.get("status", "active"),
                "listDate": listing.get("listDate") or listing.get("list_date", ""),
                "bedrooms": int(listing.get("bedrooms", 0) or 0),
                "bathrooms": float(listing.get("bathrooms", 0) or 0),
                "squareFeet": int(listing.get("squareFeet", 0) or listing.get("square_feet", 0) or 0),
                "propertyType": listing.get("propertyType") or listing.get("property_type", ""),
                "description": listing.get("description", ""),
                "agentName": listing.get("agentName", ""),
                "agentPhone": listing.get("agentPhone", ""),
                "agentEmail": listing.get("agentEmail", ""),
                "source": "manual_listing"  # Flag to indicate this came from manual listings
            }
            
            matches.append(normalized)
        
        logger.info(f"Found {len(matches)} manual listings matching criteria")
        
        # Limit results
        return matches[:limit]
    
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
