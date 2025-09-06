"""Base DTO class that all other DTOs inherit from."""
from __future__ import annotations
from typing import Any, Dict

from pydantic import BaseModel

#from .dto_protocol import DTOProtocol

class BaseDTO(BaseModel):  # Make protocol implementation explicit
    
    def dict(self, **kwargs: Any) -> Dict[str, Any]:  # noqa: A003
        """Convert the DTO to a dictionary using dataclasses.asdict.
        
        Args:
            **kwargs: Additional arguments for compatibility
            
        Returns:
            Dict representation of the DTO
        """
        return super().model_dump(**kwargs)
