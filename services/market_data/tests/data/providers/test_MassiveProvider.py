from types import SimpleNamespace

from market_data.data.providers.MassiveProvider import MassiveProvider
from market_data.data.providers.schemas import QuotesRequest, TickerInfoRequest, PriceBarsRequest


class FakeClient:
    """Stands in for massive.RESTClient so tests never hit the network."""

    def __init__(self, snapshot=None, details=None, aggs=None):
        self._snapshot = snapshot
        self._details = details
        self._aggs = aggs or []
        self.calls = []

    def get_snapshot_ticker(self, market_type, ticker):
        self.calls.append(("get_snapshot_ticker", market_type, ticker))
        return self._snapshot

    def get_ticker_details(self, ticker):
        self.calls.append(("get_ticker_details", ticker))
        return self._details

    def list_aggs(self, ticker, window, timeframe, start, end, adjusted=None, sort=None, limit=None):
        self.calls.append(("list_aggs", ticker, window, timeframe, start, end, adjusted, sort, limit))
        return iter(self._aggs)


def make_provider(client):
    # bypass __init__ so tests don't need a real MASSIVE_KEY / RESTClient
    provider = MassiveProvider.__new__(MassiveProvider)
    provider.key = "test-key"
    provider.client = client
    return provider


request_id = {"request_id": "3c498ntp398fjxn", "global_id": "nyr4cq90pxyf"}


def test_get_quotes_maps_snapshot_into_quotes_result():
    snapshot = SimpleNamespace(min=SimpleNamespace(close=189.5, timestamp=1_700_000_000_000))
    client = FakeClient(snapshot=snapshot)
    provider = make_provider(client)

    request = QuotesRequest(request_id=request_id, tickers=["AAPL"], received_at=1_700_000_000_000)
    result = provider.get_quotes(request)

    assert result.tickers == ["AAPL"]
    assert result.data["AAPL"].price == 189.5
    assert result.data["AAPL"].ts == 1_700_000_000_000
    assert isinstance(result.completed_at, int)
    assert client.calls == [("get_snapshot_ticker", "stocks", "AAPL")]


def test_get_ticker_info_maps_details_into_ticker_info_result():
    details = SimpleNamespace(
        name="Apple Inc.",
        address=SimpleNamespace(city="Cupertino", state="CA"),
        branding=SimpleNamespace(logo_url="https://example.com/logo.svg"),
        market_cap=3_000_000_000_000.0,
    )
    client = FakeClient(details=details)
    provider = make_provider(client)

    request = TickerInfoRequest(request_id=request_id, ticker="AAPL", received_at=1_700_000_000_000)
    result = provider.get_ticker_info(request)

    assert result.ticker == "AAPL"
    assert result.company_name == "Apple Inc."
    assert result.hq_location == {"city": "Cupertino", "state": "CA"}
    assert result.logo_url == "https://example.com/logo.svg"
    assert result.market_cap == 3_000_000_000_000.0
    assert isinstance(result.completed_at, int)
    assert client.calls == [("get_ticker_details", "AAPL")]


def test_get_ticker_bars_maps_aggs_into_price_bars_result():
    aggs = [
        SimpleNamespace(open=1.0, high=2.0, low=0.5, close=1.5, volume=100, timestamp=1_700_000_000_000),
        SimpleNamespace(open=1.5, high=2.5, low=1.0, close=2.0, volume=200, timestamp=1_700_000_060_000),
    ]
    client = FakeClient(aggs=aggs)
    provider = make_provider(client)

    request = PriceBarsRequest(
        request_id=request_id,
        ticker="AAPL",
        window=1,
        timeframe="minute",
        start=1_700_000_000_000,
        end=1_700_000_100_000,
        received_at=1_700_000_000_000,
    )
    result = provider.get_ticker_bars(request)

    assert result.ticker == "AAPL"
    assert set(result.data.keys()) == {1_700_000_000_000, 1_700_000_060_000}
    assert result.data[1_700_000_000_000].close == 1.5
    assert result.data[1_700_000_060_000].volume == 200
    assert isinstance(result.completed_at, int)
    assert client.calls == [
        ("list_aggs", "AAPL", 1, "minute", 1_700_000_000_000, 1_700_000_100_000, True, "asc", 32000)
    ]
