"""DTO for charging connector data transfer."""
from typing import Optional
from pydantic import Field

from .base_dto import BaseDTO

class ConnectorDTO(BaseDTO):
    """DTO representing a charging connector in the system.
    
    A connector is a physical plug or socket that connects to a vehicle.
    This DTO represents the pure data structure without any business logic.
    """
    
    # Core properties
    id: str = Field(description="Unique identifier for the connector")
    type: str = Field(description="Connector type (e.g., 'Type2', 'CCS')")
    status: str = Field(description="Current operational status")
    
    # Physical characteristics
    format: str = Field(description="Physical format (e.g., 'cable', 'socket')")
    max_power: float = Field(description="Maximum power output in kW")
    max_current: float = Field(description="Maximum current in amperes")
    
    # Optional properties
    icon: Optional[str] = Field(None, description="Icon identifier for UI")
    tariff_id: Optional[str] = Field(None, description="Associated tariff ID")
    last_status_update: Optional[str] = Field(None, description="Last status update timestamp")
