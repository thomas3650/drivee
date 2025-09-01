"""Base model for all DTOs."""
from pydantic import BaseModel, ConfigDict

class DTOBase(BaseModel):
    """Base class for all DTOs with JSON serialization support."""
    model_config = ConfigDict(
        alias_generator=lambda s: ''.join(word.capitalize() if i else word for i, word in enumerate(s.split('_'))),
        populate_by_name=True,
        extra='ignore'  # Ignore extra fields from API
    )
