"""DTOs for charge point data transfer."""
from __future__ import annotations
"""DTOs for charge point data transfer."""

from datetime import datetime
from typing import  Optional

from pydantic import Field, ConfigDict

from .base_dto import BaseDTO
from .evse_dto import EVSEDTO
from .scheduling_intervals_dto import SchedulingIntervalsDTO

class LocationDTO(BaseDTO):
    """DTO representing location information for a charge point."""
    latitude: Optional[float] = Field(None, description="Latitude coordinate")
    longitude: Optional[float] = Field(None, description="Longitude coordinate")

class ChargePointDTO(BaseDTO):
    """DTO representing a charge point in the system."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True, arbitrary_types_allowed=True)
    id: str = Field(description="Unique identifier for the charge point")
    name: str = Field(description="Display name of the charge point")
    location: LocationDTO = Field(description="Geographic location information")
    location_id: Optional[str] = Field(None, description="ID of the location where installed")
    postcode: Optional[str] = Field(None, description="Postal code of the location")
    photo: Optional[str] = Field(None, description="URL to charge point photo")
    last_updated: datetime = Field(description="Timestamp of last status update")
    
    # Charging capabilities
    plug_and_charge: bool = Field(False, description="Whether plug & charge is supported")
    smart_charging_enabled: bool = Field(False, description="Whether smart charging is enabled")
    allowed_min_current_a: int = Field(description="Minimum allowed current in amperes")
    allowed_max_current_a: int = Field(description="Maximum allowed current in amperes")
    allowed_solar_min_power_kw: Optional[float] = Field(None, description="Minimum solar power in kW")
    allowed_max_power_kw: str = Field(description="Maximum allowed power in kW")
    max_current_a: int = Field(description="Maximum current in amperes")
    
    # Operational status
    status: str = Field(description="Current operational status")
    is_rebooting: bool = Field(False, description="Whether charge point is rebooting")
    
    # Associated equipment and scheduling
    scheduling_intervals: Optional[SchedulingIntervalsDTO] = Field(
        default=None,
        description="Charging schedule intervals"
    )
    evses: Optional[EVSEDTO] = Field(
        default=None,
        description="List of EVSEs at this charge point"
    )
