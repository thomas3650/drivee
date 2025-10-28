"""
EVSE (Electric Vehicle Supply Equipment) model that encapsulates EVSE business logic.
"""
from __future__ import annotations

from typing import List

from .charging_session import ChargingSession

from ..dtos.evse_dto import EVSEDTO
from .base_model import BaseModel, BusinessRuleError
from .connector import Connector
from .types import EVSEStatus

class EVSE(BaseModel[EVSEDTO]):
    """Model representing an EVSE with its business logic.
    
    This model encapsulates the EVSEDTO and provides business-relevant
    properties and methods while enforcing business rules.
    """
    
    def __init__(self, dto: EVSEDTO) -> None:
        """Initialize a new EVSE.
        
        Args:
            dto: The DTO containing the EVSE data
            
        Raises:
            ValidationError: If the DTO is invalid
        """
        super().__init__(dto)
        self._dto: EVSEDTO = dto
        self._connectors = [Connector(conn) for conn in dto.connectors or []]
    
    @property
    def session(self) -> ChargingSession | None:
        """Get the current charging session associated with this EVSE, if any."""
        if self._dto.session:
            return ChargingSession(self._dto.session)
        return None

    @property
    def status(self) -> EVSEStatus:
        """Get the current status of the EVSE.
        
        Returns:
            EVSEStatus: The current operational status of the EVSE
        
        Raises:
            ValueError: If the status from DTO is not a valid EVSEStatus value
        """
        return EVSEStatus(self._dto.status)
    
    @property
    def connectors(self) -> List[Connector]:
        """Get all connectors on this EVSE."""
        return self._connectors
    
    @property
    def id(self) -> str:
        """Get the ID of this EVSE."""
        return self._dto.id

    @property
    def is_charging(self) -> bool:
        """Check if this EVSE is currently in a charging state.
        
        Returns:
            bool: True if the EVSE is in a charging, suspended, or pending state
        """
        return self.status in (
            EVSEStatus.CHARGING,
            EVSEStatus.SUSPENDED,
            EVSEStatus.PENDING
        )
    
    @property
    def is_connected(self) -> bool:
        return self.status in (
            EVSEStatus.CHARGING,
            EVSEStatus.SUSPENDED,
            EVSEStatus.PENDING,
            EVSEStatus.PREPARING
        )
        


    def get_available_connectors(self) -> List[Connector]:
        """Get all connectors that are currently available for charging.
        
        Returns:
            List[Connector]: List of connectors that are available
        """
        return [conn for conn in self._connectors if conn.is_available]
    
    def validate_business_rules(self) -> None:
        """Validate that this EVSE satisfies all business rules.
        
        Business Rules:
        - Must have at least one connector
        - All connectors must be valid
        - Status must be a valid value
        
        Raises:
            BusinessRuleError: If any business rule is violated
        """
        if not self._connectors:
            raise BusinessRuleError("EVSE must have at least one connector")
            
        for conn in self._connectors:
            try:
                conn.validate_business_rules()
            except BusinessRuleError as e:
                raise BusinessRuleError(f"Invalid connector {conn.id}: {str(e)}")
            
        try:
            EVSEStatus(self.status)
        except ValueError:
            valid_statuses = [status.value for status in EVSEStatus]
            raise BusinessRuleError(f"Invalid status '{self.status}'. Must be one of: {', '.join(valid_statuses)}")
