from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from datetime import datetime
from decimal import Decimal

@dataclass
class ChargingPeriod:
    started_at: datetime
    stopped_at: datetime
    state: str
    duration_in_seconds: int
    amount: Decimal
    grace_time_end: Optional[datetime]
    free_energy_wh: int
    max_allowance_wh: int

@dataclass
class Currency:
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

@dataclass
class SmartCharging:
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

@dataclass
class PaymentDetails:
    card_network: str
    card_type: str
    method_id: str
    method_type: str
    name: str
    type: str

@dataclass
class ChargingSession:
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
        """Create a ChargingSession instance from API response data."""
        def parse_datetime(dt_str: str) -> datetime:
            return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))

        def parse_charging_period(period_data: Dict[str, Any]) -> ChargingPeriod:
            return ChargingPeriod(
                started_at=parse_datetime(period_data['startedAt']),
                stopped_at=parse_datetime(period_data['stoppedAt']) if period_data.get('stoppedAt') else None,
                state=period_data['state'],
                duration_in_seconds=period_data.get('durationInSeconds'),
                amount=Decimal(str(period_data['amount'])),
                grace_time_end=parse_datetime(period_data['graceTimeEnd']) if period_data.get('graceTimeEnd') else None,
                free_energy_wh=period_data['freeEnergyWh'],
                max_allowance_wh=period_data['maxAllowanceWh']
            )

        def parse_currency(currency_data: Dict[str, Any]) -> Currency:
            return Currency(
                id=currency_data['id'],
                name=currency_data['name'],
                symbol=currency_data['symbol'],
                sign=currency_data['sign'],
                code=currency_data['code'],
                formatter=currency_data['formatter'],
                unit_price_formatter=currency_data['unitPriceFormatter'],
                updated_at=parse_datetime(currency_data['updatedAt']),
                minor_unit_decimal=currency_data['minorUnitDecimal'],
                has_prefix=currency_data['hasPrefix'],
                has_suffix=currency_data['hasSuffix'],
                prefix=currency_data['prefix'],
                suffix=currency_data['suffix']
            )

        def parse_smart_charging(smart_data: Dict[str, Any]) -> SmartCharging:
            return SmartCharging(
                enabled=smart_data['enabled'],
                mode=smart_data['mode'],
                target_charge=smart_data['target_charge'],
                use_solar=smart_data['use_solar'],
                use_all_generated_solar=smart_data.get('use_all_generated_solar'),
                max_current_from_grid_a=smart_data.get('max_current_from_grid_a'),
                solar_stable_time_sec=smart_data.get('solar_stable_time_sec'),
                dynamic_rates_integration_id=smart_data.get('dynamic_rates_integration_id'),
                start_time=smart_data['start_time'],
                end_time=smart_data['end_time'],
                weekdays=smart_data.get('weekdays')
            )

        def parse_payment_details(payment_data: Optional[Dict[str, Any]]) -> Optional[PaymentDetails]:
            if not payment_data:
                return None
            return PaymentDetails(
                card_network=payment_data.get('cardNetwork'),
                card_type=payment_data.get('card_type'),
                method_id=payment_data.get('methodId'),
                method_type=payment_data.get('methodType'),
                name=payment_data.get('name'),
                type=payment_data.get('type')
            )

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
            payment_details=parse_payment_details(data.get('paymentDetails')),
            is_extending=data['isExtending'],
            is_extended=data['isExtended'],
            is_optimized=data['isOptimized'],
            stop_reason=data.get('stopReason'),
            charging_state=data['chargingState'],
            is_session_timed_out=data['isSessionTimedOut'],
            stopped_at=parse_datetime(data['stoppedAt']) if data.get('stoppedAt') else None,
            is_personal=data['isPersonal'],
            reimbursement_eligibility=data['reimbursementEligibility'],
            can_toggle_reimbursement_eligibility=data['canToggleReimbursementEligibility'],
            has_third_party_electricity_cost_integration_enabled=data.get('hasThirdPartyElectricityCostIntegrationEnabled'),
            non_billable_energy=data['nonBillableEnergy'],
            currency_id=data['currencyId'],
            currency=parse_currency(data['currency']),
            smart_charging=parse_smart_charging(data['smartCharging']),
            electricity_cost=Decimal(str(data['electricityCost'])),
            electricity_cost_currency_id=data['electricityCostCurrencyId'],
            power_avg=float(data['powerAvg']),
            is_using_charging_allowance=data['isUsingChargingAllowance'],
            free_energy_wh=data['freeEnergyWh'],
            sca_pending_transaction=data.get('scaPendingTransaction'),
            idle_period=data['idlePeriod'],
            is_remote_stop_enabled=data['isRemoteStopEnabled'],
            is_balance_payment_pending=data['isBalancePaymentPending'],
            charging_periods=[parse_charging_period(p) for p in data.get('chargingPeriods', [])],
            last_period=parse_charging_period(data['lastPeriod']),
            idle_fee_eligible=data['idleFeeEligible'],
            tax_name=data.get('taxName'),
            smart_charging_schedule=data.get('smartChargingSchedule'),
            power_stats=data.get('powerStats')
        )

