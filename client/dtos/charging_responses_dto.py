"""DTOs for charging operation responses."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from .base_dto import BaseDTO
from .charging_session_dto import ChargingSessionDTO

@dataclass
class StartChargingResponseDTO(BaseDTO):  # type: ignore[type-arg]
    """DTO for start charging request response.
    
    Contains the charging session that was started.
    """
    # Required fields from BaseDTO
    id: str
    
    # Optional fields
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    session: Optional[ChargingSessionDTO] = None

@dataclass
class EndChargingResponseDTO(BaseDTO):  # type: ignore[type-arg]
    """DTO for end charging request response.
    
    Contains the charging session that was ended.
    """
    # Required fields from BaseDTO
    id: str
    
    # Optional fields
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    session: Optional[ChargingSessionDTO] = None
