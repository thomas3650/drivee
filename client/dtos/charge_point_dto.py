"""DTOs for charge point data transfer."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from client.dtos.connector_dto import ConnectorDTO
from client.dtos.scheduling_intervals_dto import SchedulingIntervalDTO

from .base_dto import BaseDTO
from .dto_protocol import ChargePointDTOProtocol  # type: ignore # Used for type checking
from .evse_dto import EVSEDTO

@dataclass
class LocationDTO(BaseDTO):
    """DTO representing location information for a charge point."""
    id: str  # Required from BaseDTO
    latitude: Optional[float] = None
    longitude: Optional[float] = None

@dataclass
class ChargePointDTO(BaseDTO):  # type: ignore[type-arg] # Implements ChargePointDTOProtocol
    """DTO representing a charge point in the system that implements ChargePointDTOProtocol."""
    # Required fields from BaseDTO
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Fields matching the actual API response from charge-points.json
    name: str = ""
    location_id: Optional[str] = None  # snake_case in API
    last_updated: datetime = field(default_factory=datetime.now)
    status: str = ""
    photo: Optional[str] = None
    plug_and_charge: bool = False  # snake_case in API
    smart_charging_enabled: bool = False  # snake_case in API
    allowed_min_current_a: int = 0  # snake_case in API
    allowed_max_current_a: int = 0  # snake_case in API
    allowed_max_power_kw: str = "0"  # snake_case in API
    max_current_a: int = 0  # snake_case in API
    is_rebooting: bool = False  # snake_case in API
    evses: List[EVSEDTO] = field(default_factory=lambda: list())
    
    # Additional fields from API response
    postcode: Optional[str] = None
    allowed_solar_min_power_kw: Optional[float] = None  # snake_case in API
    location: Optional[LocationDTO] = None
    scheduling_intervals: List[SchedulingIntervalDTO] = field(default_factory=lambda: list())

    track_electricity_cost: Optional[bool] = None  # snake_case in API
    smart_charging: Optional[Dict[str, Any]] = None  # snake_case in API - keeping as dict for now
    
    # Mixed case fields that appear in camelCase in API
    isElectricityCostTrackingAvailable: bool = False  # camelCase in API
    requires_authorization: bool = True  # snake_case in API
    enable_keep_awake: bool = False  # snake_case in API
    min_charging_current: int = 6  # snake_case in API
    connector_lock: bool = False  # snake_case in API
    is_connector_lock_supported: bool = True  # snake_case in API
    is_light_intensity_supported: bool = True  # snake_case in API
    light_intensity: int = 100  # snake_case in API
    allowed_smart_charging_modes: List[str] = field(default_factory=lambda: [])  # snake_case in API
    has_electricity_tax_reimbursement: bool = False  # snake_case in API
    electricity_cost_tax_name: Optional[str] = None  # snake_case in API
    electricity_cost_tax_percent: Optional[int] = None  # snake_case in API
    last_month_energy_kwh: Optional[str] = None  # snake_case in API
    last_month_electricity_cost: Optional[str] = None  # snake_case in API
    electricity_cost_currency_id: Optional[int] = None  # snake_case in API
    has_third_party_electricity_cost_integration_enabled: bool = False  # snake_case in API
    user_manual_url: Optional[str] = None  # snake_case in API
    isTamperDetectionNotifications: bool = False  # camelCase in API
    subscription: Optional[Dict[str, Any]] = None  # snake_case in API - keeping as dict for now
    randomised_delay_enabled: bool = False  # snake_case in API
    firmware_version: Optional[str] = None  # snake_case in API
    disable_automatic_firmware_updates: bool = False  # snake_case in API
    isFirmwareUpdatesSupported: bool = False  # camelCase in API
    latestFirmwareUpdateExecution: Optional[str] = None  # camelCase in API
    isFirmwareUpdating: bool = False  # camelCase in API
    isOwner: Optional[bool] = False  # camelCase in API
    ownerName: Optional[str] = None  # camelCase in API
    is_max_current_supported: Optional[bool] = None  # camelCase in API
    operatorCountry: Optional[str] = None  # camelCase in API
    connectors: List[ConnectorDTO] = field(default_factory=lambda: [])  # snake_case in API
