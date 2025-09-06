"""Drivee client package."""

__version__ = "0.1.0"

from .drivee_client import DriveeClient
from .errors import (
    DriveeError,
    AuthenticationError,
    APIError,
    SessionError,
    ModelError,
    BusinessRuleError,
    ValidationError,
    NetworkError,
    TimeoutError,
    RateLimitError,
    ConfigurationError,
    ChargingError,
    ChargingNotAvailableError,
    ChargingSessionNotFoundError,
    ChargingAlreadyActiveError,
    ChargePointError,
    ChargePointNotFoundError,
    MultipleChargePointsError,
    ConnectorError,
    ConnectorNotAvailableError,
    ConnectorInUseError,
)
from .models import ChargePoint
from .models.charging_history import ChargingHistory
from .models.charging_response import ChargingResponseModel
from .models.charging_session import ChargingSession
from .models.connector import Connector
from .models.currency import Currency
from .models.evse import EVSE
from .models.power_stats import PowerStatsBaseModel

__all__ = [
    "DriveeClient",
    # Errors
    "DriveeError",
    "AuthenticationError",
    "APIError",
    "SessionError",
    "ModelError",
    "BusinessRuleError",
    "ValidationError",
    "NetworkError",
    "TimeoutError",
    "RateLimitError",
    "ConfigurationError",
    "ChargingError",
    "ChargingNotAvailableError",
    "ChargingSessionNotFoundError",
    "ChargingAlreadyActiveError",
    "ChargePointError",
    "ChargePointNotFoundError",
    "MultipleChargePointsError",
    "ConnectorError",
    "ConnectorNotAvailableError",
    "ConnectorInUseError",
    # Models
    "ChargePoint",
    "ChargingHistory",
    "ChargingResponseModel",
    "ChargingSession",
    "Connector",
    "Currency",
    "EVSE",
    "PowerStatsBaseModel",
]
