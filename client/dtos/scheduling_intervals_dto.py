"""SchedulingIntervals DTO model."""
from pydantic import Field

from .base_dto import DTOBase

class SchedulingIntervals(DTOBase):
    """Model for charge point scheduling intervals."""
    off_peak_is_set: bool = Field(alias='offPeakIsSet', default=False)
