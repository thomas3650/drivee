"""DTOs for scheduling intervals data transfer."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .base_dto import BaseDTO

@dataclass
class SchedulingIntervalDTO(BaseDTO):
    """DTO representing a scheduling interval for charging."""
    # Required fields from BaseDTO
    id: str
    
    # Scheduling fields
    start_time: str = ""  # Format: "HH:mm"
    end_time: str = ""  # Format: "HH:mm"
    active: bool = True
    days: Optional[list[str]] = None  # Days of week this interval is active
