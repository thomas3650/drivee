from .base_model import BaseModel
from ..dtos.currency_dto import CurrencyDTO
from datetime import datetime
from typing import Optional

class Currency(BaseModel[CurrencyDTO]):
    @property
    def code(self) -> str:
        return self._dto.code

    @property
    def name(self) -> str:
        return self._dto.name

    @property
    def symbol(self) -> str:
        return self._dto.symbol

    @property
    def sign(self) -> str:
        return self._dto.sign

    @property
    def formatter(self) -> str:
        return self._dto.formatter

    @property
    def unit_price_formatter(self) -> str:
        return self._dto.unit_price_formatter

    @property
    def has_prefix(self) -> bool:
        return self._dto.has_prefix

    @property
    def prefix(self) -> Optional[str]:
        return self._dto.prefix

    @property
    def has_suffix(self) -> bool:
        return self._dto.has_suffix

    @property
    def suffix(self) -> Optional[str]:
        return self._dto.suffix

    @property
    def minor_unit_decimal(self) -> int:
        return self._dto.minor_unit_decimal

    @property
    def updated_at(self) -> datetime:
        return self._dto.updated_at
