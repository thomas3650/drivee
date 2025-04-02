"""Models for the Drivee API responses."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from datetime import datetime
from decimal import Decimal

def parse_datetime(dt_str: Optional[str]) -> Optional[datetime]:
    """Parse datetime string to datetime object."""
    if not dt_str:
        return None
    return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))

@dataclass
class ChargingPeriod:
    """Model for a charging period."""
    started_at: datetime
    stopped_at: Optional[datetime]
    state: str
    duration_in_seconds: int
    amount: Decimal
    grace_time_end: Optional[datetime]
    free_energy_wh: int
    max_allowance_wh: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChargingPeriod':
        """Create a ChargingPeriod instance from a dictionary."""
        return cls(
            started_at=parse_datetime(data['startedAt']),
            stopped_at=parse_datetime(data.get('stoppedAt')),
            state=data['state'],
            duration_in_seconds=data['durationInSeconds'],
            amount=Decimal(str(data['amount'])),
            grace_time_end=parse_datetime(data.get('graceTimeEnd')),
            free_energy_wh=data['freeEnergyWh'],
            max_allowance_wh=data['maxAllowanceWh']
        )

@dataclass
class Currency:
    """Model for currency information."""
    id: int
    name: str
    symbol: str
    sign: str
    code: str
    formatter: str
    unit_price_formatter: str
    updated_at: datetime
    minor_unit_decimal: int
    has_prefix: bool
    has_suffix: bool
    prefix: Optional[str]
    suffix: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Currency':
        """Create a Currency instance from a dictionary."""
        return cls(
            id=data['id'],
            name=data['name'],
            symbol=data['symbol'],
            sign=data['sign'],
            code=data['code'],
            formatter=data['formatter'],
            unit_price_formatter=data['unitPriceFormatter'],
            updated_at=parse_datetime(data['updatedAt']),
            minor_unit_decimal=data['minorUnitDecimal'],
            has_prefix=data['hasPrefix'],
            has_suffix=data['hasSuffix'],
            prefix=data.get('prefix'),
            suffix=data['suffix']
        )

@dataclass
class SmartCharging:
    """Model for smart charging settings."""
    enabled: bool
    mode: str
    target_charge: Dict[str, str]
    use_solar: bool
    use_all_generated_solar: Optional[bool]
    max_current_from_grid_a: Optional[int]
    solar_stable_time_sec: Optional[int]
    dynamic_rates_integration_id: Optional[int]
    start_time: str
    end_time: str
    weekdays: Optional[List[str]]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SmartCharging':
        """Create a SmartCharging instance from a dictionary."""
        return cls(
            enabled=data['enabled'],
            mode=data['mode'],
            target_charge=data['target_charge'],
            use_solar=data['use_solar'],
            use_all_generated_solar=data.get('use_all_generated_solar'),
            max_current_from_grid_a=data.get('max_current_from_grid_a'),
            solar_stable_time_sec=data.get('solar_stable_time_sec'),
            dynamic_rates_integration_id=data.get('dynamic_rates_integration_id'),
            start_time=data['start_time'],
            end_time=data['end_time'],
            weekdays=data.get('weekdays')
        )

@dataclass
class PaymentDetails:
    """Model for payment details."""
    card_network: str
    card_type: str
    method_id: str
    method_type: str
    name: str
    type: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PaymentDetails':
        """Create a PaymentDetails instance from a dictionary."""
        return cls(
            card_network=data['cardNetwork'],
            card_type=data['card_type'],
            method_id=data['methodId'],
            method_type=data['methodType'],
            name=data['name'],
            type=data['type']
        )

@dataclass
class ChargingSession:
    """Model for a charging session."""
    id: str
    started_at: datetime
    duration: int
    total_duration: int
    energy: int
    power: int
    location_id: Optional[str]
    evse_id: str
    evse_status: str
    payment_method_id: str
    payment_method_type: str
    amount: Decimal
    total_amount: Decimal
    amount_due: Decimal
    status: str
    summary_seen: bool
    payment_status: str
    payment_details: Optional[PaymentDetails]
    is_extending: bool
    is_extended: bool
    is_optimized: bool
    stop_reason: Optional[str]
    charging_state: str
    is_session_timed_out: bool
    stopped_at: Optional[datetime]
    is_personal: bool
    reimbursement_eligibility: bool
    can_toggle_reimbursement_eligibility: bool
    has_third_party_electricity_cost_integration_enabled: Optional[bool]
    non_billable_energy: int
    currency_id: int
    currency: Currency
    smart_charging: SmartCharging
    electricity_cost: Decimal
    electricity_cost_currency_id: int
    power_avg: float
    is_using_charging_allowance: bool
    free_energy_wh: int
    sca_pending_transaction: Optional[Any]
    idle_period: int
    is_remote_stop_enabled: bool
    is_balance_payment_pending: bool
    charging_periods: List[ChargingPeriod]
    last_period: ChargingPeriod
    idle_fee_eligible: bool
    tax_name: Optional[str]
    smart_charging_schedule: Optional[List[Dict[str, Any]]]
    power_stats: Optional[Dict[str, Any]]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChargingSession':
        """Create a ChargingSession instance from a dictionary."""
        return cls(
            id=data['id'],
            started_at=parse_datetime(data['startedAt']),
            duration=data['duration'],
            total_duration=data['totalDuration'],
            energy=data['energy'],
            power=data['power'],
            location_id=data.get('locationId'),
            evse_id=data['evseId'],
            evse_status=data['evseStatus'],
            payment_method_id=data['paymentMethodId'],
            payment_method_type=data['paymentMethodType'],
            amount=Decimal(str(data['amount'])),
            total_amount=Decimal(str(data['totalAmount'])),
            amount_due=Decimal(str(data['amountDue'])),
            status=data['status'],
            summary_seen=data['summarySeen'],
            payment_status=data['paymentStatus'],
            payment_details=PaymentDetails.from_dict(data['paymentDetails']) if data.get('paymentDetails') else None,
            is_extending=data['isExtending'],
            is_extended=data['isExtended'],
            is_optimized=data['isOptimized'],
            stop_reason=data.get('stopReason'),
            charging_state=data['chargingState'],
            is_session_timed_out=data['isSessionTimedOut'],
            stopped_at=parse_datetime(data.get('stoppedAt')),
            is_personal=data['isPersonal'],
            reimbursement_eligibility=data['reimbursementEligibility'],
            can_toggle_reimbursement_eligibility=data['canToggleReimbursementEligibility'],
            has_third_party_electricity_cost_integration_enabled=data.get('hasThirdPartyElectricityCostIntegrationEnabled'),
            non_billable_energy=data['nonBillableEnergy'],
            currency_id=data['currencyId'],
            currency=Currency.from_dict(data['currency']),
            smart_charging=SmartCharging.from_dict(data['smartCharging']),
            electricity_cost=Decimal(str(data['electricityCost'])),
            electricity_cost_currency_id=data['electricityCostCurrencyId'],
            power_avg=float(data['powerAvg']),
            is_using_charging_allowance=data['isUsingChargingAllowance'],
            free_energy_wh=data['freeEnergyWh'],
            sca_pending_transaction=data.get('scaPendingTransaction'),
            idle_period=data['idlePeriod'],
            is_remote_stop_enabled=data['isRemoteStopEnabled'],
            is_balance_payment_pending=data['isBalancePaymentPending'],
            charging_periods=[ChargingPeriod.from_dict(p) for p in data.get('chargingPeriods', [])],
            last_period=ChargingPeriod.from_dict(data['lastPeriod']),
            idle_fee_eligible=data['idleFeeEligible'],
            tax_name=data.get('taxName'),
            smart_charging_schedule=data.get('smartChargingSchedule'),
            power_stats=data.get('powerStats')
        )

@dataclass
class Connector:
    """Model for a charging connector."""
    name: str
    status: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Connector':
        """Create a Connector instance from a dictionary."""
        return cls(
            name=data['name'],
            status=data['status']
        )

@dataclass
class SchedulingIntervals:
    """Model for charge point scheduling intervals."""
    off_peak_is_set: bool

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SchedulingIntervals':
        """Create a SchedulingIntervals instance from a dictionary."""
        return cls(
            off_peak_is_set=data.get('offPeakIsSet', False)
        )

@dataclass
class EVSE:
    """Model for Electric Vehicle Supply Equipment."""
    id: str
    status: str
    max_power: float
    current_type: str
    connectors: List[Connector]
    session: Optional[ChargingSession]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EVSE':
        """Create an EVSE instance from a dictionary."""
        return cls(
            id=data['id'],
            status=data['status'],
            max_power=data['maxPower'],
            current_type=data['currentType'],
            connectors=[Connector.from_dict(c) for c in data['connectors']],
            session=ChargingSession.from_dict(data['session']) if data.get('session') else None
        )

@dataclass
class ChargePoint:
    """Model for a charge point."""
    name: str
    status: str
    allowed_max_power_kw: float
    scheduling_intervals: SchedulingIntervals
    evse: EVSE

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChargePoint':
        """Create a ChargePoint instance from a dictionary."""
        # The API returns evses as a list, but we expect exactly one
        evses = data.get('evses', [])
        if not evses:
            raise ValueError("No EVSEs found in charge point data")
            
        evse = EVSE.from_dict(evses[0])
            
        return cls(
            name=data['name'],
            status=data['status'],
            allowed_max_power_kw=float(data.get('allowed_max_power_kw', data.get('allowedMaxPowerKw', 0))),
            scheduling_intervals=SchedulingIntervals.from_dict(data.get('scheduling_intervals', {})),
            evse=evse
        )

@dataclass
class StartChargingResponse:
    """Response model for start charging request."""
    success: bool
    message: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StartChargingResponse':
        """Create a StartChargingResponse instance from a dictionary."""
        return cls(
            success=data['success'],
            message=data['message']
        )

@dataclass
class EndChargingResponse:
    """Response model for end charging request."""
    session: ChargingSession

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EndChargingResponse':
        """Create an EndChargingResponse instance from a dictionary."""
        return cls(
            session=ChargingSession.from_dict(data['session'])
        )

@dataclass
class ChargingHistoryEntry:
    """Model for a charging history entry."""
    session: ChargingSession
    note: str
    type: str
    address: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChargingHistoryEntry':
        """Create a ChargingHistoryEntry instance from a dictionary."""
        return cls(
            session=ChargingSession.from_dict(data['session']),
            note=data['note'],
            type=data['type'],
            address=data['address']
        )

@dataclass
class ChargingHistory:
    """Model for charging history data."""
    session_history: List[ChargingHistoryEntry]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChargingHistory':
        """Create a ChargingHistory instance from a dictionary."""
        return cls(
            session_history=[ChargingHistoryEntry.from_dict(entry) for entry in data['session_history']]
        )

    def get_session(self, session_id: str) -> Optional[ChargingHistoryEntry]:
        """Get a specific charging session by ID."""
        for entry in self.session_history:
            if entry.session.id == session_id:
                return entry
        return None 