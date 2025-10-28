from typing import List
from datetime import datetime, timedelta
from ..dtos.price_periods_dto import PricePeriodsDTO, PricePeriodDTO

class PricePeriod:
    def __init__(self, dto: PricePeriodDTO, granularity: int):
        # Combine at_day and at_time into a datetime object
        self.start_date = datetime.strptime(f"{dto.at_day} {dto.at_time}", "%Y-%m-%d %H:%M:%S")
        self.end_date = self.start_date + timedelta(minutes=granularity)
        self.price_per_kwh = dto.price_per_kwh

class PricePeriods:
    def __init__(self, dto: PricePeriodsDTO):
        self.granularity = dto.granularity
        self.periods: List[PricePeriod] = [PricePeriod(p, self.granularity) for p in dto.periods]

    def prices(self) -> List[PricePeriod]:
        return self.periods

    def get_price_at(self, dt: datetime) -> PricePeriod | None:
        """
        Returns the PricePeriod whose interval contains the given datetime, or None if not found.
        """
        for period in self.periods:
            if period.start_date <= dt < period.end_date:
                return period
        return None
