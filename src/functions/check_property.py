"""
Function: Check Property
Searches and retrieves property details from BoldTrail CRM Manual Listings
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
    Search for properties in BoldTrail CRM Manual Listings based on criteria
    
    This function allows the voice agent to search for properties by:
    - Address, city, state, zip code
    - MLS number (via specific listing lookup)
    - Property type, price range, bedrooms, bathrooms
    
    Returns property details including availability, price, and features.
    
    API Reference: https://developer.insiderealestate.com/publicv2/reference/get_v2-public-manuallistings
    """
    try:
        logger.info(f"Checking property with params: {request.model_dump()}")
        
        # Search manual listings by criteria
        # Note: MLS number is passed as a filter, not as a direct lookup
        # because get_manual_listing() expects BoldTrail's internal listing ID, not MLS number
        properties = await crm_client.get_manual_listings(
            property_type=request.property_type,
            city=request.city,
            state=request.state or "FL",
            address=request.address,
            zip_code=request.zip_code,
            mls_number=request.mls_number,
            status="active",  # Only show active/available listings
            min_price=request.min_price,
            max_price=request.max_price,
            min_bedrooms=request.bedrooms,
            min_bathrooms=request.bathrooms,
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
            message = (
                f"I found a property at {prop.get('address')}, {prop.get('city')}. "
                f"It's a {prop.get('bedrooms')} bedroom, {prop.get('bathrooms')} bathroom "
                f"{prop.get('propertyType', 'home')} listed at ${prop.get('price', 0):,.0f}. "
                f"The MLS number is {prop.get('mlsNumber')}. "
                f"Would you like more details about this property?"
            )
        else:
            message = (
                f"I found {len(properties)} properties matching your criteria. "
                f"The prices range from ${min(p.get('price', 0) for p in properties):,.0f} "
                f"to ${max(p.get('price', 0) for p in properties):,.0f}. "
                f"Would you like me to tell you about each one?"
            )
        
        return VapiResponse(
            success=True,
            message=message,
            results=properties,
            data={
                "count": len(properties),
                "search_params": request.model_dump(exclude_none=True)
            }
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

