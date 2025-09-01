"""SmartCharging DTO."""
from typing import Dict, List, Optional
from datetime import datetime
from pydantic import Field, field_validator

from .base_dto import DTOBase

class SmartCharging(DTOBase):
    """Model for smart charging settings."""
    enabled: bool
    mode: str
    target_charge: Dict[str, str]
    use_solar: bool
    use_all_generated_solar: Optional[bool] = None
    max_current_from_grid_a: Optional[int] = Field(None, gt=0)
    solar_stable_time_sec: Optional[int] = Field(None, ge=0)
    dynamic_rates_integration_id: Optional[int] = None
    start_time: str
    end_time: str
    weekdays: Optional[List[str]] = None

    @field_validator('start_time', 'end_time')
    @classmethod
    def validate_time_format(cls, v: str) -> str:
        """Validate time strings are in correct format."""
        try:
            datetime.strptime(v, "%H:%M:%S")
            return v
        except ValueError:
            raise ValueError("Time must be in HH:MM:SS format")
