"""
Function: Check Property
Searches and retrieves property details from BoldTrail CRM
Searches both MLS listings (XML feed) and manual listings (API endpoint)
Uses fallback strategy: XML feed first, then manual listings if no results found
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from src.models.vapi_models import VapiResponse, CheckPropertyRequest
from src.config.settings import settings
from src.integrations.boldtrail import BoldTrailClient
from src.utils.logger import get_logger
from src.utils.errors import BoldTrailError
from src.utils.roster import find_agent_by_name, get_any_agent
from src.utils.speech_format import format_spoken_address, format_spoken_price

logger = get_logger(__name__)
router = APIRouter()

crm_client = BoldTrailClient()


@router.post("/check_property")
async def check_property(request: CheckPropertyRequest) -> VapiResponse:
    """
    Search for properties in BoldTrail CRM from multiple sources
    
    This function searches properties in this order:
    1. First: MLS listings feed (via XML feed) - includes all active MLS listings
    2. Fallback: Manual listings (via API) - includes properties manually added to BoldTrail
    
    Search criteria:
    - Address, city, state, zip code
    - MLS number
    - Property type, price range, bedrooms, bathrooms
    
    Returns property details including availability, price, and features.
    
    Data sources:
    - XML Feed: https://api.kvcore.com/export/listings/{ZAPIER_KEY}/10
    - Manual Listings: GET /v2/public/manuallistings
    """
    try:
        logger.info(f"Checking property with params: {request.model_dump()}")
        
        # Validate that at least one search parameter is provided
        has_search_criteria = any([
            request.address,
            request.city,
            request.zip_code,
            request.mls_number,
            request.property_type,
            request.min_price,
            request.max_price,
            request.bedrooms,
            request.bathrooms
        ])
        
        if not has_search_criteria:
            return VapiResponse(
                success=False,
                message="I need at least one search criteria to look up properties. Please provide an address, city, ZIP code, MLS number, or property preferences like price range or number of bedrooms.",
                error="No search criteria provided",
                results=[],
                data={"search_params": {}}
            )
        
        # Search listings from XML feed (includes all MLS listings)
        properties = await crm_client.search_listings_from_xml(
            address=request.address,
            city=request.city,
            state=request.state or "FL",
            zip_code=request.zip_code,
            mls_number=request.mls_number,
            property_type=request.property_type,
            min_price=request.min_price,
            max_price=request.max_price,
            bedrooms=request.bedrooms,
            bathrooms=request.bathrooms,
            status="active",  # Only show active/available listings
            limit=5  # Return top 5 matches
        )
        
        # Fallback: If no results from XML feed, try manual listings
        if not properties:
            logger.info("No properties found in XML feed, trying manual listings...")
            properties = await crm_client.search_manual_listings(
                address=request.address,
                city=request.city,
                state=request.state or "FL",
                zip_code=request.zip_code,
                property_type=request.property_type,
                min_price=request.min_price,
                max_price=request.max_price,
                bedrooms=request.bedrooms,
                bathrooms=request.bathrooms,
                status="active",
                limit=5
            )
            
            if properties:
                logger.info(f"Found {len(properties)} properties in manual listings")
        
        if not properties:
            # Check if we have enough location info to avoid asking for zip again
            has_zip = bool(request.zip_code)
            has_city = bool(request.city)
            has_full_address = bool(request.address)
            
            if has_zip or (has_city and has_full_address):
                # We have enough location info, don't ask for zip again
                message = "No properties found matching your criteria. Would you like to adjust your search, or should I connect you with an agent who can help?"
            else:
                # Missing location info
                message = "No properties found. Do you have the city and zip code, or an MLS number?"
            
            return VapiResponse(
                success=True,
                message=message,
                results=[]
            )
        
        # Format results for voice response
        if len(properties) == 1:
            prop = properties[0]
            # Handle both possible field names from XML feed
            mls_num = prop.get('mlsNumber') or prop.get('mls_number', 'N/A')
            prop_type = prop.get('propertyType') or prop.get('property_type', 'home')
            agent_name = prop.get('agentName', '').strip()
            agent_phone = prop.get('agentPhone', '').strip()
            
            # Check status and include in message if not active
            prop_status = prop.get('status', '').lower()
            status_note = ""
            if prop_status in ['pending', 'under contract']:
                status_note = " This property is currently under contract, but they may be accepting backup offers. "
            elif prop_status == 'sold':
                status_note = " I should note that this property has been sold. "
            
            # Format address and price for speech
            spoken_address = format_spoken_address(prop.get('address', ''))
            spoken_price = format_spoken_price(prop.get('price'))
            
            message = (
                f"I found a property at {spoken_address}, {prop.get('city')}. "
                f"It's a {prop.get('bedrooms', 0)} bedroom, {prop.get('bathrooms', 0)} bathroom "
                f"{prop_type} listed at {spoken_price}.{status_note}"
            )
            if mls_num and mls_num != 'N/A':
                message += f"The MLS number is {mls_num}. "
            
            # Include agent information if available
            if agent_name:
                message += f"The listing agent is {agent_name}. "
                if agent_phone:
                    message += f"Would you like me to connect you with {agent_name}?"
                else:
                    message += "Would you like more details about this property?"
            else:
                message += "Would you like more details about this property?"
        else:
            # Format price range for speech
            min_price_spoken = format_spoken_price(min(p.get('price', 0) for p in properties))
            max_price_spoken = format_spoken_price(max(p.get('price', 0) for p in properties))
            
            message = (
                f"I found {len(properties)} properties matching your criteria. "
                f"The prices range from {min_price_spoken} "
                f"to {max_price_spoken}. "
                f"Would you like me to tell you about each one?"
            )
        
        # Include agent and transfer info in response data
        response_data = {
            "count": len(properties),
            "search_params": request.model_dump(exclude_none=True)
        }
        
        # Add agent info for single property result (for transfer capability)
        # Validate against roster: use roster phone when agent matches; else fallback to any roster agent
        if len(properties) == 1:
            prop = properties[0]
            xml_agent_name = (prop.get('agentName') or '').strip()
            xml_agent_phone = (prop.get('agentPhone') or '').strip()
            roster_path = settings.AGENT_ROSTER_PATH or None

            roster_agent = find_agent_by_name(xml_agent_name, roster_path) if xml_agent_name else None
            transfer_phone = None
            agent_name = xml_agent_name
            agent_email = prop.get('agentEmail', '')

            if roster_agent:
                agent_name = roster_agent.get('name') or xml_agent_name
                transfer_phone = roster_agent.get('cell_phone') or roster_agent.get('phone') or ''
                agent_email = roster_agent.get('email') or agent_email
            else:
                fallback = get_any_agent(roster_path)
                if fallback:
                    agent_name = fallback.get('name') or xml_agent_name or 'an agent'
                    transfer_phone = fallback.get('cell_phone') or fallback.get('phone') or ''
                    agent_email = fallback.get('email') or ''
                    if xml_agent_name:
                        logger.info(f"Listing agent '{xml_agent_name}' not in roster; using fallback: {agent_name}")

            if agent_name:
                response_data["listing_agent"] = {
                    "name": agent_name,
                    "phone": transfer_phone or xml_agent_phone,
                    "email": agent_email,
                    "kvcore_id": prop.get('agentKvcoreId', '')
                }
                if transfer_phone or xml_agent_phone:
                    response_data["transfer_phone"] = transfer_phone or xml_agent_phone

            # Include broker/office info as fallback (Jeff's contact)
            if prop.get('brokerPhone'):
                response_data["broker"] = {
                    "name": prop.get('brokerageName', 'Sally Love Real Estate'),
                    "phone": prop.get('brokerPhone', ''),
                    "email": prop.get('brokerEmail', '')
                }
        
        return VapiResponse(
            success=True,
            message=message,
            results=properties,
            data=response_data
        )
        
    except BoldTrailError as e:
        logger.error(f"BoldTrail error in check_property: {e.message}")
        return VapiResponse(
            success=False,
            error="I'm having trouble accessing the property listings right now. Could you try again in a moment?",
            message=e.message
        )
    
    except Exception as e:
        logger.exception(f"Error in check_property: {str(e)}")
        return VapiResponse(
            success=False,
            error="I encountered an error while searching for properties. Let me connect you with an agent who can help.",
            message=str(e)
        )

