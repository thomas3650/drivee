"""Connector DTO model."""
from .base_dto import DTOBase

class Connector(DTOBase):
    """Model for a charging connector."""
    name: str
    status: str
