"""DTO for charging period data transfer."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from .base_dto import BaseDTO
from .dto_protocol import ChargingPeriodDTOProtocol  # type: ignore # Used for type checking

@dataclass
class ChargingPeriodDTO(BaseDTO):  # type: ignore[type-arg] # Implements ChargingPeriodDTOProtocol
    """DTO representing a charging period that implements ChargingPeriodDTOProtocol.
    
    A charging period represents a continuous duration of charging or idle time
    with consistent pricing and state.
    """
    # Required fields from BaseDTO
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Required fields from ChargingPeriodDTOProtocol
    start_time: datetime = field(default_factory=datetime.now)  # When the period started
    end_time: Optional[datetime] = None  # When the period ended
    energy_kwh: float = 0.0  # Total energy delivered in kWh
    cost: float = 0.0  # Total cost for this period
    
    # Additional fields not in protocol
    state: str = ""  # Current state of the period (charging, idle, grace)
    grace_time_end: Optional[datetime] = None  # When grace period ends
    free_energy_wh: int = 0  # Free energy delivered in Wh
    max_allowance_wh: int = 0  # Maximum allowed free energy in Wh
