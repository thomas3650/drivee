"""DTOs for charging history data transfer."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from .base_dto import BaseDTO
from .charging_session_dto import ChargingSessionDTO

@dataclass
class ChargingHistoryEntryDTO(BaseDTO):  # type: ignore[type-arg]
    """DTO representing a single charging history entry.
    
    This DTO contains the details of a single charging session with its
    associated metadata like notes and location.
    """
    # Required fields from BaseDTO
    id: str
    
    # Optional fields from BaseDTO
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Entry fields
    session: Optional[ChargingSessionDTO] = None  # The charging session details
    note: str = ""  # User or system note about the session
    type: str = ""  # Type of charging session
    address: str = ""  # Location address where charging occurred

    def __post_init__(self) -> None:
        """Set the ID after initialization if not provided."""
        if self.session and not self.id:
            self.id = self.session.id

@dataclass
class ChargingHistoryDTO(BaseDTO):  # type: ignore[type-arg]
    """DTO representing a collection of charging history entries.
    
    This DTO contains a list of charging sessions with their associated
    metadata, sorted by date.
    """
    # Required fields from BaseDTO
    id: str
    
    # Optional fields from BaseDTO
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Collection fields
    sessions: List[ChargingHistoryEntryDTO] = field(default_factory=lambda: list())
