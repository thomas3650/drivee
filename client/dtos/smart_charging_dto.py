"""DTO for smart charging configuration data transfer."""
from typing import Dict, List, Optional, Literal
from datetime import datetime
from pydantic import Field, field_validator

from .base_dto import BaseDTO

ChargingModeType = Literal["eco", "fast", "solar", "scheduled"]
WeekdayType = Literal["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

class SmartChargingDTO(BaseDTO):
    """DTO representing smart charging configuration.
    
    Contains settings for optimizing charging based on various factors like
    solar production, electricity rates, and scheduling preferences.
    """
    
    # Core settings
    enabled: bool = Field(description="Whether smart charging is enabled")
    mode: ChargingModeType = Field(description="Smart charging mode")
    
    # Target configuration
    target_charge: Dict[str, str] = Field(
        description="Target charging parameters"
    )
    start_time: str = Field(description="Daily start time (HH:MM:SS)")
    end_time: str = Field(description="Daily end time (HH:MM:SS)")
    weekdays: Optional[List[WeekdayType]] = Field(
        None,
        description="Days when schedule applies"
    )
    
    # Solar charging settings
    use_solar: bool = Field(description="Whether to use solar power")
    use_all_generated_solar: Optional[bool] = Field(
        None,
        description="Whether to use all available solar power"
    )
    max_current_from_grid_a: Optional[int] = Field(
        None,
        gt=0,
        description="Maximum current to draw from grid"
    )
    solar_stable_time_sec: Optional[int] = Field(
        None,
        ge=0,
        description="Required stable solar production time"
    )
    
    # Dynamic pricing
    dynamic_rates_integration_id: Optional[int] = Field(
        None,
        description="ID of dynamic rates provider"
    )

    @field_validator('start_time', 'end_time')
    @classmethod
    def validate_time_format(cls, v: str) -> str:
        """Validate time strings are in HH:MM:SS format.
        
        Args:
            v: Time string to validate
            
        Returns:
            str: The validated time string
            
        Raises:
            ValueError: If time string is not in HH:MM:SS format
        """
        try:
            datetime.strptime(v, "%H:%M:%S")
            return v
        except ValueError:
            raise ValueError(
                "Time must be in HH:MM:SS format (e.g., 13:30:00)"
            )
