"""DTO for charging session data transfer."""
from __future__ import annotations
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional, Any

from pydantic import Field, field_validator

from .base_dto import BaseDTO
from .payment_details_dto import PaymentDetailsDTO
from .currency_dto import CurrencyDTO
from .smart_charging_dto import SmartChargingDTO
from .charging_period_dto import ChargingPeriodDTO

from ..models.types import ChargingStateType, PaymentStatusType

class ChargingSessionDTO(BaseDTO):
    """DTO representing a charging session in the system.
    
    This DTO contains all data related to a charging session, including:
    - Session timing and duration
    - Energy and power metrics
    - Payment and billing information
    - Status and state information
    - Associated equipment details
    """
    
    # Core session identifiers and metadata
    id: str = Field(description="Unique identifier for the charging session")
    evse_id: str = Field(alias='evseId', description="ID of the EVSE used")
    location_id: Optional[str] = Field(
        alias='locationId', 
        default=None,
        description="ID of the charging location"
    )
    
    # Timing information
    started_at: datetime = Field(
        alias='startedAt',
        description="When the session started"
    )
    
    def model_dump(self, **kwargs: Any) -> Dict[str, Any]:
        """Dump the model to a dictionary."""
        return super().model_dump(**kwargs)
    stopped_at: Optional[datetime] = Field(
        alias='stoppedAt',
        default=None,
        description="When the session ended"
    )
    duration: int = Field(ge=0, description="Current duration in seconds")
    total_duration: int = Field(
        alias='totalDuration',
        ge=0,
        description="Total duration including idle time"
    )
    idle_period: int = Field(
        ge=0,
        description="Duration of idle time in seconds"
    )
    
    # Energy and power metrics
    energy: int = Field(ge=0, description="Energy delivered in Wh")
    power: int = Field(ge=0, description="Current power in W")
    power_avg: float = Field(
        alias='powerAvg',
        ge=0,
        description="Average power during session"
    )
    power_stats: Optional[Dict[str, Any]] = Field(
        alias='powerStats',
        default=None,
        description="Detailed power statistics"
    )
    free_energy_wh: int = Field(
        ge=0,
        description="Amount of free energy delivered"
    )
    non_billable_energy: int = Field(
        alias='nonBillableEnergy',
        ge=0,
        description="Energy not subject to billing"
    )
    
    # Payment and billing
    payment_method_id: str = Field(
        alias='paymentMethodId',
        description="ID of payment method used"
    )
    payment_method_type: str = Field(
        alias='paymentMethodType',
        description="Type of payment method"
    )
    payment_status: PaymentStatusType = Field(
        alias='paymentStatus',
        description="Current payment status"
    )
    payment_details: Optional[PaymentDetailsDTO] = Field(
        alias='paymentDetails',
        default=None,
        description="Detailed payment information"
    )
    amount: Decimal = Field(ge=0, description="Current amount charged")
    total_amount: Decimal = Field(
        alias='totalAmount',
        ge=0,
        description="Total amount including fees"
    )
    amount_due: Decimal = Field(
        alias='amountDue',
        ge=0,
        description="Amount still to be paid"
    )
    currency_id: int = Field(
        alias='currencyId',
        description="ID of billing currency"
    )
    currency: CurrencyDTO = Field(description="Currency details")
    
    # Status and state
    status: str = Field(description="Overall session status")
    evse_status: str = Field(
        alias='evseStatus',
        description="Current EVSE status"
    )
    charging_state: ChargingStateType = Field(
        alias='chargingState',
        description="Current charging state"
    )
    is_session_timed_out: bool = Field(
        alias='isSessionTimedOut',
        description="Whether session has timed out"
    )
    stop_reason: Optional[str] = Field(
        alias='stopReason',
        default=None,
        description="Reason for session stop"
    )
    
    # Smart charging
    smart_charging: SmartChargingDTO = Field(
        alias='smartCharging',
        description="Smart charging configuration"
    )
    is_optimized: bool = Field(
        alias='isOptimized',
        description="Whether charging is optimized"
    )
    smart_charging_schedule: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Smart charging schedule"
    )
    
    # Session control
    is_extending: bool = Field(
        alias='isExtending',
        description="Whether session is being extended"
    )
    is_extended: bool = Field(
        alias='isExtended',
        description="Whether session was extended"
    )
    is_remote_stop_enabled: bool = Field(
        description="Whether remote stop is enabled"
    )
    
    # Charging periods
    charging_periods: Optional[List[ChargingPeriodDTO]] = Field(
        default=None,
        description="List of charging periods"
    )
    last_period: Optional[ChargingPeriodDTO] = Field(
        default=None,
        description="Most recent charging period"
    )
    
    # Billing and reimbursement
    is_personal: bool = Field(
        alias='isPersonal',
        description="Whether session is personal"
    )
    reimbursement_eligibility: bool = Field(
        alias='reimbursementEligibility',
        description="Whether eligible for reimbursement"
    )
    can_toggle_reimbursement_eligibility: bool = Field(
        alias='canToggleReimbursementEligibility',
        description="Whether reimbursement can be toggled"
    )
    has_third_party_electricity_cost_integration_enabled: Optional[bool] = Field(
        alias='hasThirdPartyElectricityCostIntegrationEnabled',
        default=None,
        description="Whether third party cost integration is enabled"
    )
    electricity_cost: Decimal = Field(
        alias='electricityCost',
        ge=0,
        description="Electricity cost amount"
    )
    electricity_cost_currency_id: int = Field(
        alias='electricityCostCurrencyId',
        description="Currency ID for electricity cost"
    )
    is_using_charging_allowance: bool = Field(
        description="Whether using charging allowance"
    )
    is_balance_payment_pending: bool = Field(
        description="Whether balance payment is pending"
    )
    idle_fee_eligible: bool = Field(
        description="Whether idle fees apply"
    )
    
    # Additional metadata
    summary_seen: bool = Field(
        alias='summarySeen',
        description="Whether session summary was viewed"
    )
    sca_pending_transaction: Optional[Any] = Field(
        default=None,
        description="Pending SCA transaction details"
    )
    tax_name: Optional[str] = Field(
        default=None,
        description="Name of applied tax"
    )

    @field_validator('charging_state')
    @classmethod
    def validate_charging_state(cls, v: str) -> ChargingStateType:
        """Validate charging state value.
        
        Args:
            v: The charging state value to validate
            
        Returns:
            ChargingStateType: The validated charging state
            
        Raises:
            ValueError: If the state is not one of the allowed values
        """
        valid_states = {"charging", "idle", "error", "disconnected"}
        if v not in valid_states:
            raise ValueError(
                f"Invalid charging state '{v}'. Must be one of: {', '.join(sorted(valid_states))}"
            )
        return v  # type: ignore # Validated against literal set above

    @field_validator('charging_periods')
    @classmethod
    def validate_charging_periods(cls, v: List[Any]) -> List[ChargingPeriodDTO]:
        """Validate charging periods list.
        
        Args:
            v: List of charging periods to validate
            
        Returns:
            List[ChargingPeriodDTO]: The validated charging periods list
            
        Raises:
            ValueError: If any period is not a ChargingPeriodDTO
        """
        # List type is enforced by Pydantic
        return [p if isinstance(p, ChargingPeriodDTO) else ChargingPeriodDTO(**p) for p in v]

    @field_validator('last_period')
    @classmethod
    def validate_last_period(cls, v: Optional[Any]) -> Optional[ChargingPeriodDTO]:
        """Validate last charging period.
        
        Args:
            v: The last charging period to validate
            
        Returns:
            Optional[ChargingPeriodDTO]: The validated last period
            
        Raises:
            ValueError: If the period is not a ChargingPeriodDTO
        """
        if v is None:
            return None
        if isinstance(v, ChargingPeriodDTO):
            return v
        return ChargingPeriodDTO(**v)