@dataclass
class ChargingHistoryEntry:
    session: ChargingSession
    note: str
    type: str
    address: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChargingHistoryEntry':
        """Create a ChargingHistoryEntry instance from API response data."""
        def parse_datetime(dt_str: str) -> datetime:
            return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))

        def parse_charging_period(period_data: Dict[str, Any]) -> ChargingPeriod:
            return ChargingPeriod(
                started_at=parse_datetime(period_data['startedAt']),
                stopped_at=parse_datetime(period_data['stoppedAt']),
                state=period_data['state'],
                duration_in_seconds=period_data['durationInSeconds'],
                amount=Decimal(str(period_data['amount'])),
                grace_time_end=parse_datetime(period_data['graceTimeEnd']) if period_data['graceTimeEnd'] else None,
                free_energy_wh=period_data['freeEnergyWh'],
                max_allowance_wh=period_data['maxAllowanceWh']
            )

        def parse_currency(currency_data: Dict[str, Any]) -> Currency:
            return Currency(
                id=currency_data['id'],
                name=currency_data['name'],
                symbol=currency_data['symbol'],
                sign=currency_data['sign'],
                code=currency_data['code'],
                formatter=currency_data['formatter'],
                unit_price_formatter=currency_data['unitPriceFormatter'],
                updated_at=parse_datetime(currency_data['updatedAt']),
                minor_unit_decimal=currency_data['minorUnitDecimal'],
                has_prefix=currency_data['hasPrefix'],
                has_suffix=currency_data['hasSuffix'],
                prefix=currency_data['prefix'],
                suffix=currency_data['suffix']
            )

        def parse_smart_charging(smart_data: Dict[str, Any]) -> SmartCharging:
            return SmartCharging(
                enabled=smart_data['enabled'],
                mode=smart_data['mode'],
                target_charge=smart_data['target_charge'],
                use_solar=smart_data['use_solar'],
                use_all_generated_solar=smart_data['use_all_generated_solar'],
                max_current_from_grid_a=smart_data['max_current_from_grid_a'],
                solar_stable_time_sec=smart_data['solar_stable_time_sec'],
                dynamic_rates_integration_id=smart_data['dynamic_rates_integration_id'],
                start_time=smart_data['start_time'],
                end_time=smart_data['end_time'],
                weekdays=smart_data['weekdays']
            )

        def parse_payment_details(payment_data: Dict[str, Any]) -> PaymentDetails:
            return PaymentDetails(
                card_network=payment_data['cardNetwork'],
                card_type=payment_data['card_type'],
                method_id=payment_data['methodId'],
                method_type=payment_data['methodType'],
                name=payment_data['name'],
                type=payment_data['type']
            )

        def parse_session(session_data: Dict[str, Any]) -> ChargingSession:
            return ChargingSession.from_dict(session_data)

        return cls(
            session=parse_session(data['session']),
            note=data['note'],
            type=data['type'],
            address=data['address']
        )

@dataclass
class ChargingSessionResponse:
    """Response model for a single charging session."""
    session: ChargingSession

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChargingSessionResponse':
        """Create a ChargingSessionResponse instance from API response data."""
        return cls(
            session=ChargingSession.from_dict(data['session'])
        )

