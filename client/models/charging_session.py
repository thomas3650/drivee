"""
ChargingSession model that encapsulates charging session business logic.
"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from ..dtos.charging_session_dto import ChargingSessionDTO
from ..dtos.charging_period_dto import ChargingPeriodDTO
from .base_model import BaseModel
from ..models.types import ChargingStateType

class ChargingSessionStatus:
    """Valid charging session statuses."""
    ACTIVE = 'Active'
    COMPLETED = 'Completed'
    STOPPED = 'Stopped'
    FAULTED = 'Faulted'

class ChargingSession(BaseModel[ChargingSessionDTO]):
    """Model representing a charging session with its business logic.
    
    This model encapsulates the ChargingSessionDTO and provides business-relevant
    properties and methods while enforcing business rules.
    """
    
    def __init__(self, dto: ChargingSessionDTO) -> None:
        """Initialize a new charging session.
        
        Args:
            dto: The DTO containing the charging session data
        """
        super().__init__(dto)
    
    @property
    def evse_id(self) -> str:
        """Get the ID of the EVSE used for this session."""
        return self._dto.evse_id
    
    @property
    def started_at(self) -> datetime:
        """Get when the charging session started."""
        return self._dto.started_at
    
    @property
    def stopped_at(self) -> Optional[datetime]:
        """Get when the charging session ended, if it has ended."""
        return self._dto.stopped_at
    
    @property
    def duration(self) -> int:
        """Get the current duration in seconds."""
        return self._dto.duration
    
    @property
    def energy(self) -> int:
        """Get the total energy delivered in Wh."""
        return self._dto.energy
    
    @property
    def power(self) -> int:
        """Get the current power in W."""
        return self._dto.power
    
    @property
    def total_amount(self) -> Decimal:
        """Get the total amount charged including fees."""
        return self._dto.total_amount
    
    @property
    def currency_id(self) -> int:
        """Get the ID of the billing currency."""
        return self._dto.currency_id
    
    @property
    def status(self) -> str:
        """Get the overall session status."""
        return self._dto.status
    
    @property
    def charging_state(self) -> ChargingStateType:
        """Get the current charging state."""
        return self._dto.charging_state
    
    @property
    def charging_periods(self) -> List[ChargingPeriodDTO]:
        """Get all charging periods in this session."""
        return self._dto.charging_periods
    
    @property
    def last_period(self) -> Optional[ChargingPeriodDTO]:
        """Get the most recent charging period."""
        return self._dto.last_period
    
    def validate_business_rules(self) -> bool:
        """Validate that this charging session satisfies all business rules.
        
        Business Rules:
        1. Session must have a valid EVSE ID
        2. Start time must be before end time if session has ended
        3. Energy and power values must be non-negative
        4. Total amount must be non-negative
        5. Must have at least one charging period
        
        Returns:
            bool: True if all business rules are satisfied, False otherwise
        """
        # Must have valid EVSE ID
        if not self.evse_id:
            return False
            
        # If ended, end time must be after start time
        if self.stopped_at and self.stopped_at <= self.started_at:
            return False
            
        # Energy and power must be non-negative
        if self.energy < 0 or self.power < 0:
            return False
            
        # Amount must be non-negative
        if self.total_amount < Decimal(0):
            return False
            
        # Must have at least one charging period
        if not self.charging_periods:
            return False
            
        return True
