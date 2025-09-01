"""EVSE (Electric Vehicle Supply Equipment) DTO model."""
from typing import List, Optional
from pydantic import Field

from .base_dto import DTOBase
from .connector_dto import Connector
from .charging_session_dto import ChargingSession

class EVSE(DTOBase):
    """Model for Electric Vehicle Supply Equipment."""
    id: str
    status: str
    max_power: float = Field(alias='maxPower')
    current_type: str
    connectors: List[Connector]
    session: Optional[ChargingSession] = None
