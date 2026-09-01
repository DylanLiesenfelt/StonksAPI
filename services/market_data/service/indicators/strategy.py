from abc import ABC, abstractmethod

from market_data.data.providers.schemas import PriceBarsResult
from market_data.service.indicators.schemas import IndicatorRequest, IndicatorResult


class IndicatorStrategy(ABC):

    @abstractmethod
    def calculate(self, data: PriceBarsResult, request: IndicatorRequest) -> IndicatorResult:
        pass

