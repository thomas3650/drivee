"""ChargingPeriod DTO."""
from datetime import datetime
from decimal import Decimal
from typing import Optional

from .base_dto import DTOBase

class ChargingPeriod(DTOBase):
    """Model for a charging period."""
    started_at: datetime
    stopped_at: Optional[datetime] = None
    state: str
    duration_in_seconds: int
    amount: Decimal
    grace_time_end: Optional[datetime] = None
    free_energy_wh: int
    max_allowance_wh: int
