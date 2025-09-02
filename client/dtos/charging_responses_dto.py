"""DTOs for charging operation responses."""
from pydantic import Field

from .base_dto import BaseDTO
from .charging_session_dto import ChargingSessionDTO

class StartChargingResponseDTO(BaseDTO):
    """DTO for start charging request response.
    
    Contains the charging session that was started.
    """
    session: ChargingSessionDTO = Field(description="The started charging session")

class EndChargingResponseDTO(BaseDTO):
    """DTO for end charging request response.
    
    Contains the charging session that was ended.
    """
    session: ChargingSessionDTO = Field(description="The ended charging session")
