"""DTO for EVSE (Electric Vehicle Supply Equipment) data transfer."""
from __future__ import annotations

from typing import List

from pydantic import Field

from .base_dto import BaseDTO
from .connector_dto import ConnectorDTO


class EVSEDTO(BaseDTO):
    """DTO representing an EVSE that implements EVSEDTOProtocol.

    An EVSE is a physical charging station unit that may have multiple connectors.
    This DTO represents the pure data structure without any business logic.
    """
    id: str = Field(..., alias="id")
    # Required fields from EVSEDTOProtocol
    status: str = Field(..., alias="status")
    connectors: List[ConnectorDTO] = Field(..., alias="connectors")

    # Additional fields
    identifier: str = Field(..., alias="identifier")
