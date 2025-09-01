"""Currency DTO."""
from datetime import datetime
from typing import Optional
from pydantic import Field, field_validator

from .base_dto import DTOBase

class Currency(DTOBase):
    """Model for currency information."""
    id: int
    name: str
    symbol: str
    sign: str
    code: str
    formatter: str
    unit_price_formatter: str = Field(alias='unitPriceFormatter')
    updated_at: datetime
    minor_unit_decimal: int
    has_prefix: bool
    has_suffix: bool
    prefix: Optional[str] = None
    suffix: str


    
    @field_validator('code')
    @classmethod
    def validate_currency_code(cls, v: str) -> str:
        """Validate currency code is 3 letters."""
        if len(v) != 3 or not v.isalpha():
            raise ValueError('Currency code must be 3 letters')
        return v.upper()
