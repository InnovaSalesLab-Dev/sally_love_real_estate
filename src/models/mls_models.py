"""
Pydantic models for MLS (Stellar MLS) data
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class PropertyStatus(str, Enum):
    """Property listing status"""
    ACTIVE = "active"
    PENDING = "pending"
    SOLD = "sold"
    EXPIRED = "expired"
    WITHDRAWN = "withdrawn"
    COMING_SOON = "coming_soon"


class PropertyType(str, Enum):
    """Property types"""
    SINGLE_FAMILY = "single_family"
    CONDO = "condo"
    TOWNHOUSE = "townhouse"
    MULTI_FAMILY = "multi_family"
    LAND = "land"
    COMMERCIAL = "commercial"
    MOBILE_HOME = "mobile_home"
    FARM_RANCH = "farm_ranch"


class PropertySearchParams(BaseModel):
    """Parameters for searching properties in MLS"""
    mls_number: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = "FL"
    zip_code: Optional[str] = None
    property_type: Optional[PropertyType] = None
    status: Optional[PropertyStatus] = PropertyStatus.ACTIVE
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    min_bedrooms: Optional[int] = None
    max_bedrooms: Optional[int] = None
    min_bathrooms: Optional[float] = None
    max_bathrooms: Optional[float] = None
    min_square_feet: Optional[int] = None
    max_square_feet: Optional[int] = None
    min_lot_size: Optional[float] = None
    max_lot_size: Optional[float] = None
    min_year_built: Optional[int] = None
    max_year_built: Optional[int] = None
    has_pool: Optional[bool] = None
    has_garage: Optional[bool] = None
    waterfront: Optional[bool] = None
    limit: int = Field(default=10, le=100)
    offset: int = Field(default=0, ge=0)


class Property(BaseModel):
    """Property listing model"""
    mls_number: str
    address: str
    city: str
    state: str
    zip_code: str
    property_type: PropertyType
    status: PropertyStatus
    price: float
    bedrooms: int
    bathrooms: float
    square_feet: Optional[int] = None
    lot_size: Optional[float] = None
    year_built: Optional[int] = None
    description: Optional[str] = None
    listing_agent_id: Optional[str] = None
    listing_agent_name: Optional[str] = None
    listing_agent_phone: Optional[str] = None
    list_date: Optional[datetime] = None
    days_on_market: Optional[int] = None
    
    @property
    def full_address(self) -> str:
        """Get full formatted address"""
        return f"{self.address}, {self.city}, {self.state} {self.zip_code}"


class PropertyDetails(Property):
    """Detailed property information"""
    photos: List[str] = Field(default_factory=list)
    virtual_tour_url: Optional[str] = None
    features: List[str] = Field(default_factory=list)
    amenities: List[str] = Field(default_factory=list)
    appliances: List[str] = Field(default_factory=list)
    flooring: List[str] = Field(default_factory=list)
    heating_cooling: Optional[str] = None
    parking: Optional[str] = None
    garage_spaces: Optional[int] = None
    pool: Optional[bool] = False
    waterfront: Optional[bool] = False
    view: Optional[str] = None
    hoa_fee: Optional[float] = None
    tax_amount: Optional[float] = None
    tax_year: Optional[int] = None
    zoning: Optional[str] = None
    subdivision: Optional[str] = None
    school_district: Optional[str] = None
    elementary_school: Optional[str] = None
    middle_school: Optional[str] = None
    high_school: Optional[str] = None
    showing_instructions: Optional[str] = None
    additional_details: Dict[str, Any] = Field(default_factory=dict)

