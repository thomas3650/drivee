"""DTOs for charging history data transfer."""
from __future__ import annotations

from typing import List, Optional

from pydantic import Field

from .base_dto import BaseDTO
from .charging_session_dto import ChargingSessionDTO

class ChargingHistoryEntryDTO(BaseDTO):
    session: Optional[ChargingSessionDTO] = Field(default=None, alias="session")
    note: str = Field(..., alias="note")
    type: str = Field(..., alias="type")
    address: str = Field(..., alias="address")

class ChargingHistoryDTO(BaseDTO):
    session_history: List[ChargingHistoryEntryDTO] = Field(default_factory=lambda: list(), alias="session_history")
