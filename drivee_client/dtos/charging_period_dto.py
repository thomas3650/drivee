"""DTO for charging period data transfer."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from .base_dto import BaseDTO
from pydantic import Field

class ChargingPeriodDTO(BaseDTO):
    started_at: datetime = Field(..., alias="startedAt")
    stopped_at: Optional[datetime] = Field(..., alias="stoppedAt")
    amount: float = Field(..., alias="amount")
    state: str = Field(..., alias="state")
    duration_in_seconds: int = Field(..., alias="durationInSeconds")

