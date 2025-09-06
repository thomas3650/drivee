"""
PowerStats model that encapsulates power statistics business logic.
"""
from __future__ import annotations
from ..dtos.power_stats_dto import PowerStatsDTO
from .base_model import BaseModel
from .power_stats_history_entry import PowerStatsHistoryEntry

class PowerStatsBaseModel(BaseModel[PowerStatsDTO]):
    def __init__(self, dto: PowerStatsDTO) -> None:
        super().__init__(dto)

    @property
    def history(self) -> list[PowerStatsHistoryEntry]:
        return [PowerStatsHistoryEntry(entry) for entry in self._dto.history]
