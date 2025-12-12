"""
Stellar MLS API client
"""

import httpx
from typing import Dict, Any, Optional, List
from src.config.settings import settings
from src.utils.logger import get_logger
from src.utils.errors import StellarMLSError
from src.models.mls_models import Property, PropertySearchParams, PropertyDetails

logger = get_logger(__name__)


class StellarMLSClient:
    """Client for Stellar MLS API"""
    
    def __init__(self):
        self.username = settings.STELLAR_MLS_USERNAME
        self.password = settings.STELLAR_MLS_PASSWORD
        self.base_url = settings.STELLAR_MLS_API_URL
        self.auth_token: Optional[str] = None
    
    async def _authenticate(self) -> str:
        """
        Authenticate and get access token
        
        Returns:
            Access token
            
        Raises:
            StellarMLSError: If authentication fails
        """
        if self.auth_token:
            return self.auth_token
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/auth/token",
                    json={
                        "username": self.username,
                        "password": self.password,
                    },
                    timeout=30.0,
                )
                
                if response.status_code >= 400:
                    raise StellarMLSError(
                        message="MLS authentication failed",
                        status_code=response.status_code,
                    )
                
                data = response.json()
                self.auth_token = data.get("access_token")
                return self.auth_token
                
        except httpx.RequestError as e:
            logger.exception(f"MLS authentication failed: {str(e)}")
            raise StellarMLSError(
                message=f"Failed to authenticate with MLS: {str(e)}",
                details={"error": str(e)}
            )
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make HTTP request to Stellar MLS API
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            data: Request body
            params: Query parameters
            
        Returns:
            Response data
            
        Raises:
            StellarMLSError: If request fails
        """
        token = await self._authenticate()
        url = f"{self.base_url}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                    params=params,
                    timeout=30.0,
                )
                
                if response.status_code >= 400:
                    error_detail = response.text
                    logger.error(f"Stellar MLS API error: {response.status_code} - {error_detail}")
                    
                    # Retry authentication if token expired
                    if response.status_code == 401:
                        self.auth_token = None
                        token = await self._authenticate()
                        headers["Authorization"] = f"Bearer {token}"
                        
                        # Retry request
                        response = await client.request(
                            method=method,
                            url=url,
                            headers=headers,
                            json=data,
                            params=params,
                            timeout=30.0,
                        )
                    
                    if response.status_code >= 400:
                        raise StellarMLSError(
                            message=f"MLS API error: {error_detail}",
                            status_code=response.status_code,
                            details={"response": error_detail}
                        )
                
                return response.json() if response.text else {}
                
        except httpx.RequestError as e:
            logger.exception(f"MLS request failed: {str(e)}")
            raise StellarMLSError(
                message=f"Failed to connect to MLS: {str(e)}",
                details={"error": str(e)}
            )
    
    async def search_properties(
        self,
        search_params: PropertySearchParams
    ) -> List[Dict[str, Any]]:
        """
        Search for properties in MLS
        
        Args:
            search_params: Search parameters
            
        Returns:
            List of matching properties
        """
        logger.info(f"Searching MLS properties with params: {search_params.model_dump()}")
        
        # Build query parameters
        params = {}
        
        if search_params.mls_number:
            params["mlsNumber"] = search_params.mls_number
        if search_params.address:
            params["address"] = search_params.address
        if search_params.city:
            params["city"] = search_params.city
        if search_params.state:
            params["state"] = search_params.state
        if search_params.zip_code:
            params["zipCode"] = search_params.zip_code
        if search_params.property_type:
            params["propertyType"] = search_params.property_type.value
        if search_params.status:
            params["status"] = search_params.status.value
        if search_params.min_price:
            params["minPrice"] = search_params.min_price
        if search_params.max_price:
            params["maxPrice"] = search_params.max_price
        if search_params.min_bedrooms:
            params["minBedrooms"] = search_params.min_bedrooms
        if search_params.max_bedrooms:
            params["maxBedrooms"] = search_params.max_bedrooms
        if search_params.min_bathrooms:
            params["minBathrooms"] = search_params.min_bathrooms
        if search_params.max_bathrooms:
            params["maxBathrooms"] = search_params.max_bathrooms
        if search_params.min_square_feet:
            params["minSquareFeet"] = search_params.min_square_feet
        if search_params.max_square_feet:
            params["maxSquareFeet"] = search_params.max_square_feet
        if search_params.has_pool is not None:
            params["hasPool"] = search_params.has_pool
        if search_params.has_garage is not None:
            params["hasGarage"] = search_params.has_garage
        if search_params.waterfront is not None:
            params["waterfront"] = search_params.waterfront
        
        params["limit"] = search_params.limit
        params["offset"] = search_params.offset
        
        result = await self._make_request("GET", "properties/search", params=params)
        return result.get("properties", []) if isinstance(result, dict) else []
    
    async def get_property(self, mls_number: str) -> Dict[str, Any]:
        """
        Get detailed property information by MLS number
        
        Args:
            mls_number: MLS listing number
            
        Returns:
            Property details
        """
        logger.info(f"Getting MLS property: {mls_number}")
        return await self._make_request("GET", f"properties/{mls_number}")
    
    async def get_property_photos(self, mls_number: str) -> List[str]:
        """
        Get property photos
        
        Args:
            mls_number: MLS listing number
            
        Returns:
            List of photo URLs
        """
        result = await self._make_request("GET", f"properties/{mls_number}/photos")
        return result.get("photos", []) if isinstance(result, dict) else []
    
    async def check_availability(self, mls_number: str) -> Dict[str, Any]:
        """
        Check if a property is still available
        
        Args:
            mls_number: MLS listing number
            
        Returns:
            Availability status
        """
        logger.info(f"Checking availability for MLS: {mls_number}")
        property_data = await self.get_property(mls_number)
        
        return {
            "mls_number": mls_number,
            "available": property_data.get("status") == "active",
            "status": property_data.get("status"),
            "price": property_data.get("price"),
            "address": property_data.get("address"),
        }

