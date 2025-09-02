"""Protocols defining the interfaces that DTOs must implement."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable

@runtime_checkable
class DTOProtocol(Protocol):
    """Protocol defining the interface that all DTOs must implement."""
    id: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    
    def dict(self, *,  # noqa: A003
            include: Optional[Any] = None,
            exclude: Optional[Any] = None,
            by_alias: bool = False,
            exclude_unset: bool = False,
            exclude_defaults: bool = False,
            exclude_none: bool = False,
            **kwargs: Any) -> Dict[str, Any]:
        """Convert the DTO to a dictionary."""
        ...

@runtime_checkable
class ChargePointDTOProtocol(DTOProtocol, Protocol):
    """Protocol defining the interface that ChargePointDTO must implement."""
    name: str
    location_id: str
    last_updated: datetime
    evse: EVSEDTOProtocol
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
    free_energy_wh: int
    non_billable_energy: int
    payment_method_id: str
    payment_method_type: str
    payment_status: str
    charging_state: str
    payment_details: Optional[Any]
    amount: Decimal
    total_amount: Decimal
    amount_due: Decimal
    currency_id: int
    status: str
    evse_status: str
    charging_state: str
    charging_periods: List['ChargingPeriodDTOProtocol']

@runtime_checkable
class ChargingPeriodDTOProtocol(DTOProtocol, Protocol):
    """Protocol defining the interface that ChargingPeriodDTO must implement."""
    start_time: datetime
    end_time: Optional[datetime]
    energy_kwh: float
    cost: float

# Re-export all protocols for type checking
__all__ = [
    'DTOProtocol',
    'ChargePointDTOProtocol',
    'EVSEDTOProtocol',
    'ConnectorDTOProtocol',
    'ChargingSessionDTOProtocol',
    'ChargingPeriodDTOProtocol',
]
