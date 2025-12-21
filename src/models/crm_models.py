"""
Pydantic models for CRM (BoldTrail) data
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ContactType(str, Enum):
    """Contact types in CRM"""
    BUYER = "buyer"
    SELLER = "seller"
    BOTH = "both"
    AGENT = "agent"
    OTHER = "other"


class LeadStatus(str, Enum):
    """Lead status in CRM"""
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    UNQUALIFIED = "unqualified"
    APPOINTMENT_SET = "appointment_set"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"


class Contact(BaseModel):
    """CRM Contact model"""
    id: Optional[str] = None
    first_name: str
    last_name: str
    phone: str
    email: Optional[EmailStr] = None
    contact_type: ContactType = ContactType.OTHER
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    source: Optional[str] = "voice_agent"
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    custom_fields: Dict[str, Any] = Field(default_factory=dict)


class BuyerLead(BaseModel):
    """Buyer lead model"""
    contact: Contact
    property_type: Optional[str] = None
    location_preference: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[float] = None
    square_feet_min: Optional[int] = None
    square_feet_max: Optional[int] = None
    timeframe: Optional[str] = None
    pre_approved: Optional[bool] = False
    lender_name: Optional[str] = None
    must_haves: List[str] = Field(default_factory=list)
    nice_to_haves: List[str] = Field(default_factory=list)
    special_requirements: Optional[str] = None  # Golf cart garage, water view, etc.
    buyer_experience: Optional[str] = None  # "first-time", "experienced", or "not-specified"
    payment_method: Optional[str] = None  # "cash", "financing", or "not-sure"
    status: LeadStatus = LeadStatus.NEW
    assigned_agent_id: Optional[str] = None


class SellerLead(BaseModel):
    """Seller lead model"""
    contact: Contact
    property_address: str
    city: str
    state: str
    zip_code: str
    property_type: Optional[str] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[float] = None
    square_feet: Optional[int] = None
    lot_size: Optional[str] = None
    year_built: Optional[int] = None
    condition: Optional[str] = None  # Note: Also aliased as property_condition in requests
    reason_for_selling: Optional[str] = None
    timeframe: Optional[str] = None
    estimated_value: Optional[float] = None
    mortgage_balance: Optional[float] = None
    improvements: Optional[str] = None
    previously_listed: Optional[bool] = None  # Has the property been listed before?
    currently_occupied: Optional[bool] = None  # Are they currently living there?
    status: LeadStatus = LeadStatus.NEW
    assigned_agent_id: Optional[str] = None


class Agent(BaseModel):
    """Real estate agent model"""
    id: str
    first_name: str
    last_name: str
    phone: str
    email: EmailStr
    license_number: Optional[str] = None
    specialties: List[str] = Field(default_factory=list)
    service_areas: List[str] = Field(default_factory=list)
    languages: List[str] = Field(default=["English"])
    available: bool = True
    photo_url: Optional[str] = None
    bio: Optional[str] = None
    years_experience: Optional[int] = None
    properties_sold: Optional[int] = None
    rating: Optional[float] = None
    
    @property
    def full_name(self) -> str:
        """Get agent's full name"""
        return f"{self.first_name} {self.last_name}"


class Appointment(BaseModel):
    """Appointment model"""
    id: Optional[str] = None
    contact_id: str
    agent_id: str
    appointment_type: str  # showing, consultation, listing_appointment, etc.
    date: datetime
    duration_minutes: int = 60
    location: Optional[str] = None
    property_address: Optional[str] = None
    mls_number: Optional[str] = None
    status: str = "scheduled"  # scheduled, confirmed, completed, cancelled, no_show
    notes: Optional[str] = None
    reminder_sent: bool = False
    created_at: Optional[datetime] = None

