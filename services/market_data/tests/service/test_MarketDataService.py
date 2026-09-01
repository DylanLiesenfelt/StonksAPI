from market_data.data.providers.schemas import PriceBar, PriceBarsResult
from market_data.service.indicators.schemas import IndicatorRequest, IndicatorResult
from market_data.service.MarketDataService import MarketDataService

DAY_MS = 86400000
BASE_TS_MS = 1672531200000  # 2023-01-01T00:00:00Z, fixed so tests are deterministic


def ts_for_day(day):
    return BASE_TS_MS + (day - 1) * DAY_MS


def make_bar(day, close):
    return PriceBar(open=close, high=close, low=close, close=close, volume=1000, ts=ts_for_day(day))


request_id = {"request_id": "3c498ntp398fjxn", "global_id": "nyr4cq90pxyf"}

history = {ts_for_day(day): make_bar(day, close) for day, close in enumerate([1.0, 2.0, 3.0, 4.0, 5.0], start=1)}


class FakeProvider:
    def __init__(self, bars):
        self.calls = []
        self._bars = bars

    def get_ticker_bars(self, request):
        self.calls.append(request)
        return PriceBarsResult(request_id=request.request_id, ticker=request.ticker, data=self._bars)


def make_service(provider):
    service = MarketDataService()
    service.provider = provider
    return service


def test_get_indicator_forwards_multiplier_not_period_to_price_bars_request():
    provider = FakeProvider(history)
    service = make_service(provider)

    request = IndicatorRequest(
        request_id=request_id,
        indicator_method="SMA",
        ticker="AAPL",
        period=3,
        timeframe="day",
        multiplier=1,
        start=ts_for_day(1),
        end=ts_for_day(5),
    )

    service.get_indicator(request)

    assert len(provider.calls) == 1
    bars_request = provider.calls[0]
    assert bars_request.multiplier == 1
    assert bars_request.timeframe == "day"


def test_get_indicator_returns_indicator_result_using_period_as_lookback():
    provider = FakeProvider(history)
    service = make_service(provider)

    request = IndicatorRequest(
        request_id=request_id,
        indicator_method="SMA",
        ticker="AAPL",
        period=3,
        timeframe="day",
        multiplier=1,
        start=ts_for_day(1),
        end=ts_for_day(5),
    )

    result = service.get_indicator(request)

    assert isinstance(result, IndicatorResult)
    assert result.result == {
        ts_for_day(3): 2.0,
        ts_for_day(4): 3.0,
        ts_for_day(5): 4.0,
    }


def test_market_data_service_constructs_cleanly():
    MarketDataService()
