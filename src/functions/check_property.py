"""
Function: Check Property
Searches and retrieves property details from BoldTrail CRM MLS Listings Feed
Uses the XML feed endpoint to access all active MLS listings (not just manual listings)
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from src.models.vapi_models import VapiResponse, CheckPropertyRequest
from src.integrations.boldtrail import BoldTrailClient
from src.utils.logger import get_logger
from src.utils.errors import BoldTrailError

logger = get_logger(__name__)
router = APIRouter()

crm_client = BoldTrailClient()


@router.post("/check_property")
async def check_property(request: CheckPropertyRequest) -> VapiResponse:
    """
    Search for properties in BoldTrail CRM from MLS listings feed based on criteria
    
    This function searches the full MLS listings feed (via XML feed) which includes
    all active listings, not just manually created ones. It allows the voice agent 
    to search for properties by:
    - Address, city, state, zip code
    - MLS number
    - Property type, price range, bedrooms, bathrooms
    
    Returns property details including availability, price, and features.
    
    Uses BoldTrail XML Feed: https://api.kvcore.com/export/listings/{ZAPIER_KEY}/10
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
            min_bedrooms=request.bedrooms,
            min_bathrooms=request.bathrooms,
            status="active",  # Only show active/available listings
            limit=5  # Return top 5 matches
        )
        
        if not properties:
            return VapiResponse(
                success=True,
                message="No properties found matching your criteria. Would you like to adjust your search?",
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
            
            message = (
                f"I found a property at {prop.get('address')}, {prop.get('city')}. "
                f"It's a {prop.get('bedrooms', 0)} bedroom, {prop.get('bathrooms', 0)} bathroom "
                f"{prop_type} listed at ${prop.get('price', 0):,.0f}.{status_note}"
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
            message = (
                f"I found {len(properties)} properties matching your criteria. "
                f"The prices range from ${min(p.get('price', 0) for p in properties):,.0f} "
                f"to ${max(p.get('price', 0) for p in properties):,.0f}. "
                f"Would you like me to tell you about each one?"
            )
        
        # Include agent and transfer info in response data
        response_data = {
            "count": len(properties),
            "search_params": request.model_dump(exclude_none=True)
        }
        
        # Add agent info for single property result (for transfer capability)
        if len(properties) == 1:
            prop = properties[0]
            if prop.get('agentName'):
                response_data["listing_agent"] = {
                    "name": prop.get('agentName', ''),
                    "phone": prop.get('agentPhone', ''),
                    "email": prop.get('agentEmail', ''),
                    "kvcore_id": prop.get('agentKvcoreId', '')
                }
                # Add transfer phone if available (for route_to_agent function)
                if prop.get('agentPhone'):
                    response_data["transfer_phone"] = prop.get('agentPhone')
            
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

