"""
Pydantic models for Vapi.ai integration
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any, List
from enum import Enum


class MessageType(str, Enum):
    """Vapi message types"""
    TRANSCRIPT = "transcript"
    FUNCTION_CALL = "function-call"
    HANG = "hang"
    SPEECH_UPDATE = "speech-update"
    STATUS_UPDATE = "status-update"


class VapiMessage(BaseModel):
    """Vapi message model"""
    type: str
    role: Optional[str] = None
    content: Optional[str] = None
    timestamp: Optional[str] = None


class VapiToolCall(BaseModel):
    """Vapi tool/function call model"""
    id: str
    type: str = "function"
    function: Dict[str, Any]


class VapiRequest(BaseModel):
    """Standard Vapi function request"""
    message: VapiMessage
    call: Optional[Dict[str, Any]] = None
    tool_call_id: Optional[str] = None
    function_name: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict)


class VapiResponse(BaseModel):
    """Standard Vapi function response"""
    result: Optional[str] = None
    results: Optional[List[Dict[str, Any]]] = None
    success: bool = True
    message: Optional[str] = None
    error: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Operation completed successfully",
                "data": {}
            }
        }


class VapiWebhookEvent(BaseModel):
    """Vapi webhook event model"""
    type: str
    call: Optional[Dict[str, Any]] = None
    message: Optional[VapiMessage] = None
    timestamp: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


# Function-specific request models

class CheckPropertyRequest(BaseModel):
    """Request model for check_property function - handles Vapi's empty strings"""
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = "FL"
    zip_code: Optional[str] = None
    mls_number: Optional[str] = None
    agent_name: Optional[str] = None  # Search listings by listing agent (use roster name from get_agent_info)
    property_type: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[float] = None
    
    # Convert empty strings to None for numeric fields (Pydantic v2 syntax)
    @field_validator('min_price', 'max_price', 'bedrooms', 'bathrooms', mode='before')
    @classmethod
    def empty_str_to_none(cls, v):
        """Convert empty strings and whitespace to None before type validation"""
        if v is None:
            return None
        if isinstance(v, str):
            v = v.strip()
            if v == "":
                return None
        return v
    
    # Strip whitespace from string fields and convert empty strings to None
    @field_validator('address', 'city', 'state', 'zip_code', 'mls_number', 'agent_name', 'property_type', mode='before')
    @classmethod
    def strip_strings(cls, v):
        """Strip whitespace and convert empty strings to None"""
        if isinstance(v, str):
            v = v.strip()
            if v == "":
                return None
        return v


class GetAgentInfoRequest(BaseModel):
    """Request model for get_agent_info function"""
    agent_name: Optional[str] = None
    agent_id: Optional[str] = None
    specialty: Optional[str] = None
    city: Optional[str] = None


class RouteToAgentRequest(BaseModel):
    """Request model for route_to_agent function"""
    lead_id: str
    agent_id: Optional[str] = None
    agent_name: str
    agent_phone: str
    caller_name: str
    caller_phone: str
    reason: Optional[str] = None


class CreateBuyerLeadRequest(BaseModel):
    """Request model for create_buyer_lead function - handles Vapi's empty strings"""
    first_name: str
    last_name: str
    phone: str
    email: Optional[str] = None
    property_type: Optional[str] = None
    location_preference: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[float] = None
    timeframe: Optional[str] = None
    pre_approved: Optional[bool] = None
    special_requirements: Optional[str] = None  # Golf cart garage, water view, etc.
    buyer_experience: Optional[str] = None  # "first-time", "experienced", or "not-specified"
    payment_method: Optional[str] = None  # "cash", "financing", or "not-sure"
    notes: Optional[str] = None
    
    # Convert empty strings to None for numeric fields
    @field_validator('min_price', 'max_price', 'bedrooms', 'bathrooms', mode='before')
    @classmethod
    def empty_str_to_none(cls, v):
        """Convert empty strings and whitespace to None before type validation"""
        if v is None:
            return None
        if isinstance(v, str):
            v = v.strip()
            if v == "":
                return None
        return v
    
    # Convert empty strings to None for boolean fields
    @field_validator('pre_approved', mode='before')
    @classmethod
    def empty_str_to_none_bool(cls, v):
        """Convert empty strings and whitespace to None before boolean validation"""
        if v is None:
            return None
        if isinstance(v, str):
            v = v.strip()
            if v == "":
                return None
            # Try to convert string booleans to actual booleans
            if v.lower() in ('true', 'yes', '1'):
                return True
            if v.lower() in ('false', 'no', '0'):
                return False
        return v
    
    # Strip whitespace from string fields
    @field_validator('email', 'property_type', 'location_preference', 'timeframe', 'special_requirements', 'buyer_experience', 'payment_method', 'notes', mode='before')
    @classmethod
    def strip_strings(cls, v):
        """Strip whitespace and convert empty strings to None"""
        if isinstance(v, str):
            v = v.strip()
            if v == "":
                return None
        return v


class CreateSellerLeadRequest(BaseModel):
    """Request model for create_seller_lead function - handles Vapi's empty strings"""
    first_name: str
    last_name: Optional[str] = None
    phone: str
    email: Optional[str] = None
    property_address: str
    city: str
    state: str = "FL"
    zip_code: Optional[str] = None
    property_type: Optional[str] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[float] = None
    square_feet: Optional[int] = None
    year_built: Optional[int] = None
    reason_for_selling: Optional[str] = None
    timeframe: Optional[str] = None
    estimated_value: Optional[float] = None
    property_condition: Optional[str] = None  # excellent, good, fair, needs-work
    previously_listed: Optional[bool] = None  # Has it been listed before?
    currently_occupied: Optional[bool] = None  # Are they living in the property?
    notes: Optional[str] = None
    
    # Convert empty strings to None for numeric fields
    @field_validator('bedrooms', 'bathrooms', 'square_feet', 'year_built', 'estimated_value', mode='before')
    @classmethod
    def empty_str_to_none(cls, v):
        """Convert empty strings and whitespace to None before type validation"""
        if v is None:
            return None
        if isinstance(v, str):
            v = v.strip()
            if v == "":
                return None
        return v
    
    # Convert empty strings to None for boolean fields
    @field_validator('previously_listed', 'currently_occupied', mode='before')
    @classmethod
    def empty_str_to_none_bool(cls, v):
        """Convert empty strings and whitespace to None before boolean validation"""
        if v is None:
            return None
        if isinstance(v, str):
            v = v.strip()
            if v == "":
                return None
            # Try to convert string booleans to actual booleans
            if v.lower() in ('true', 'yes', '1'):
                return True
            if v.lower() in ('false', 'no', '0'):
                return False
        return v
    
    # Strip whitespace from string fields
    @field_validator('email', 'property_type', 'reason_for_selling', 'timeframe', 'property_condition', 'notes', mode='before')
    @classmethod
    def strip_strings(cls, v):
        """Strip whitespace and convert empty strings to None"""
        if isinstance(v, str):
            v = v.strip()
            if v == "":
                return None
        return v


class SendNotificationRequest(BaseModel):
    """Request model for send_notification function"""
    recipient_phone: str
    message: str
    notification_type: str = "sms"  # sms, email, both
    recipient_email: Optional[str] = None

