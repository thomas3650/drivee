"""DTOs for charging history data transfer."""
from typing import List, Any
from pydantic import Field

from .base_dto import BaseDTO
from .charging_session_dto import ChargingSessionDTO

class ChargingHistoryEntryDTO(BaseDTO):
    """DTO representing a single charging history entry.
    
    This DTO contains the details of a single charging session with its
    associated metadata like notes and location.
    """
    session: ChargingSessionDTO = Field(description="The charging session details")
    note: str = Field(description="User or system note about the session")
    type: str = Field(description="Type of charging session")
    address: str = Field(description="Location address where charging occurred")

    id: str = Field(
        description="The session ID",
        default=""
    )

    def model_post_init(self, __context: Any) -> None:
        """Set the ID after initialization."""
        super().model_post_init(__context)
        self.id = self.session.id

class ChargingHistoryDTO(BaseDTO):
    """DTO representing a collection of charging history entries.
    
    This DTO contains a list of charging sessions with their associated
    metadata, sorted by date.
    """
    sessions: List[ChargingHistoryEntryDTO] = Field(
        alias='session_history',
        description="List of charging history entries"
    )
