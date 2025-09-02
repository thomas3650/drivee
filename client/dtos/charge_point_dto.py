"""DTOs for charge point data transfer."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from .base_dto import BaseDTO
from .dto_protocol import ChargePointDTOProtocol  # type: ignore # Used for type checking
from .evse_dto import EVSEDTO

@dataclass
class LocationDTO(BaseDTO):
    """DTO representing location information for a charge point."""
    id: str  # Required from BaseDTO
    latitude: Optional[float] = None
    longitude: Optional[float] = None

@dataclass
class ChargePointDTO(BaseDTO):  # type: ignore[type-arg] # Implements ChargePointDTOProtocol
    """DTO representing a charge point in the system that implements ChargePointDTOProtocol."""
    # Required fields from BaseDTO
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Required fields from ChargePointDTOProtocol
    name: str = ""
    location_id: str = ""
    last_updated: datetime = field(default_factory=datetime.now)
    status: str = ""
    photo: Optional[str] = None
    plug_and_charge: bool = False
    smart_charging_enabled: bool = False
    allowed_min_current_a: int = 0
    allowed_max_current_a: int = 0
    allowed_max_power_kw: str = "0"
    max_current_a: int = 0
    is_rebooting: bool = False
    evses: List[EVSEDTO] = field(default_factory=lambda: list())
    
    # Additional fields not in protocol
    postcode: Optional[str] = None
    allowed_solar_min_power_kw: Optional[float] = None
    location: Optional[LocationDTO] = None
