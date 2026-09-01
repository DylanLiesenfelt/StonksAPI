from market_data.data.providers.schemas import PriceBar, PriceBarsResult
from market_data.service.indicators.schemas import IndicatorRequest, IndicatorResult
from market_data.service.indicators.strategies import ATR

DAY_MS = 86400000
BASE_TS_MS = 1672531200000  # 2023-01-01T00:00:00Z, fixed so tests are deterministic


def ts_for_day(day):
    return BASE_TS_MS + (day - 1) * DAY_MS


def make_bar(day, high, low, close):
    return PriceBar(
        open=close,
        high=high,
        low=low,
        close=close,
        volume=1000,
        ts=ts_for_day(day)
    )


request_id = {"request_id": "3c498ntp398fjxn", "global_id": "nyr4cq90pxyf"}

bars = [
    (10, 8, 9),
    (13, 9, 11),
    (12, 10, 11),
    (15, 11, 13),
    (14, 12, 13),
]
history = {ts_for_day(day): make_bar(day, high, low, close) for day, (high, low, close) in enumerate(bars, start=1)}

data = PriceBarsResult(request_id=request_id, ticker="AAPL", data=history)

request = IndicatorRequest(
    request_id=request_id,
    indicator_method="ATR",
    ticker="AAPL",
    period=2,
    timeframe="day",
    multiplier=1,
    start=ts_for_day(1),
    end=ts_for_day(5),
)


def test_ATR_calculate_computes_wilder_smoothed_average():
    result = ATR().calculate(data, request)
    # true ranges (using prev bar's close):
    # day 2: max(13-9, |13-9|, |9-9|)   = 4
    # day 3: max(12-10, |12-11|, |10-11|) = 2
    # day 4: max(15-11, |15-11|, |11-11|) = 4
    # day 5: max(14-12, |14-13|, |12-13|) = 2
    # seed (day 3) = avg(TR day2, TR day3) = avg(4, 2) = 3.0
    # day 4 = ((3.0 * (2-1)) + 4) / 2 = 3.5
    # day 5 = ((3.5 * (2-1)) + 2) / 2 = 2.75
    expected = {
        ts_for_day(3): 3.0,
        ts_for_day(4): 3.5,
        ts_for_day(5): 2.75,
    }
    assert result.result == expected


def test_ATR_calculate_drops_incomplete_windows():
    result = ATR().calculate(data, request)
    # ATR needs an extra prior bar for the first true range, so it yields
    # one fewer point than SMA/EMA/VWAP would for the same period
    assert len(result.result) == len(history) - 2


def test_ATR_calculate_returns_indicator_result():
    result = ATR().calculate(data, request)
    assert isinstance(result, IndicatorResult)
    assert result.request_id == request_id
    assert result.ticker == "AAPL"
