"""
ChargingHistory model that encapsulates charging history business logic.
"""
from __future__ import annotations
from typing import List
from ..dtos.charging_history_dto import ChargingHistoryDTO
from .base_model import BaseModel, BusinessRuleError
from .charging_session import ChargingSession

class ChargingHistory(BaseModel[ChargingHistoryDTO]):
    """Model representing a collection of charging history entries with business logic."""
    _sessions: List[ChargingSession]

    def __init__(self, dto: ChargingHistoryDTO) -> None:
        super().__init__(dto)
        self._sessions = [ChargingSession(entry.session) for entry in dto.session_history or [] if entry.session]
        self.validate_business_rules()

    @property
    def sessions(self) -> List[ChargingSession]:
        """Get all charging sessions in the history."""
        return self._sessions
    
    @property
    def last_session(self) -> ChargingSession | None:
        """Get the most recent charging session, or None if there are no sessions."""
        return self._sessions[-1] if self._sessions else None

    def validate_business_rules(self) -> None:
        """Validate that this charging history satisfies all business rules.
        - Must have at least one session
        Raises:
            BusinessRuleError: If any business rule is violated
        """
        if not self._sessions:
            raise BusinessRuleError("Charging history must have at least one session")
