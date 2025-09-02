"""
Connector model that encapsulates connector business logic.
"""

from enum import Enum
from typing import Protocol

from ..dtos.connector_dto import ConnectorDTO
from .base_model import BaseModel

class ConnectorStatus(Enum):
    """Valid connector statuses."""
    AVAILABLE = 'Available'
    OCCUPIED = 'Occupied'
    RESERVED = 'Reserved'
    UNAVAILABLE = 'Unavailable'
    FAULTED = 'Faulted'

class ConnectorProtocol(Protocol):
    """Protocol defining the interface that ConnectorDTO must implement."""
    id: str
    type: str
    status: str
    max_power: float
    
class Connector(BaseModel['ConnectorDTO']):
    """Model representing a charging connector with its business logic.
    
    This model encapsulates the ConnectorDTO and provides business-relevant
    properties and methods while enforcing business rules.
    """
    
    def __init__(self, dto: ConnectorDTO) -> None:
        super().__init__(dto)
    
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
    
    def validate_business_rules(self) -> bool:
        """Validate that this connector satisfies all business rules.
        
        Business Rules:
        - Type must not be empty
        - Status must be a valid value
        - Maximum power must be positive
        
        Returns:
            bool: True if all business rules are satisfied, False otherwise
        """
        if not self.type:
            return False
            
        try:
            ConnectorStatus(self._dto.status)
        except ValueError:
            return False
            
        if self.max_power <= 0:
            return False
            
        return True
