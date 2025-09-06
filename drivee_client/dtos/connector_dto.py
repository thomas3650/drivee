"""DTO for charging connector data transfer."""
from __future__ import annotations

from .base_dto import BaseDTO
from pydantic import Field

class ConnectorDTO(BaseDTO):
    name: str = Field(..., alias="name")
    status: str = Field(..., alias="status")
    icon: str = Field(..., alias="icon")
    format: str = Field(..., alias="format")
