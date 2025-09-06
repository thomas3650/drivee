"""Base model class that provides common functionality for all models."""
from __future__ import annotations

from abc import abstractmethod
from typing import TypeVar, Generic
from ..dtos.base_dto import BaseDTO
from ..errors import BusinessRuleError

T = TypeVar("T", bound=BaseDTO)

class BaseModel(Generic[T]):
    """Base class for all models in the system.
    
    Models encapsulate DTOs and provide business logic. They should never expose
    DTOs directly to external code. Instead, they should provide business-relevant
    properties and methods that operate on the underlying DTO data.
    """
    _dto: T  # The underlying DTO
    def __init__(self, dto: T) -> None:
        """Initialize the model with a DTO.
        
        Args:
            dto: The DTO containing the raw data
        """
        self._dto = dto
        
    
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
