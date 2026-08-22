from abc import ABC, abstractmethod
from market_data.models.dataclasses.IndicatorParams import IndicatorParams
from market_data.models.dataclasses.IndicatorResult import IndicatorResult
from market_data.models.dataclasses.PriceBar import PriceBar

class IndicatorStrategy(ABC):

    @abstractmethod
    def calculate(self, data: list[PriceBar], params: IndicatorParams) -> IndicatorResult:
        pass