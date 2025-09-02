"""DTO for currency data transfer."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from .base_dto import BaseDTO

@dataclass
class CurrencyDTO(BaseDTO):  # type: ignore[type-arg]
    """DTO representing currency configuration.
    
    Contains currency formatting and display information used for
    showing prices and amounts in the UI.
    """
    # Required fields from BaseDTO
    id: str
    
    # Optional fields from BaseDTO
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Currency fields
    code: str = ""  # ISO 4217 currency code (e.g., 'USD')
    name: str = ""  # Full currency name
    
    # Display formatting
    symbol: str = ""  # Currency symbol (e.g., '$')
    sign: str = ""  # Currency sign
    formatter: str = ""  # Format string for amounts
    unit_price_formatter: str = ""  # Format string for unit prices
    
    # Position configuration
    has_prefix: bool = False  # Whether symbol goes before amount
    prefix: Optional[str] = None  # Text to show before amount
    has_suffix: bool = False  # Whether symbol goes after amount
    suffix: str = ""  # Text to show after amount
    
    # Technical details
    minor_unit_decimal: int = 2  # Number of decimal places (0-6)
    
    def __post_init__(self) -> None:
        """Validate currency code is exactly 3 characters."""
        if len(self.code) != 0 and len(self.code) != 3:
            raise ValueError("Currency code must be exactly 3 characters")
    @classmethod
    def validate_currency_code(cls, v: str) -> str:
        """Validate currency code is 3 uppercase letters.
        
        Args:
            v: The currency code to validate
            
        Returns:
            str: The uppercase currency code
            
        Raises:
            ValueError: If code is not 3 letters
        """
        if len(v) != 3 or not v.isalpha():
            raise ValueError('Currency code must be 3 letters (e.g., USD)')
        return v.upper()
