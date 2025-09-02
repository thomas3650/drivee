"""DTO for charging session data transfer."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional, Any

from .base_dto import BaseDTO
from .charging_period_dto import ChargingPeriodDTO
from .dto_protocol import ChargingSessionDTOProtocol  # type: ignore # Used for type checking

@dataclass
class ChargingSessionDTO(BaseDTO):  # type: ignore[type-arg] # Implements ChargingSessionDTOProtocol
    """DTO representing a charging session in the system.
    
    This DTO contains all data related to a charging session, including:
    - Session status and timestamps
    - Payment and billing information
    - Energy consumption data
    - User and charger details
    """
    # Required fields from BaseDTO
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Required fields from ChargingSessionDTOProtocol
    evse_id: str = ""
    started_at: datetime = field(default_factory=datetime.now)
    stopped_at: Optional[datetime] = None
    duration: int = 0
    free_energy_wh: int = 0
    non_billable_energy: int = 0
    payment_method_id: str = ""
    payment_method_type: str = ""
    payment_status: str = ""
    charging_state: str = ""
    payment_details: Optional[Any] = None
    amount: Decimal = field(default_factory=lambda: Decimal('0'))
    total_amount: Decimal = field(default_factory=lambda: Decimal('0'))
    amount_due: Decimal = field(default_factory=lambda: Decimal('0'))
    currency_id: int = 0
    status: str = ""
    evse_status: str = ""
    charging_periods: List[ChargingPeriodDTO] = field(default_factory=lambda: list())

    # Additional fields not in protocol
    charge_point_id: str = ""
    connector_id: str = ""
    current_power: Decimal = field(default_factory=lambda: Decimal('0'))  # Power in kW
    max_power: Decimal = field(default_factory=lambda: Decimal('0'))  # Max power in kW
    metadata: Dict[str, Any] = field(default_factory=lambda: dict())
