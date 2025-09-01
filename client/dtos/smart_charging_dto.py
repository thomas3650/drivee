"""SmartCharging DTO."""
from typing import Dict, List, Optional
from datetime import datetime, time
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

    @property
    def is_scheduled(self) -> bool:
        """Check if charging is scheduled."""
        return self.enabled and self.mode == "schedule"

    @property
    def is_solar_charging(self) -> bool:
        """Check if solar charging is enabled."""
        return self.enabled and self.use_solar

    def _parse_time(self, time_str: str) -> time:
        """Parse time string to time object."""
        try:
            return datetime.strptime(time_str, "%H:%M:%S").time()
        except ValueError as e:
            raise ValueError(f"Invalid time format. Use HH:MM:SS: {e}")

    @field_validator('start_time', 'end_time')
    @classmethod
    def validate_time_format(cls, v: str) -> str:
        """Validate time strings are in correct format."""
        try:
            datetime.strptime(v, "%H:%M:%S")
            return v
        except ValueError:
            raise ValueError("Time must be in HH:MM:SS format")
