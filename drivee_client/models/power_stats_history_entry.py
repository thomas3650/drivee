"""
PowerStatsHistoryEntry model that encapsulates power stats history entry business logic.
"""
from __future__ import annotations
from ..dtos.power_stats_dto import PowerStatsHistoryEntryDTO

class PowerStatsHistoryEntry:
    def __init__(self, dto: PowerStatsHistoryEntryDTO) -> None:
        self._dto = dto

    @property
    def value(self) -> float:
        return self._dto.value

    @property
    def timestamp(self) -> str:
        return self._dto.timestamp
