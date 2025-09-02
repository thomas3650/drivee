"""Base DTO class that all other DTOs inherit from."""
from __future__ import annotations
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, Optional

from .dto_protocol import DTOProtocol

@dataclass
class BaseDTO(DTOProtocol):  # Make protocol implementation explicit
    """Base class for all DTOs.
    
    This class provides common functionality for all DTOs including:
    - JSON serialization/deserialization via dataclasses
    - Simple data structure with type hints
    - DTOProtocol implementation
    
    DTOs should:
    - Only contain data, no business logic
    - Match API response structures exactly
    - Use proper type hints
    - End with 'DTO' suffix in class name
    """
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def dict(self, **kwargs: Any) -> Dict[str, Any]:  # noqa: A003
        """Convert the DTO to a dictionary using dataclasses.asdict.
        
        Args:
            **kwargs: Additional arguments for compatibility
            
        Returns:
            Dict representation of the DTO
        """
        return asdict(self)
