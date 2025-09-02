"""
EVSE (Electric Vehicle Supply Equipment) model that encapsulates EVSE business logic.
"""
from __future__ import annotations

from typing import List, cast

from ..dtos.evse_dto import EVSEDTO
from .base_model import BaseModel, BusinessRuleError
from .connector import Connector
from .protocols import EVSEDTOProtocol
from .types import EVSEStatus

class EVSE(BaseModel[EVSEDTOProtocol]):
    """Model representing an EVSE with its business logic.
    
    This model encapsulates the EVSEDTO and provides business-relevant
    properties and methods while enforcing business rules.
    """
    _dto: EVSEDTOProtocol  # Type hint for the DTO
    
    def __init__(self, dto: EVSEDTO) -> None:
        """Initialize a new EVSE.
        
        Args:
            dto: The DTO containing the EVSE data
            
        Raises:
            ValidationError: If the DTO is invalid
        """
        super().__init__(cast(EVSEDTOProtocol, dto))
        self._connectors = [Connector(conn) for conn in dto.connectors or []]
    
    @property
    def status(self) -> str:
        """Get the current status of the EVSE."""
        return self._dto.status
    
    @property
    def connectors(self) -> List[Connector]:
        """Get all connectors on this EVSE."""
        return self._connectors
    
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
