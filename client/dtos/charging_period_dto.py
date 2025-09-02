"""DTO for charging period data transfer."""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import Field

from .base_dto import BaseDTO
from ..models.types import PeriodStateType

class ChargingPeriodDTO(BaseDTO):
    """DTO representing a charging period.
    
    A charging period represents a continuous duration of charging or idle time
    with consistent pricing and state.
    """
    started_at: datetime = Field(description="When the period started")
    stopped_at: Optional[datetime] = Field(
        default=None,
        description="When the period ended"
    )
    state: PeriodStateType = Field(description="Current state of the period")
    duration_in_seconds: int = Field(
        ge=0,
        description="Duration of the period in seconds"
    )
    amount: Decimal = Field(
        ge=0,
        description="Amount charged for this period"
    )
    grace_time_end: Optional[datetime] = Field(
        default=None,
        description="When grace period ends"
    )
    free_energy_wh: int = Field(
        ge=0,
        description="Free energy delivered in Wh"
    )
    max_allowance_wh: int = Field(
        ge=0,
        description="Maximum allowed free energy in Wh"
    )
