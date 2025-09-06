"""
ChargePoint model that encapsulates charge point business logic.
"""

from __future__ import annotations

from typing import List

from ..dtos.charge_point_dto import ChargePointDTO

from .base_model import BaseModel, BusinessRuleError
from .evse import EVSE

class ChargePoint(BaseModel[ChargePointDTO]):
    """Model representing a charging point with its business logic.
    
    This model encapsulates the ChargePointDTO and provides business-relevant
    properties and methods while enforcing business rules.
    """

    _evses: List[EVSE]

    def __init__(self, dto: ChargePointDTO) -> None:
        """Initialize a new charge point.
        
        Args:
            dto: The DTO containing the charge point data
            
        Raises:
            ValidationError: If the DTO is invalid
        """
        super().__init__(dto)
        self._evses: List[EVSE] = [EVSE(evse) for evse in dto.evses or []]
        self.validate_business_rules()
    
    @property
    def name(self) -> str:
        """Get the name of the charge point."""
        return self._dto.name  
        
    @property
    def evse(self) -> EVSE:
        """Get EVSE (Electric Vehicle Supply Equipment) at this charge point."""
        return self._evses[0]    
    
    def validate_business_rules(self) -> None:
        if not self._evses:
            raise BusinessRuleError("Charge point must have at least one EVSE")
            
        for evse in self._evses:
            try:
                evse.validate_business_rules()
            except BusinessRuleError as e:
                raise BusinessRuleError(f"Invalid EVSE {evse.id}: {str(e)}")
        if(len(self._evses) > 1):
            raise BusinessRuleError("Charge point must have only one EVSE")
            
        if not self.name:
            raise BusinessRuleError("Name must not be empty")
    
    @classmethod
    def from_dtos(cls, charge_points: List[ChargePointDTO]) -> "ChargePoint":
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
