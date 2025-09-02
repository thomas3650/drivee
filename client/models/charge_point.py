"""
ChargePoint model that encapsulates charge point business logic.
"""

from datetime import datetime
from typing import List, Protocol

from ..dtos.charge_point_dto import ChargePointDTO
from ..dtos.connector_dto import ConnectorDTO
from ..dtos.evse_dto import EVSEDTO
from .base_model import BaseModel
from .connector import Connector
from .evse import EVSE

class ChargePointProtocol(Protocol):
    """Protocol defining the interface that ChargePointDTO must implement."""
    id: str
    name: str
    location_id: str
    evses: List[EVSEDTO]
    last_updated: datetime
    
class ChargePoint(BaseModel['ChargePointDTO']):
    """Model representing a charging point with its business logic.
    
    This model encapsulates the ChargePointDTO and provides business-relevant
    properties and methods while enforcing business rules.
    """
    
    def __init__(self, dto: ChargePointDTO) -> None:
        super().__init__(dto)
        self._evses = [EVSE(evse) for evse in dto.evses]
    
    @property
    def name(self) -> str:
        """Get the name of the charge point."""
        return self._dto.name
    
    @property
    def location_id(self) -> str:
        """Get the location ID where this charge point is installed."""
        return self._dto.location_id
    
    @property
    def evses(self) -> List[EVSE]:
        """Get all EVSEs (Electric Vehicle Supply Equipment) at this charge point."""
        return self._evses
    
    @property
    def last_updated(self) -> datetime:
        """Get the last time this charge point was updated."""
        return self._dto.last_updated
    
    def get_available_connectors(self) -> List[Connector]:
        """Get all available connectors across all EVSEs.
        
        Returns:
            List[Connector]: List of connectors that are currently available for charging
        """
        available = []
        for evse in self._evses:
            available.extend(evse.get_available_connectors())
        return available
    
    def validate_business_rules(self) -> bool:
        """Validate that this charge point satisfies all business rules.
        
        Business Rules:
        - Must have at least one EVSE
        - All EVSEs must be valid
        - Location ID must be set
        - Name must not be empty
        
        Returns:
            bool: True if all business rules are satisfied, False otherwise
        """
        if not self._evses:
            return False
            
        if not all(evse.validate_business_rules() for evse in self._evses):
            return False
            
        if not self.location_id:
            return False
            
        if not self.name:
            return False
            
        return True
