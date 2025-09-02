"""Base model class that provides common functionality for all models."""
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Generic, Optional, Protocol, TypeVar, runtime_checkable

@runtime_checkable
class DTOProtocol(Protocol):
    """Protocol defining the interface that all DTOs must implement."""
    id: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    
    def dict(self, **kwargs: Any) -> Dict[str, Any]:
        """Convert the DTO to a dictionary."""
        ...
        
    def model_dump(self, **kwargs: Any) -> Dict[str, Any]:
        """Dump the model to a dictionary."""
        ...

# Type variable bound to our DTO protocol
T = TypeVar('T', bound=DTOProtocol)

class BaseModel(Generic[T], ABC):
    """Base class for all models in the system.
    
    Models encapsulate DTOs and provide business logic. They should never expose
    DTOs directly to external code. Instead, they should provide business-relevant
    properties and methods that operate on the underlying DTO data.
    
    Args:
        dto: The DTO that this model wraps
        
    Properties that all models should implement:
        id (str): Unique identifier for the model
        created_at (Optional[datetime]): When the entity was created
        updated_at (Optional[datetime]): When the entity was last updated
    """
    
    def __init__(self, dto: T) -> None:
        """Initialize the model with a DTO.
        
        Args:
            dto: The DTO containing the raw data
        """
        self._dto = dto
    
    @property
    def id(self) -> str:
        """Get the ID of the model."""
        return str(self._dto.id)
    
    @property
    def created_at(self) -> Optional[datetime]:
        """Get when this entity was created."""
        return self._dto.created_at
    
    @property
    def updated_at(self) -> Optional[datetime]:
        """Get when this entity was last updated."""
        return self._dto.updated_at
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the model to a dictionary representation.
        
        This method should be used when exposing the model data externally.
        It uses the underlying DTO's serialization but may add or transform
        fields based on business logic.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the model
        """
        return self._dto.model_dump()
    
    @abstractmethod
    def validate_business_rules(self) -> bool:
        """Validate that this model satisfies all business rules.
        
        Each model class must implement this method to enforce its specific
        business rules. This is separate from DTO validation, which only
        handles data structure validation.
        
        Returns:
            bool: True if all business rules are satisfied, False otherwise
            
        Example:
            ```python
            def validate_business_rules(self) -> bool:
                if not self.name:
                    return False
                if self.price < 0:
                    return False
                return True
            ```
        """
        ...
    """Model representing a charging session with its business logic.
    
    This model encapsulates the ChargingSessionDTO and provides business-relevant
    properties and methods while enforcing business rules.
    """
    

    
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
