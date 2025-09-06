from pydantic import  Field
from typing import List

from .base_dto import BaseDTO

class PowerStatsHistoryEntryDTO(BaseDTO):
    value: float = Field(..., alias="value")
    timestamp: str = Field(..., alias="timestamp")

class PowerStatsDTO(BaseDTO):
    history: List[PowerStatsHistoryEntryDTO] = Field(..., alias="history")
