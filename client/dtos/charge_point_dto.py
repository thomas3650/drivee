"""ChargePoint DTO model."""
from typing import Any, Union, List, Dict
from pydantic import Field, field_validator

from .base_dto import DTOBase
from .scheduling_intervals_dto import SchedulingIntervals
from .evse_dto import EVSE

class ChargePoint(DTOBase):
    """Model for a charge point."""
    name: str
    status: str
    allowed_max_power_kw: float = Field(alias='allowedMaxPowerKw')
    scheduling_intervals: SchedulingIntervals = Field(default_factory=SchedulingIntervals)
    evse: EVSE = Field(alias='evses')

    @field_validator('evse', mode='before')
    @classmethod
    def extract_first_evse(cls, v: Union[List[Dict[str, Any]], Dict[str, Any]]) -> Dict[str, Any]:
        """Extract first EVSE from list.
        
        Args:
            v: Either a single EVSE dict or a list of EVSE dicts
            
        Returns:
            Dict[str, Any]: The first EVSE dict from the list or the single EVSE dict
            
        Raises:
            ValueError: If the input is an empty list
        """
        if isinstance(v, list):
            if not v:
                raise ValueError("No EVSEs found in charge point data")
            return v[0]
        return v
