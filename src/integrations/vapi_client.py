"""
Vapi.ai API client for managing assistants and phone calls
"""

import httpx
from typing import Dict, Any, Optional, List
from src.config.settings import settings
from src.utils.logger import get_logger
from src.utils.errors import VapiError

logger = get_logger(__name__)


class VapiClient:
    """Client for Vapi.ai API"""
    
    def __init__(self):
        self.api_key = settings.VAPI_API_KEY
        self.base_url = settings.VAPI_API_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make HTTP request to Vapi API
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint
            data: Request body data
            params: URL query parameters
            
        Returns:
            Response data
            
        Raises:
            VapiError: If request fails
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
                    logger.error(f"Vapi API error: {response.status_code} - {error_detail}")
                    raise VapiError(
                        message=f"Vapi API error: {error_detail}",
                        status_code=response.status_code,
                        details={"response": error_detail}
                    )
                
                return response.json() if response.text else {}
                
        except httpx.RequestError as e:
            logger.exception(f"Vapi request failed: {str(e)}")
            raise VapiError(
                message=f"Failed to connect to Vapi API: {str(e)}",
                details={"error": str(e)}
            )
    
    async def create_assistant(self, assistant_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new Vapi assistant
        
        Args:
            assistant_config: Assistant configuration
            
        Returns:
            Created assistant data
        """
        logger.info(f"Creating Vapi assistant: {assistant_config.get('name')}")
        return await self._make_request("POST", "assistant", data=assistant_config)
    
    async def get_assistant(self, assistant_id: str) -> Dict[str, Any]:
        """
        Get assistant by ID
        
        Args:
            assistant_id: Assistant ID
            
        Returns:
            Assistant data
        """
        return await self._make_request("GET", f"assistant/{assistant_id}")
    
    async def update_assistant(
        self,
        assistant_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update an existing assistant
        
        Args:
            assistant_id: Assistant ID
            updates: Fields to update
            
        Returns:
            Updated assistant data
        """
        logger.info(f"Updating Vapi assistant: {assistant_id}")
        return await self._make_request("PATCH", f"assistant/{assistant_id}", data=updates)
    
    async def delete_assistant(self, assistant_id: str) -> Dict[str, Any]:
        """
        Delete an assistant
        
        Args:
            assistant_id: Assistant ID
            
        Returns:
            Deletion confirmation
        """
        logger.info(f"Deleting Vapi assistant: {assistant_id}")
        return await self._make_request("DELETE", f"assistant/{assistant_id}")
    
    async def list_assistants(self) -> List[Dict[str, Any]]:
        """
        List all assistants
        
        Returns:
            List of assistants
        """
        result = await self._make_request("GET", "assistant")
        return result if isinstance(result, list) else []
    
    async def create_phone_call(self, call_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Initiate an outbound phone call
        
        Args:
            call_config: Call configuration including phone number and assistant
            
        Returns:
            Call data
        """
        logger.info(f"Creating phone call to: {call_config.get('customer', {}).get('number')}")
        return await self._make_request("POST", "call/phone", data=call_config)
    
    async def get_call(self, call_id: str) -> Dict[str, Any]:
        """
        Get call details by ID
        
        Args:
            call_id: Call ID
            
        Returns:
            Call data
        """
        return await self._make_request("GET", f"call/{call_id}")
    
    async def end_call(self, call_id: str) -> Dict[str, Any]:
        """
        End an active call
        
        Args:
            call_id: Call ID
            
        Returns:
            Call end confirmation
        """
        logger.info(f"Ending call: {call_id}")
        return await self._make_request("DELETE", f"call/{call_id}")

