"""
Connector model that encapsulates connector business logic.
"""
from __future__ import annotations

from typing import cast

from ..dtos.connector_dto import ConnectorDTO
from .base_model import BaseModel, BusinessRuleError
from .protocols import ConnectorDTOProtocol
from .types import ConnectorStatus

class Connector(BaseModel[ConnectorDTOProtocol]):
    """Model representing a charging connector with its business logic.
    
    This model encapsulates the ConnectorDTO and provides business-relevant
    properties and methods while enforcing business rules.
    """
    _dto: ConnectorDTOProtocol  # Type hint for the DTO
    
    def __init__(self, dto: ConnectorDTO) -> None:
        """Initialize a new connector.
        
        Args:
            dto: The DTO containing the connector data
            
        Raises:
            ValidationError: If the DTO is invalid
        """
        super().__init__(cast(ConnectorDTOProtocol, dto))
    
    @property
    def type(self) -> str:
        """Get the connector type (e.g., 'Type2', 'CCS')."""
        return self._dto.type
    
    @property
    def status(self) -> ConnectorStatus:
        """Get the current status of the connector."""
        return ConnectorStatus(self._dto.status)
    
    @property
    def max_power(self) -> float:
        """Get the maximum power output in kW."""
        return self._dto.max_power
    
    @property
    def is_available(self) -> bool:
        """Check if the connector is available for charging."""
        return self.status == ConnectorStatus.AVAILABLE
    
    def can_provide_power(self, required_power: float) -> bool:
        """Check if this connector can provide the required power.
        
        Args:
            required_power: Power required in kW
            
        Returns:
            bool: True if this connector can provide the required power
        """
        return self.max_power >= required_power
    
    def validate_business_rules(self) -> None:
        """Validate that this connector satisfies all business rules.
        
        Business Rules:
        - Type must not be empty
        - Status must be a valid value
        - Maximum power must be positive
        
        Raises:
            BusinessRuleError: If any business rule is violated
        """
        if not self.type:
            raise BusinessRuleError("Connector type must not be empty")
            
        try:
            ConnectorStatus(self._dto.status)
        except ValueError:
            valid_statuses = [status.value for status in ConnectorStatus]
            raise BusinessRuleError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
            
        if self.max_power <= 0:
            raise BusinessRuleError("Maximum power must be positive")
