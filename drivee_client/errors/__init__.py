"""Error classes for the drivee_client package."""

from __future__ import annotations


class DriveeError(Exception):
    """Base exception for all Drivee client errors."""
    pass


class AuthenticationError(DriveeError):
    """Raised when authentication fails."""
    pass


class APIError(DriveeError):
    """Raised when the API returns an error."""
    
    def __init__(self, status: int, message: str) -> None:
        self.status = status
        super().__init__(f"API error {status}: {message}")


class SessionError(DriveeError):
    """Raised when there are session-related errors."""
    pass


class ModelError(DriveeError):
    """Base class for all model-related errors."""
    pass


class BusinessRuleError(ModelError):
    """Error raised when a business rule is violated."""
    pass


class ValidationError(ModelError):
    """Error raised when model validation fails."""
    pass


class NetworkError(DriveeError):
    """Raised when network-related errors occur."""
    pass


class TimeoutError(NetworkError):
    """Raised when a request times out."""
    pass


class RateLimitError(APIError):
    """Raised when API rate limits are exceeded."""
    
    def __init__(self, retry_after: int | None = None) -> None:
        self.retry_after = retry_after
        message = "Rate limit exceeded"
        if retry_after:
            message += f", retry after {retry_after} seconds"
        super().__init__(429, message)


class ConfigurationError(DriveeError):
    """Raised when there are configuration-related errors."""
    pass


class ChargingError(DriveeError):
    """Base class for charging-related errors."""
    pass


class ChargingNotAvailableError(ChargingError):
    """Raised when charging is not available (e.g., vehicle not connected)."""
    pass


class ChargingSessionNotFoundError(ChargingError):
    """Raised when a charging session is not found."""
    pass


class ChargingAlreadyActiveError(ChargingError):
    """Raised when trying to start charging but a session is already active."""
    pass


class ChargePointError(DriveeError):
    """Base class for charge point-related errors."""
    pass


class ChargePointNotFoundError(ChargePointError):
    """Raised when no charge points are available."""
    pass


class MultipleChargePointsError(ChargePointError):
    """Raised when multiple charge points are found but only one is expected."""
    pass


class ConnectorError(DriveeError):
    """Base class for connector-related errors."""
    pass


class ConnectorNotAvailableError(ConnectorError):
    """Raised when no connectors are available for charging."""
    pass


class ConnectorInUseError(ConnectorError):
    """Raised when trying to use a connector that is already in use."""
    pass
