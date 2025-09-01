"""SchedulingIntervals DTO model."""
from typing import Optional
from pydantic import Field

from .base_dto import DTOBase

class SchedulingIntervals(DTOBase):
    """Model for charge point scheduling intervals."""
    off_peak_is_set: bool = Field(alias='off_peak_is_set', default=False)
    solar_is_set: bool = Field(alias='solar_is_set', default=False)
    off_peak_start_time: str = Field(alias='off_peak_start_time', default="23:00")
    off_peak_end_time: str = Field(alias='off_peak_end_time', default="06:00")
    solar_start_time: Optional[str] = Field(alias='solar_start_time', default=None)
    solar_end_time: Optional[str] = Field(alias='solar_end_time', default=None)
    solar_max_power: Optional[float] = Field(alias='solar_max_power', default=None)
