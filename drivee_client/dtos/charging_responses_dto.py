"""DTOs for charging operation responses."""
from __future__ import annotations

from .base_dto import BaseDTO
from .charging_session_dto import ChargingSessionDTO
from pydantic import Field


class ChargingResponseDTO(BaseDTO):
    session: ChargingSessionDTO = Field(..., alias="session")

