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
    started_at: datetime = Field(alias='startedAt')
    duration: int = Field(ge=0)
    total_duration: int = Field(alias='totalDuration', ge=0)
    energy: int = Field(ge=0)  # Energy in Wh
    power: int = Field(ge=0)  # Power in W
    location_id: Optional[str] = Field(alias='locationId', default=None)
    evse_id: str = Field(alias='evseId')
    evse_status: str = Field(alias='evseStatus')
    payment_method_id: str = Field(alias='paymentMethodId')
    payment_method_type: str = Field(alias='paymentMethodType')
    amount: Decimal = Field(ge=0)
    total_amount: Decimal = Field(alias='totalAmount', ge=0)
    amount_due: Decimal = Field(alias='amountDue', ge=0)
    status: str
    summary_seen: bool = Field(alias='summarySeen')
    payment_status: str = Field(alias='paymentStatus')
    payment_details: Optional[PaymentDetails] = Field(alias='paymentDetails', default=None)
    is_extending: bool = Field(alias='isExtending')
    is_extended: bool = Field(alias='isExtended')
    is_optimized: bool = Field(alias='isOptimized')
    stop_reason: Optional[str] = Field(alias='stopReason', default=None)
    charging_state: str = Field(alias='chargingState')
    is_session_timed_out: bool = Field(alias='isSessionTimedOut')
    stopped_at: Optional[datetime] = Field(alias='stoppedAt', default=None)
    is_personal: bool = Field(alias='isPersonal')
    reimbursement_eligibility: bool = Field(alias='reimbursementEligibility')
    can_toggle_reimbursement_eligibility: bool = Field(alias='canToggleReimbursementEligibility')
    has_third_party_electricity_cost_integration_enabled: Optional[bool] = Field(
        alias='hasThirdPartyElectricityCostIntegrationEnabled', 
        default=None
    )
    non_billable_energy: int = Field(alias='nonBillableEnergy', ge=0)
    currency_id: int = Field(alias='currencyId')
    currency: Currency
    smart_charging: SmartCharging = Field(alias='smartCharging')
    electricity_cost: Decimal = Field(alias='electricityCost', ge=0)
    electricity_cost_currency_id: int = Field(alias='electricityCostCurrencyId')
    power_avg: float = Field(alias='powerAvg', ge=0)
    power_stats: Optional[Dict[str, Any]] = Field(alias='powerStats', default=None)
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
