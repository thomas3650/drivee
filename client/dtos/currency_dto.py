"""DTO for currency data transfer."""
from typing import Optional
from pydantic import Field, field_validator

from .base_dto import BaseDTO

class CurrencyDTO(BaseDTO):
    """DTO representing currency configuration.
    
    Contains currency formatting and display information used for
    showing prices and amounts in the UI.
    """
    code: str = Field(
        max_length=3,
        min_length=3,
        description="ISO 4217 currency code (e.g., 'USD')"
    )
    name: str = Field(description="Full currency name")
    
    # Display formatting
    symbol: str = Field(description="Currency symbol (e.g., '$')")
    sign: str = Field(description="Currency sign")
    formatter: str = Field(description="Format string for amounts")
    unit_price_formatter: str = Field(
        alias='unitPriceFormatter',
        description="Format string for unit prices"
    )
    
    # Position configuration
    has_prefix: bool = Field(
        description="Whether symbol goes before amount"
    )
    prefix: Optional[str] = Field(
        None,
        description="Text to show before amount"
    )
    has_suffix: bool = Field(
        description="Whether symbol goes after amount"
    )
    suffix: str = Field(description="Text to show after amount")
    
    # Technical details
    minor_unit_decimal: int = Field(
        ge=0,
        le=6,
        description="Number of decimal places"
    )
    
    @field_validator('code')
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
