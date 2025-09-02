"""DTOs for the Drivee API responses.

This package contains all Data Transfer Objects (DTOs) used to serialize and
deserialize data between the Drivee API and the client. DTOs are pure data
classes with validation but no business logic.
"""

from .base_dto import BaseDTO
from .charge_point_dto import ChargePointDTO, LocationDTO
from .charging_history_dto import ChargingHistoryDTO, ChargingHistoryEntryDTO
from .charging_period_dto import ChargingPeriodDTO
from .charging_responses_dto import StartChargingResponseDTO, EndChargingResponseDTO
from .charging_session_dto import ChargingSessionDTO
from .connector_dto import ConnectorDTO
from .currency_dto import CurrencyDTO
from .dto_protocol import (
    DTOProtocol,
    ChargePointDTOProtocol,
    EVSEDTOProtocol,
    ConnectorDTOProtocol,
    ChargingSessionDTOProtocol,
    ChargingPeriodDTOProtocol,
)
from .evse_dto import EVSEDTO
from .payment_details_dto import PaymentDetailsDTO

__all__ = [
    # Protocols
    'DTOProtocol',
    'ChargePointDTOProtocol',
    'EVSEDTOProtocol',
    'ConnectorDTOProtocol',
    'ChargingSessionDTOProtocol',
    'ChargingPeriodDTOProtocol',
    
    # Base classes
    'BaseDTO',
    
    # Charge point related
    'ChargePointDTO',
    'LocationDTO',
    'EVSEDTO',
    'ConnectorDTO',
    
    # Charging session related
    'ChargingSessionDTO',
    'ChargingPeriodDTO',
    'ChargingHistoryDTO',
    'ChargingHistoryEntryDTO',
    
    # Payment related
    'CurrencyDTO',
    'PaymentDetailsDTO',
        
    # API responses
    'StartChargingResponseDTO',
    'EndChargingResponseDTO',
]
