from pydantic import BaseModel, Field
from typing import List

class PricePeriodDTO(BaseModel):
    at_day: str = Field(..., alias="atDay")
    at_time: str = Field(..., alias="atTime")
    price_per_kwh: float = Field(..., alias="pricePerKwh")

class PricePeriodsDTO(BaseModel):
    granularity: int
    periods: List[PricePeriodDTO]
