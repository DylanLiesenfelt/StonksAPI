from market_data.data.providers.schemas import PriceBar, PriceBarsResult
from market_data.service.indicators.schemas import IndicatorRequest, IndicatorResult
from market_data.service.indicators.strategies import EMA

DAY_MS = 86400000
BASE_TS_MS = 1672531200000  # 2023-01-01T00:00:00Z, fixed so tests are deterministic


def ts_for_day(day):
    return BASE_TS_MS + (day - 1) * DAY_MS


def make_bar(day, close):
    return PriceBar(
        open=close,
        high=close,
        low=close,
        close=close,
        volume=1000,
        ts=ts_for_day(day)
    )


request_id = {"request_id": "3c498ntp398fjxn", "global_id": "nyr4cq90pxyf"}

history = {ts_for_day(day): make_bar(day, close) for day, close in enumerate([1.0, 2.0, 3.0, 4.0, 5.0], start=1)}

data = PriceBarsResult(request_id=request_id, ticker="AAPL", data=history)

request = IndicatorRequest(
    request_id=request_id,
    indicator_method="EMA",
    ticker="AAPL",
    period=3,
    timeframe="day",
    multiplier=1,
    start=ts_for_day(1),
    end=ts_for_day(5),
)


def test_EMA_calculate_computes_ema():
    result = EMA().calculate(data, request)
    # mult = 2 / (3 + 1) = 0.5
    # seed (day 3) = SMA(1, 2, 3) = 2.0
    # day 4 = 4.0 * 0.5 + 2.0 * 0.5 = 3.0
    # day 5 = 5.0 * 0.5 + 3.0 * 0.5 = 4.0
    expected = {
        ts_for_day(3): 2.0,
        ts_for_day(4): 3.0,
        ts_for_day(5): 4.0,
    }
    assert result.result == expected


def test_EMA_calculate_drops_incomplete_windows():
    result = EMA().calculate(data, request)
    assert len(result.result) == len(history) - 3 + 1


def test_EMA_calculate_returns_indicator_result():
    result = EMA().calculate(data, request)
    assert isinstance(result, IndicatorResult)
    assert result.request_id == request_id
    assert result.ticker == "AAPL"
