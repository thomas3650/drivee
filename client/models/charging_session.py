"""
ChargingSession model that encapsulates charging session business logic.
"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional, cast

from ..dtos.charging_session_dto import ChargingSessionDTO
from .base_model import BaseModel, BusinessRuleError
from ..dtos.dto_protocol import ChargingSessionDTOProtocol

class ChargingSession(BaseModel[ChargingSessionDTOProtocol]):
    """Model representing a charging session with its business logic.
    
    This model encapsulates the ChargingSessionDTO and provides business-relevant
    properties and methods while enforcing business rules.
    
    Business Rules:
    - Session must have a valid EVSE ID
    - Started_at must be set and be in the past
    - If stopped_at is set, it must be after started_at
    - Duration must match the time between started_at and stopped_at
    - Energy and power values must be non-negative
    - Total amount must be non-negative
    """
    
    def __init__(self, dto: ChargingSessionDTO) -> None:
        """Initialize a new charging session.
        
        Args:
            dto: The DTO containing the charging session data
            
        Raises:
            ValidationError: If the DTO is invalid
        """
        super().__init__(cast(ChargingSessionDTOProtocol, dto))
    
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
        """Get when the charging session stopped, if it has stopped."""
        return self._dto.stopped_at
    
    @property
    def duration(self) -> int:
        """Get the duration of the session in seconds."""
        return self._dto.duration
    
    @property
    def free_energy_wh(self) -> int:
        """Get the free energy delivered in Wh."""
        return self._dto.free_energy_wh
    
    @property
    def non_billable_energy(self) -> int:
        """Get the non-billable energy in Wh."""
        return self._dto.non_billable_energy
    
    @property
    def amount(self) -> Decimal:
        """Get the current amount charged for this session."""
        return self._dto.amount
        
    @property
    def total_amount(self) -> Decimal:
        """Get the total amount charged including fees."""
        return self._dto.total_amount
    
    @property
    def amount_due(self) -> Decimal:
        """Get the amount still to be paid."""
        return self._dto.amount_due
    
    @property
    def payment_status(self) -> str:
        """Get the current payment status."""
        return str(self._dto.payment_status)
        
    @property
    def charging_state(self) -> str:
        """Get the current charging state."""
        return str(self._dto.charging_state)
        
    @property
    def currency_id(self) -> int:
        """Get the ID of the currency used for payment."""
        return self._dto.currency_id
    
    @property
    def status(self) -> str:
        """Get the overall status of the session."""
        return self._dto.status
        
    @property
    def evse_status(self) -> str:
        """Get the EVSE status during this session."""
        return self._dto.evse_status
    
    @property
    def is_active(self) -> bool:
        """Check if the charging session is currently active."""
        return self.stopped_at is None
    
    @property
    def calculated_duration(self) -> int:
        """Calculate the session duration based on timestamps.
        
        This is useful for validating the stored duration value.
        
        Returns:
            Duration in seconds, or 0 if started_at is not set
        """
        if not self.started_at:
            return 0
            
        end_time = self.stopped_at or datetime.now()
        duration = (end_time - self.started_at).total_seconds()
        return int(duration)
    
    def validate_business_rules(self) -> None:
        """Validate that this charging session satisfies all business rules.
        
        Business Rules:
        - Session must have a valid EVSE ID
        - Started_at must be set and be in the past
        - If stopped_at is set, it must be after started_at
        - Duration must match the time between started_at and stopped_at
        - Energy and power values must be non-negative
        - Total amount must be non-negative
        
        Raises:
            BusinessRuleError: If any business rule is violated
        """
        if not self.evse_id:
            raise BusinessRuleError("EVSE ID must be set")
            
        if not self.started_at:
            raise BusinessRuleError("Start time must be set")
            
        if self.started_at > datetime.now():
            raise BusinessRuleError("Start time cannot be in the future")
            
        if self.stopped_at and self.stopped_at <= self.started_at:
            raise BusinessRuleError("Stop time must be after start time")
            
        # Allow some tolerance in duration validation (±5 seconds)
        calculated_duration = self.calculated_duration
        if abs(calculated_duration - self.duration) > 5:
            raise BusinessRuleError(
                f"Duration ({self.duration}s) does not match time between "
                f"start and stop ({calculated_duration}s)"
            )
            
        if self.free_energy_wh < 0:
            raise BusinessRuleError("Free energy must be non-negative")
            
        if self.non_billable_energy < 0:
            raise BusinessRuleError("Non-billable energy must be non-negative")
            
        if self.total_amount < 0:
            raise BusinessRuleError("Total amount must be non-negative")
