"""Base DTO class that all other DTOs inherit from."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

class BaseDTO(BaseModel):
    """Base class for all DTOs.
    
    This class provides common functionality for all DTOs including:
    - JSON serialization/deserialization
    - Camel case field name conversion for API compatibility
    - Strict data validation
    - Extra field handling
    
    DTOs should:
    - Only contain data, no business logic
    - Match API response structures exactly
    - Use proper field typing and validation
    - End with 'DTO' suffix in class name
    """
    id: str = Field(description="Unique identifier")
    created_at: Optional[datetime] = Field(
        default=None,
        description="When this entity was created"
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        description="When this entity was last updated"
    )

    model_config = ConfigDict(
        alias_generator=lambda s: ''.join(word.capitalize() if i else word for i, word in enumerate(s.split('_'))),
        populate_by_name=True,
        extra='ignore'  # Ignore extra fields from API
    )