@dataclass
class ChargingHistory:
    """Top-level class for charging history data."""
    session_history: List[ChargingHistoryEntry]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChargingHistory':
        """Create a ChargingHistory instance from API response data."""
        def parse_datetime(dt_str: str) -> datetime:
            return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))

        def parse_charging_period(period_data: Dict[str, Any]) -> ChargingPeriod:
            return ChargingPeriod(
                started_at=parse_datetime(period_data['startedAt']),
                stopped_at=parse_datetime(period_data['stoppedAt']),
                state=period_data['state'],
                duration_in_seconds=period_data['durationInSeconds'],
                amount=Decimal(str(period_data['amount'])),
                grace_time_end=parse_datetime(period_data['graceTimeEnd']) if period_data['graceTimeEnd'] else None,
                free_energy_wh=period_data['freeEnergyWh'],
                max_allowance_wh=period_data['maxAllowanceWh']
            )

        def parse_currency(currency_data: Dict[str, Any]) -> Currency:
            return Currency(
                id=currency_data['id'],
                name=currency_data['name'],
                symbol=currency_data['symbol'],
                sign=currency_data['sign'],
                code=currency_data['code'],
                formatter=currency_data['formatter'],
                unit_price_formatter=currency_data['unitPriceFormatter'],
                updated_at=parse_datetime(currency_data['updatedAt']),
                minor_unit_decimal=currency_data['minorUnitDecimal'],
                has_prefix=currency_data['hasPrefix'],
                has_suffix=currency_data['hasSuffix'],
                prefix=currency_data['prefix'],
                suffix=currency_data['suffix']
            )

        def parse_smart_charging(smart_data: Dict[str, Any]) -> SmartCharging:
            return SmartCharging(
                enabled=smart_data['enabled'],
                mode=smart_data['mode'],
                target_charge=smart_data['target_charge'],
                use_solar=smart_data['use_solar'],
                use_all_generated_solar=smart_data['use_all_generated_solar'],
                max_current_from_grid_a=smart_data['max_current_from_grid_a'],
                solar_stable_time_sec=smart_data['solar_stable_time_sec'],
                dynamic_rates_integration_id=smart_data['dynamic_rates_integration_id'],
                start_time=smart_data['start_time'],
                end_time=smart_data['end_time'],
                weekdays=smart_data['weekdays']
            )

        def parse_payment_details(payment_data: Dict[str, Any]) -> PaymentDetails:
            return PaymentDetails(
                card_network=payment_data['cardNetwork'],
                card_type=payment_data['card_type'],
                method_id=payment_data['methodId'],
                method_type=payment_data['methodType'],
                name=payment_data['name'],
                type=payment_data['type']
            )

        def parse_session(session_data: Dict[str, Any]) -> ChargingSession:
            return ChargingSession.from_dict(session_data)

        def parse_entry(entry_data: Dict[str, Any]) -> ChargingHistoryEntry:
            return ChargingHistoryEntry(
                session=parse_session(entry_data['session']),
                note=entry_data['note'],
                type=entry_data['type'],
                address=entry_data['address']
            )

        return cls(
            session_history=[parse_entry(entry) for entry in data['session_history']]
        )

    def get_session(self, session_id: str) -> Optional[ChargingHistoryEntry]:
        """Get a specific charging session by ID."""
        for entry in self.session_history:
            if entry.session.id == session_id:
                return entry
        return None

@dataclass
class Connector:
    """Model for a charging connector."""
    name: str
    icon: str
    format: str
    status: str

@dataclass
class SchedulingIntervals:
    """Model for charge point scheduling intervals."""
    off_peak_is_set: bool
    solar_is_set: bool
    off_peak_start_time: str
    off_peak_end_time: str
    solar_start_time: Optional[str]
    solar_end_time: Optional[str]
    solar_max_power: Optional[float]

@dataclass
class EVSE:
    """Model for Electric Vehicle Supply Equipment."""
    id: str
    max_power: int
    identifier: str
    current_type: str
    status: str
    connectors: List[Connector]
    session: Optional[ChargingSession]
    tariff_id: int
    tariff: Dict[str, Any]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EVSE':
        """Create an EVSE instance from API response data."""
        return cls(
            id=data['id'],
            max_power=data['maxPower'],
            identifier=data['identifier'],
            current_type=data['currentType'],
            status=data['status'],
            connectors=[Connector(**conn) for conn in data['connectors']],
            session=ChargingSession.from_dict(data['session']) if data.get('session') else None,
            tariff_id=data['tariffId'],
            tariff=data['tariff']
        )

