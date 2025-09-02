"""
ChargePoint model that encapsulates charge point business logic.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, cast

from ..dtos.charge_point_dto import ChargePointDTO
from .base_model import BaseModel, BusinessRuleError
from .connector import Connector
from .evse import EVSE
from ..dtos.dto_protocol import ChargePointDTOProtocol

class ChargePoint(BaseModel[ChargePointDTOProtocol]):
    """Model representing a charging point with its business logic.
    
    This model encapsulates the ChargePointDTO and provides business-relevant
    properties and methods while enforcing business rules.
    """

    _dto: ChargePointDTOProtocol  # Type hint for the DTO

    def __init__(self, dto: ChargePointDTO) -> None:
        """Initialize a new charge point.
        
        Args:
            dto: The DTO containing the charge point data
            
        Raises:
            ValidationError: If the DTO is invalid
        """
        super().__init__(cast(ChargePointDTOProtocol, dto))
        self._evses = [EVSE(evse) for evse in dto.evses or []]
    
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
        available: List[Connector] = []
        for evse in self._evses:
            connectors = evse.get_available_connectors()
            available.extend(connectors)
        return available
    
    def validate_business_rules(self) -> None:
        """Validate that this charge point satisfies all business rules.
        
        Business Rules:
        - Must have at least one EVSE
        - All EVSEs must be valid
        - Location ID must be set
        - Name must not be empty
        
        Raises:
            BusinessRuleError: If any business rule is violated
        """
        if not self._evses:
            raise BusinessRuleError("Charge point must have at least one EVSE")
            
        for evse in self._evses:
            try:
                evse.validate_business_rules()
            except BusinessRuleError as e:
                raise BusinessRuleError(f"Invalid EVSE {evse.id}: {str(e)}")
            
        if not self.location_id:
            raise BusinessRuleError("Location ID must be set")
            
        if not self.name:
            raise BusinessRuleError("Name must not be empty")
    
    @classmethod
    def from_dtos(cls, charge_points: List[ChargePointDTO]) -> "ChargePoint":
        """Create a ChargePoint from a list of DTOs.
        
        Business Rules:
        - Must have exactly one charge point
        - The charge point must be valid
        
        Args:
            charge_points: List of charge point DTOs
            
        Returns:
            ChargePoint: A validated charge point instance
            
        Raises:
            BusinessRuleError: If no charge points or multiple charge points are found
        """
        if not charge_points:
            raise BusinessRuleError("No charge points found")
            
        if len(charge_points) > 1:
            raise BusinessRuleError(
                f"Multiple charge points found ({len(charge_points)}), expected exactly one"
            )
            
        # Create and validate instance
        instance = cls(charge_points[0])
        instance.validate_business_rules()
        
        return instance
