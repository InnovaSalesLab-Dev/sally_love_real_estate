"""
Function: Check Property
Searches and retrieves property details from Stellar MLS
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from src.models.vapi_models import VapiResponse, CheckPropertyRequest
from src.models.mls_models import PropertySearchParams
from src.integrations.stellar_mls import StellarMLSClient
from src.utils.logger import get_logger
from src.utils.errors import StellarMLSError

logger = get_logger(__name__)
router = APIRouter()

mls_client = StellarMLSClient()


@router.post("/check_property")
async def check_property(request: CheckPropertyRequest) -> VapiResponse:
    """
    Search for properties in Stellar MLS based on criteria
    
    This function allows the voice agent to search for properties by:
    - Address, city, state, zip code
    - MLS number
    - Property type, price range, bedrooms, bathrooms
    
    Returns property details including availability, price, and features.
    """
    try:
        logger.info(f"Checking property with params: {request.model_dump()}")
        
        # Build search parameters
        search_params = PropertySearchParams(
            address=request.address,
            city=request.city,
            state=request.state or "FL",
            zip_code=request.zip_code,
            mls_number=request.mls_number,
            min_price=request.min_price,
            max_price=request.max_price,
            min_bedrooms=request.bedrooms,
            min_bathrooms=request.bathrooms,
            limit=5,  # Return top 5 matches
        )
        
        # Search MLS
        properties = await mls_client.search_properties(search_params)
        
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
                f"{prop.get('propertyType', 'home')} listed at ${prop.get('price'):,.0f}. "
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
        
    except StellarMLSError as e:
        logger.error(f"MLS error in check_property: {e.message}")
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