@dataclass
class ChargePoint:
    """Model for a charge point."""
    id: str
    name: str
    location: Dict[str, Optional[float]]
    location_id: Optional[str]
    postcode: Optional[str]
    photo: str
    plug_and_charge: bool
    smart_charging_enabled: bool
    allowed_min_current_a: int
    allowed_max_current_a: int
    allowed_solar_min_power_kw: float
    allowed_max_power_kw: float
    max_current_a: int
    status: str
    is_rebooting: bool
    scheduling_intervals: SchedulingIntervals
    evses: List[EVSE]
    track_electricity_cost: Optional[bool]
    smart_charging: SmartCharging
    is_electricity_cost_tracking_available: bool
    requires_authorization: bool
    enable_keep_awake: bool
    min_charging_current: int
    connector_lock: bool
    is_connector_lock_supported: bool
    is_light_intensity_supported: bool
    light_intensity: int
    allowed_smart_charging_modes: List[str]
    has_electricity_tax_reimbursement: bool
    electricity_cost_tax_name: str
    electricity_cost_tax_percent: float
    last_month_energy_kwh: str
    last_month_electricity_cost: str
    electricity_cost_currency_id: int
    has_third_party_electricity_cost_integration_enabled: bool
    user_manual_url: Optional[str]
    is_tamper_detection_notifications: bool
    subscription: Dict[str, Any]
    randomised_delay_enabled: bool
    firmware_version: str
    is_firmware_updates_supported: bool
    latest_firmware_update_execution: Optional[str]
    is_firmware_updating: bool

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChargePoint':
        """Create a ChargePoint instance from API response data."""
        return cls(
            id=data['id'],
            name=data['name'],
            location=data['location'],
            location_id=data['location_id'],
            postcode=data['postcode'],
            photo=data['photo'],
            plug_and_charge=data['plug_and_charge'],
            smart_charging_enabled=data['smart_charging_enabled'],
            allowed_min_current_a=data['allowed_min_current_a'],
            allowed_max_current_a=data['allowed_max_current_a'],
            allowed_solar_min_power_kw=data['allowed_solar_min_power_kw'],
            allowed_max_power_kw=float(data['allowed_max_power_kw']),
            max_current_a=data['max_current_a'],
            status=data['status'],
            is_rebooting=data['is_rebooting'],
            scheduling_intervals=SchedulingIntervals(**data['scheduling_intervals']),
            evses=[EVSE.from_dict(evse) for evse in data['evses']],
            track_electricity_cost=data.get('track_electricity_cost'),
            smart_charging=SmartCharging(**data['smart_charging']),
            is_electricity_cost_tracking_available=data['isElectricityCostTrackingAvailable'],
            requires_authorization=data['requires_authorization'],
            enable_keep_awake=data['enable_keep_awake'],
            min_charging_current=data['min_charging_current'],
            connector_lock=data['connector_lock'],
            is_connector_lock_supported=data['is_connector_lock_supported'],
            is_light_intensity_supported=data['is_light_intensity_supported'],
            light_intensity=data['light_intensity'],
            allowed_smart_charging_modes=data['allowed_smart_charging_modes'],
            has_electricity_tax_reimbursement=data['has_electricity_tax_reimbursement'],
            electricity_cost_tax_name=data['electricity_cost_tax_name'],
            electricity_cost_tax_percent=data['electricity_cost_tax_percent'],
            last_month_energy_kwh=data['last_month_energy_kwh'],
            last_month_electricity_cost=data['last_month_electricity_cost'],
            electricity_cost_currency_id=data['electricity_cost_currency_id'],
            has_third_party_electricity_cost_integration_enabled=data['has_third_party_electricity_cost_integration_enabled'],
            user_manual_url=data.get('user_manual_url'),
            is_tamper_detection_notifications=data['isTamperDetectionNotifications'],
            subscription=data['subscription'],
            randomised_delay_enabled=data['randomised_delay_enabled'],
            firmware_version=data['firmware_version'],
            is_firmware_updates_supported=data['isFirmwareUpdatesSupported'],
            latest_firmware_update_execution=data.get('latestFirmwareUpdateExecution'),
            is_firmware_updating=data['isFirmwareUpdating']
        )

@dataclass
class ChargePointsResponse:
    """Response model for charge points data."""
    data: List[ChargePoint]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChargePointsResponse':
        """Create a ChargePointsResponse instance from API response data."""
        return cls(
            data=[ChargePoint.from_dict(point) for point in data['data']]
        )

@dataclass
class StartChargingResponse:
    """Response model for start charging request."""
    success: bool
    message: str
    session_id: Optional[str] = None
    evse_id: Optional[str] = None
    max_power: Optional[int] = None
    started_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StartChargingResponse':
        """Create a StartChargingResponse instance from API response data."""
        def parse_datetime(dt_str: str) -> datetime:
            return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))

        return cls(
            success=data.get('success', False),
            message=data.get('message', ''),
            session_id=data.get('sessionId'),
            evse_id=data.get('evseId'),
            max_power=data.get('maxPower'),
            started_at=parse_datetime(data['startedAt']) if data.get('startedAt') else None
        ) 