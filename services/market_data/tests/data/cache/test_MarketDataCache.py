from unittest.mock import patch

from market_data.data.cache.MarketDataCache import MarketDataCache
from market_data.models.schemas import Quote, TickerInfo


def make_quote(ticker="AAPL", price=100.0, ts=1_700_000_000.0):
    return Quote(ticker=ticker, price=price, ts=ts)


def make_ticker_info(ticker="AAPL"):
    return TickerInfo(
        ticker=ticker,
        company_name="Apple Inc.",
        hq_location="Cupertino, CA",
        logo_url="https://example.com/logo.svg",
        market_cap=1.0,
    )


def test_get_returns_none_for_missing_entry():
    cache = MarketDataCache()
    assert cache.get("AAPL", Quote) is None


def test_set_then_get_returns_the_data():
    cache = MarketDataCache()
    quote = make_quote()
    cache.set(quote)
    assert cache.get("AAPL", Quote) == quote


def test_set_overwrites_existing_entry_of_the_same_type():
    cache = MarketDataCache()
    cache.set(make_quote(price=100.0))
    updated = make_quote(price=105.0)
    cache.set(updated)
    assert cache.get("AAPL", Quote) == updated


def test_different_types_for_same_ticker_do_not_clobber_each_other():
    cache = MarketDataCache()
    quote = make_quote()
    info = make_ticker_info()

    cache.set(quote)
    cache.set(info)

    assert cache.get("AAPL", Quote) == quote
    assert cache.get("AAPL", TickerInfo) == info


def test_expired_entry_is_pruned_and_get_returns_none():
    cache = MarketDataCache(ttl=10)

    with patch("market_data.data.cache.MarketDataCache.time.time", return_value=1000.0):
        cache.set(make_quote())

    with patch("market_data.data.cache.MarketDataCache.time.time", return_value=1000.0 + 11):
        assert cache.get("AAPL", Quote) is None
        assert "AAPL" not in cache.cache


def test_non_expired_entry_survives_prune():
    cache = MarketDataCache(ttl=10)

    with patch("market_data.data.cache.MarketDataCache.time.time", return_value=1000.0):
        quote = make_quote()
        cache.set(quote)

    with patch("market_data.data.cache.MarketDataCache.time.time", return_value=1005.0):
        assert cache.get("AAPL", Quote) == quote


def test_pruning_one_expired_type_does_not_remove_other_types_for_the_ticker():
    cache = MarketDataCache(ttl=10)

    with patch("market_data.data.cache.MarketDataCache.time.time", return_value=1000.0):
        cache.set(make_quote())

    with patch("market_data.data.cache.MarketDataCache.time.time", return_value=1005.0):
        info = make_ticker_info()
        cache.set(info)

    # Quote (set at t=1000, ttl=10) has expired by t=1011; TickerInfo (set at t=1005) has not.
    with patch("market_data.data.cache.MarketDataCache.time.time", return_value=1011.0):
        assert cache.get("AAPL", Quote) is None
        assert cache.get("AAPL", TickerInfo) == info
