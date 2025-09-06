"""DTO for charging session data transfer."""
from __future__ import annotations
from datetime import datetime
from decimal import Decimal
from typing import Dict, Optional, Any

from pydantic import Field

from .base_dto import BaseDTO
from .charging_period_dto import ChargingPeriodDTO
from .currency_dto import CurrencyDTO
from .power_stats_dto import PowerStatsDTO

class ChargingSessionDTO(BaseDTO):
    id: str = Field(..., alias="id")
    started_at: datetime = Field(..., alias="startedAt")
    stopped_at: Optional[datetime] = Field(default=None, alias="stoppedAt")
    duration: int = Field(..., alias="duration")
    total_duration: int = Field(..., alias="totalDuration")
    energy: int = Field(..., alias="energy")
    power: int = Field(..., alias="power")
    location_id: Optional[str] = Field(default=None, alias="locationId")
    evse_id: str = Field(..., alias="evseId")
    evse_status: str = Field(..., alias="evseStatus")
    payment_method_id: str = Field(..., alias="paymentMethodId")
    payment_method_type: str = Field(..., alias="paymentMethodType")
    amount: Decimal = Field(..., alias="amount")
    total_amount: Decimal = Field(..., alias="totalAmount")
    amount_due: Decimal = Field(..., alias="amountDue")
    status: str = Field(..., alias="status")
    charging_state: Optional[str] = Field(default=None, alias="chargingState")
    payment_status: Optional[str] = Field(default=None, alias="paymentStatus")
    charging_periods: list[ChargingPeriodDTO] = Field(default_factory=list, alias="chargingPeriods")  # type: ignore
    charge_point_id: Optional[str] = Field(default=None, alias="chargePointId")
    connector_id: Optional[str] = Field(default=None, alias="connectorId")
    current_power: Optional[Decimal] = Field(default=None, alias="currentPower")
    max_power: Optional[Decimal] = Field(default=None, alias="maxPower")
    metadata: Dict[str, Any] = Field(default_factory=dict, alias="metadata")
    power_stats: Optional[PowerStatsDTO] = Field(default=None, alias="powerStats")
    currency: CurrencyDTO = Field(alias="currency")
