"""DTO for charging connector data transfer."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from .base_dto import BaseDTO
from .dto_protocol import ConnectorDTOProtocol  # type: ignore # Used for type checking

@dataclass
class ConnectorDTO(BaseDTO):  # type: ignore[type-arg] # Implements ConnectorDTOProtocol
    """DTO representing a charging connector that implements ConnectorDTOProtocol.
    
    A connector is a physical plug or socket that connects to a vehicle.
    This DTO represents the pure data structure without any business logic.
    """
    # Required fields from BaseDTO
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Required fields from ConnectorDTOProtocol
    type: str = ""  # Connector type (e.g., 'Type2', 'CCS')
    status: str = ""  # Current operational status
    max_power: float = 0.0  # Maximum power output in kW
    
    # Additional fields
    format: str = ""  # Physical format (e.g., 'cable', 'socket')
    max_current: float = 0.0  # Maximum current in amperes
    icon: Optional[str] = None  # Icon identifier for UI
    tariff_id: Optional[str] = None  # Associated tariff ID
    last_status_update: Optional[datetime] = None  # Last status update timestamp
