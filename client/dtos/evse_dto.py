"""DTO for EVSE (Electric Vehicle Supply Equipment) data transfer."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from .base_dto import BaseDTO
from .connector_dto import ConnectorDTO
from .dto_protocol import EVSEDTOProtocol  # type: ignore # Used for type checking

@dataclass
class EVSEDTO(BaseDTO):  # type: ignore[type-arg] # Implements EVSEDTOProtocol
    """DTO representing an EVSE that implements EVSEDTOProtocol.
    
    An EVSE is a physical charging station unit that may have multiple connectors.
    This DTO represents the pure data structure without any business logic.
    """
    # Required fields from BaseDTO
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Required fields from EVSEDTOProtocol
    status: str = ""
    connectors: List[ConnectorDTO] = field(default_factory=lambda: list())
    
    # Additional fields
    identifier: str = ""
    max_power: int = 0
    current_type: str = "AC"
