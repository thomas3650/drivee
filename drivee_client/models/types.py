"""Shared types and enums used across the Drivee integration."""

from enum import Enum
from typing import Literal

class ChargePointStatus(str, Enum):
    """Valid charge point operational statuses."""
    AVAILABLE = "Available"
    PREPARING = "Preparing"
    CHARGING = "Charging"
    FINISHING = "Finishing"
    RESERVED = "Reserved"
    UNAVAILABLE = "Unavailable"
    FAULTED = "Faulted"

class EVSEStatus(str, Enum):
    """Valid EVSE operational statuses."""
    AVAILABLE = "Available"
    OCCUPIED = "Occupied"
    RESERVED = "Reserved"
    UNAVAILABLE = "Unavailable"
    FAULTED = "Faulted"
    CHARGING = "charging"
    SUSPENDED = "suspended"
    PENDING = "pending"
    READY = "ready"
    PREPARING = "preparing"

class ConnectorStatus(str, Enum):
    """Valid connector operational statuses."""
    AVAILABLE = "Available"
    OCCUPIED = "Occupied"
    RESERVED = "Reserved"
    UNAVAILABLE = "Unavailable"
    FAULTED = "Faulted"
    ACTIVE = "active"

class ConnectorType(str, Enum):
    """Valid connector types."""
    TYPE1 = "Type1"
    TYPE2 = "Type2"
    CCS = "CCS"
    CHADEMO = "CHAdeMO"
    TESLA = "Tesla"
    NACS = "NACS"

class ConnectorFormat(str, Enum):
    """Valid connector physical formats."""
    SOCKET = "socket"
    CABLE = "cable"

class ChargingSessionStatus(str, Enum):
    """Valid charging session statuses."""
    ACTIVE = "Active"
    PAUSED = "Paused"
    COMPLETED = "Completed"
    STOPPED = "Stopped"
    FAULTED = "Faulted"

# Type aliases for better type safety
PowerKW = float  # Power in kilowatts
CurrentA = float  # Current in amperes
Status = Literal[
    ChargePointStatus,
    EVSEStatus,
    ConnectorStatus,
    ChargingSessionStatus
]

# Charging state literals
ChargingStateType = Literal["charging", "idle", "error", "disconnected"]
PaymentStatusType = Literal["pending", "completed", "failed", "cancelled"]
PeriodStateType = Literal["charging", "idle", "grace"]
