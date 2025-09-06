"""
Models package containing business logic for the Drivee integration.

This package contains model classes that encapsulate DTOs and provide business logic.
Models should never expose DTOs directly to external code. Instead, they should provide
business-relevant properties and methods that operate on the underlying DTOs.
"""

from .base_model import BaseModel
from .charge_point import ChargePoint
from .connector import Connector
from .evse import EVSE

__all__ = [
    "BaseModel",
    "ChargePoint",
    "Connector",
    "EVSE",
]
