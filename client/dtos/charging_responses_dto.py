"""Response models for charging operations."""
from .base_dto import DTOBase
from .charging_session_dto import ChargingSession

class StartChargingResponse(DTOBase):
    """Response model for start charging request."""
    session: ChargingSession

class EndChargingResponse(DTOBase):
    """Response model for end charging request."""
    session: ChargingSession
