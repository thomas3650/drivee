"""Models for charging history."""
from typing import List
from pydantic import Field

from .base_dto import DTOBase
from .charging_session_dto import ChargingSession

class ChargingHistoryEntry(DTOBase):
    """Model for a charging history entry."""
    session: ChargingSession
    note: str
    type: str
    address: str

    @property
    def id(self) -> str:
        """Get the session ID."""
        return self.session.id

class ChargingHistory(DTOBase):
    """Model for charging history data."""
    sessions: List[ChargingHistoryEntry] = Field(alias='session_history')
