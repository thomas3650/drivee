from typing import List
from ..dtos.price_periods_dto import PricePeriodsDTO, PricePeriodDTO

class PricePeriod:
    def __init__(self, dto: PricePeriodDTO):
        self.day = dto.at_day
        self.time = dto.at_time
        self.price_per_kwh = dto.price_per_kwh

class PricePeriods:
    def __init__(self, dto: PricePeriodsDTO):
        self.granularity = dto.granularity
        self.periods: List[PricePeriod] = [PricePeriod(p) for p in dto.periods]

    def get_prices(self) -> List[PricePeriod]:
        return self.periods
