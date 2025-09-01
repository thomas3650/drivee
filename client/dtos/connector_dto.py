"""Connector DTO model."""
from .base_dto import DTOBase

class Connector(DTOBase):
    """Model for a charging connector."""
    name: str
    status: str
    icon: str  # e.g., "type2"
    format: str  # e.g., "cable"
