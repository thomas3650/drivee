"""Type protocols for DTOs."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Protocol, runtime_checkable

from .base_model import DTOProtocol

@runtime_checkable
class ChargePointDTOProtocol(DTOProtocol, Protocol):
    """Protocol defining the interface that ChargePointDTO must implement."""
    name: str
    location_id: str
    last_updated: datetime
    evses: List['EVSEDTOProtocol']
    status: str
    photo: Optional[str]
    plug_and_charge: bool
    smart_charging_enabled: bool
    allowed_min_current_a: int
    allowed_max_current_a: int
    allowed_max_power_kw: str
    max_current_a: int
    is_rebooting: bool

@runtime_checkable
class EVSEDTOProtocol(DTOProtocol, Protocol):
    """Protocol defining the interface that EVSEDTO must implement."""
    status: str
    connectors: List['ConnectorDTOProtocol']

@runtime_checkable
class ConnectorDTOProtocol(DTOProtocol, Protocol):
    """Protocol defining the interface that ConnectorDTO must implement."""
    type: str
    status: str
    max_power: float

@runtime_checkable
class ChargingSessionDTOProtocol(DTOProtocol, Protocol):
    """Protocol defining the interface that ChargingSessionDTO must implement."""
    evse_id: str
    started_at: datetime
    stopped_at: Optional[datetime]
    duration: int
    energy: int
    power: int
    total_amount: str
    currency_id: int
    status: str
    charging_state: str
    charging_periods: List['ChargingPeriodDTOProtocol']

@runtime_checkable
class ChargingPeriodDTOProtocol(DTOProtocol, Protocol):
    """Protocol defining the interface that ChargingPeriodDTO must implement."""
    start_time: datetime
    end_time: Optional[datetime]
    energy_kwh: float
    cost: float
