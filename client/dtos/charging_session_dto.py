"""ChargingSession DTO."""
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional, Any
from pydantic import Field, field_validator

from .base_dto import DTOBase
from .payment_details_dto import PaymentDetails
from .currency_dto import Currency
from .smart_charging_dto import SmartCharging
from .charging_period_dto import ChargingPeriod

class ChargingSession(DTOBase):
    """Model for a charging session."""
    id: str
    started_at: datetime
    duration: int = Field(ge=0)
    total_duration: int = Field(ge=0)
    energy: int = Field(ge=0)
    power: int = Field(ge=0)
    location_id: Optional[str] = None
    evse_id: str
    evse_status: str
    payment_method_id: str
    payment_method_type: str
    amount: Decimal = Field(ge=0)
    total_amount: Decimal = Field(ge=0)
    amount_due: Decimal = Field(ge=0)
    status: str
    summary_seen: bool
    payment_status: str
    payment_details: Optional[PaymentDetails] = None
    is_extending: bool
    is_extended: bool
    is_optimized: bool
    stop_reason: Optional[str] = None
    charging_state: str
    is_session_timed_out: bool
    stopped_at: Optional[datetime] = None
    is_personal: bool
    reimbursement_eligibility: bool
    can_toggle_reimbursement_eligibility: bool
    has_third_party_electricity_cost_integration_enabled: Optional[bool] = None
    non_billable_energy: int = Field(ge=0)
    currency_id: int
    currency: Currency
    smart_charging: SmartCharging
    electricity_cost: Decimal = Field(ge=0)
    electricity_cost_currency_id: int
    power_avg: float = Field(ge=0)
    is_using_charging_allowance: bool
    free_energy_wh: int = Field(ge=0)
    sca_pending_transaction: Optional[Any] = None
    idle_period: int = Field(ge=0)
    is_remote_stop_enabled: bool
    is_balance_payment_pending: bool
    charging_periods: List[ChargingPeriod] = []
    last_period: Optional[ChargingPeriod] = None
    idle_fee_eligible: bool
    tax_name: Optional[str] = None
    smart_charging_schedule: Optional[List[Dict[str, Any]]] = None
    power_stats: Optional[Dict[str, Any]] = None

    @property
    def is_active(self) -> bool:
        """Check if session is currently active."""
        return self.status == "active" and not self.stopped_at

    @property
    def total_cost(self) -> Decimal:
        """Calculate total cost including fees."""
        return self.amount + self.amount_due

    @property
    def duration_minutes(self) -> float:
        """Get duration in minutes."""
        return self.duration / 60

    @property
    def average_power_kw(self) -> float:
        """Calculate average power in kW."""
        if self.duration == 0:
            return 0.0
        return self.energy / (self.duration / 3600)  # kWh per hour

    @field_validator('charging_state')
    @classmethod
    def validate_charging_state(cls, v: str) -> str:
        """Validate charging state value."""
        valid_states = {"charging", "idle", "error", "disconnected"}
        if v not in valid_states:
            raise ValueError(f"Invalid charging state. Must be one of {valid_states}")
        return v
        """Validate charging state."""
        valid_states = {'charging', 'suspended', 'completed', 'error'}
        if v not in valid_states:
            raise ValueError(f'Invalid charging state. Must be one of: {valid_states}')
