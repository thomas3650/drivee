"""Base model class that provides common functionality for all models."""
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Generic, Optional, TypeVar

from ..dtos.dto_protocol import DTOProtocol

# Type variable for our model's DTO type
D = TypeVar('D', bound=DTOProtocol, covariant=True)

class ModelError(Exception):
    """Base class for all model-related errors."""
    pass

class BusinessRuleError(ModelError):
    """Error raised when a business rule is violated."""
    pass

class ValidationError(ModelError):
    """Error raised when model validation fails."""
    pass

class BaseModel(Generic[D], ABC):
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
        
    Raises:
        ValidationError: If the provided DTO doesn't match the required protocol
    """
    
    def __init__(self, dto: D) -> None:
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

    
    @abstractmethod
    def validate_business_rules(self) -> None:
        """Validate that this model satisfies all business rules.
        
        Each model class must implement this method to enforce its specific
        business rules. This is separate from DTO validation, which only
        handles data structure validation.
        
        Raises:
            BusinessRuleError: If any business rule is violated
            
        Example:
            ```python
            def validate_business_rules(self) -> None:
                if not self.name:
                    raise BusinessRuleError("Name cannot be empty")
                if self.price < 0:
                    raise BusinessRuleError("Price must be non-negative")
            ```
        """
        ...
    
    def is_valid(self) -> bool:
        """Check if the model is in a valid state.
        
        This combines DTO validation with business rule validation.
        
        Returns:
            bool: True if both the DTO and business rules are valid
        """
        try:
            self.validate_business_rules()
            return True
        except BusinessRuleError:
            return False
