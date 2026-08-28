from unittest.mock import patch

from market_data.data.cache.MarketDataCache import MarketDataCache
from market_data.data.providers.schemas import TickerInfoResult, PriceBarsResult, PriceBar

request_id = {"request_id": "3c498ntp398fjxn", "global_id": "nyr4cq90pxyf"}


def make_ticker_info(ticker="AAPL"):
    return TickerInfoResult(
        request_id=request_id,
        ticker=ticker,
        company_name="Apple Inc.",
        hq_location={"city": "Cupertino", "state": "CA"},
        logo_url="https://example.com/logo.svg",
        market_cap=1.0,
        completed_at=1_000_000,
    )


def make_price_bars(ticker="AAPL"):
    return PriceBarsResult(
        request_id=request_id,
        ticker=ticker,
        data={1_700_000_000_000: PriceBar(open=1.0, high=1.0, low=1.0, close=1.0, volume=100, ts=1_700_000_000_000)},
        completed_at=1_000_000,
    )


def test_get_returns_none_for_missing_entry():
    cache = MarketDataCache()
    assert cache.get("AAPL", TickerInfoResult) is None


def test_set_then_get_returns_the_data():
    cache = MarketDataCache()
    info = make_ticker_info()
    cache.set(info)
    assert cache.get("AAPL", TickerInfoResult) == info


def test_set_overwrites_existing_entry_of_the_same_type():
    cache = MarketDataCache()
    cache.set(make_ticker_info())
    updated = make_ticker_info()
    updated.market_cap = 2.0
    cache.set(updated)
    assert cache.get("AAPL", TickerInfoResult) == updated


def test_different_types_for_same_ticker_do_not_clobber_each_other():
    cache = MarketDataCache()
    info = make_ticker_info()
    bars = make_price_bars()

    cache.set(info)
    cache.set(bars)

    assert cache.get("AAPL", TickerInfoResult) == info
    assert cache.get("AAPL", PriceBarsResult) == bars


def test_expired_entry_is_pruned_and_get_returns_none():
    cache = MarketDataCache(ttl=10)

    with patch("market_data.data.cache.MarketDataCache.ms_now", return_value=1000):
        cache.set(make_ticker_info())

    with patch("market_data.data.cache.MarketDataCache.ms_now", return_value=1000 + 11):
        assert cache.get("AAPL", TickerInfoResult) is None
        assert "AAPL" not in cache.cache


def test_non_expired_entry_survives_prune():
    cache = MarketDataCache(ttl=10)

    with patch("market_data.data.cache.MarketDataCache.ms_now", return_value=1000):
        info = make_ticker_info()
        cache.set(info)

    with patch("market_data.data.cache.MarketDataCache.ms_now", return_value=1005):
        assert cache.get("AAPL", TickerInfoResult) == info


def test_pruning_one_expired_type_does_not_remove_other_types_for_the_ticker():
    cache = MarketDataCache(ttl=10)

    with patch("market_data.data.cache.MarketDataCache.ms_now", return_value=1000):
        cache.set(make_ticker_info())

    with patch("market_data.data.cache.MarketDataCache.ms_now", return_value=1005):
        bars = make_price_bars()
        cache.set(bars)

    # TickerInfoResult (set at t=1000, ttl=10) has expired by t=1011; PriceBarsResult (set at t=1005) has not.
    with patch("market_data.data.cache.MarketDataCache.ms_now", return_value=1011):
        assert cache.get("AAPL", TickerInfoResult) is None
        assert cache.get("AAPL", PriceBarsResult) == bars
