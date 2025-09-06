"""DTO for currency data transfer."""
from __future__ import annotations
from datetime import datetime
from typing import Optional
from pydantic import Field

from .base_dto import BaseDTO

class CurrencyDTO(BaseDTO):
    """DTO representing currency configuration.
    
    Contains currency formatting and display information used for
    showing prices and amounts in the UI.
    """
    
    # Currency fields
    code: str = Field(..., alias="code")  # ISO 4217 currency code (e.g., 'USD')
    name: str = Field(..., alias="name")  # Full currency name
    
    # Display formatting
    symbol: str = Field(..., alias="symbol")  # Currency symbol (e.g., '$')
    sign: str = Field(..., alias="sign")  # Currency sign
    formatter: str = Field(..., alias="formatter")  # Format string for amounts
    unit_price_formatter: str = Field(..., alias="unitPriceFormatter")  # Format string for unit prices
    
    # Position configuration
    has_prefix: bool = Field(..., alias="hasPrefix")  # Whether symbol goes before amount
    prefix: Optional[str] = Field(default=None, alias="prefix")  # Text to show before amount
    has_suffix: bool = Field(..., alias="hasSuffix")  # Whether symbol goes after amount
    suffix: Optional[str] = Field(default=None, alias="suffix")  # Text to show after amount
    
    # Technical details
    minor_unit_decimal: int = Field(..., alias="minorUnitDecimal")  # Number of decimal places (0-6)
    updated_at: datetime = Field(..., alias="updatedAt")  # Last updated timestamp
