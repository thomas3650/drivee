"""
EVSE (Electric Vehicle Supply Equipment) model that encapsulates EVSE business logic.
"""

from typing import List, Optional, Protocol

from ..dtos.connector_dto import ConnectorDTO
from ..dtos.evse_dto import EVSEDTO
from .base_model import BaseModel
from .connector import Connector

class EVSEProtocol(Protocol):
    """Protocol defining the interface that EVSEDTO must implement."""
    id: str
    status: str
    connectors: List[ConnectorDTO]

class EVSE(BaseModel['EVSEDTO']):
    """Model representing an EVSE with its business logic.
    
    This model encapsulates the EVSEDTO and provides business-relevant
    properties and methods while enforcing business rules.
    """
    
    def __init__(self, dto: EVSEDTO) -> None:
        super().__init__(dto)
        self._connectors = [Connector(conn) for conn in dto.connectors]
    
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
    
    def validate_business_rules(self) -> bool:
        """Validate that this EVSE satisfies all business rules.
        
        Business Rules:
        - Must have at least one connector
        - All connectors must be valid
        - Status must be a valid value
        
        Returns:
            bool: True if all business rules are satisfied, False otherwise
        """
        if not self._connectors:
            return False
            
        if not all(conn.validate_business_rules() for conn in self._connectors):
            return False
            
        valid_statuses = {'Available', 'Occupied', 'Reserved', 'Unavailable', 'Faulted'}
        if self.status not in valid_statuses:
            return False
            
        return True
