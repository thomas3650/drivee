"""DTO for charging schedule intervals data transfer."""
from typing import Optional
from pydantic import Field

from .base_dto import BaseDTO

class SchedulingIntervalsDTO(BaseDTO):
    """DTO representing charging schedule configuration.
    
    This DTO handles both off-peak and solar charging schedules.
    It represents pure schedule data without business logic.
    """
    
    # Off-peak charging schedule
    off_peak_is_set: bool = Field(
        alias='off_peak_is_set',
        default=False,
        description="Whether off-peak charging is configured"
    )
    off_peak_start_time: str = Field(
        alias='off_peak_start_time',
        default="23:00",
        description="Start time for off-peak charging (HH:MM)"
    )
    off_peak_end_time: str = Field(
        alias='off_peak_end_time',
        default="06:00",
        description="End time for off-peak charging (HH:MM)"
    )
    
    # Solar charging schedule
    solar_is_set: bool = Field(
        alias='solar_is_set',
        default=False,
        description="Whether solar charging is configured"
    )
    solar_start_time: Optional[str] = Field(
        alias='solar_start_time',
        default=None,
        description="Start time for solar charging (HH:MM)"
    )
    solar_end_time: Optional[str] = Field(
        alias='solar_end_time',
        default=None,
        description="End time for solar charging (HH:MM)"
    )
    solar_max_power: Optional[float] = Field(
        alias='solar_max_power',
        default=None,
        description="Maximum power for solar charging in kW"
    )
