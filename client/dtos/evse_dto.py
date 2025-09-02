"""DTO for EVSE (Electric Vehicle Supply Equipment) data transfer."""
from __future__ import annotations

from typing import List, Optional
from pydantic import Field

from .base_dto import BaseDTO
from .connector_dto import ConnectorDTO
from .charging_session_dto import ChargingSessionDTO

class EVSEDTO(BaseDTO):
    """DTO representing an EVSE in the system.
    
    An EVSE is a physical charging station unit that may have multiple connectors.
    This DTO represents the pure data structure without any business logic.
    """
    
    # Core identifiers
    id: str = Field(description="Unique identifier for the EVSE")
    identifier: str = Field(description="External/visible identifier")
    
    # Status and capabilities
    status: str = Field(description="Current operational status")
    max_power: int = Field(
        alias='maxPower',
        description="Maximum power output in watts"
    )
    current_type: str = Field(
        alias='currentType',
        description="Type of current (AC/DC)"
    )
    
    # Associated equipment and sessions
    connectors: List[ConnectorDTO] = Field(
        description="List of connectors on this EVSE"
    )
    session: Optional[ChargingSessionDTO] = Field(
        None,
        description="Current charging session, if any"
    )
