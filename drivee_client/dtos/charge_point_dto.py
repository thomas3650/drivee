"""DTOs for charge point data transfer."""
from __future__ import annotations

from typing import List

from pydantic import Field

from .base_dto import BaseDTO
from .evse_dto import EVSEDTO

class ChargePointDTO(BaseDTO):  
    id: str = Field(..., alias="id")
    name: str = Field(..., alias="name")
    status: str = Field(..., alias="status")
    photo: str = Field(..., alias="photo")
    allowed_max_power_kw: str = Field(..., alias="allowed_max_power_kw")
    evses: List[EVSEDTO] = Field(default_factory=lambda: [], alias="evses")
    connector_lock: bool = Field(..., alias="connector_lock")
