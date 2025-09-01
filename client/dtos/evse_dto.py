"""EVSE (Electric Vehicle Supply Equipment) DTO model."""
from typing import List, Optional
from pydantic import Field

from .base_dto import DTOBase
from .connector_dto import Connector
from .charging_session_dto import ChargingSession

class EVSE(DTOBase):
    """Model for Electric Vehicle Supply Equipment."""
    id: str
    identifier: str
    status: str
    max_power: int = Field(alias='maxPower')  # Power in watts
    current_type: str = Field(alias='currentType')
    connectors: List[Connector]
    session: Optional[ChargingSession] = None
