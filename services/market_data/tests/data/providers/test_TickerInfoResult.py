import pydantic
import pytest

from market_data.data.providers.schemas import TickerInfoResult

request_id = {"request_id": "3c498ntp398fjxn", "global_id": "nyr4cq90pxyf"}

valid_data = {
    "request_id": request_id,
    "ticker": "AAPL",
    "company_name": "Apple Inc.",
    "hq_location": {"city": "Cupertino", "state": "CA"},
    "logo_url": "https://api.massive.com/v1/reference/company-branding/YXBwbGUuY29t/images/2026-08-01_logo.svg",
    "market_cap": 4514709583000.0,
    "completed_at": 1_700_000_000_000
}

invalid_ticker = {**valid_data, "ticker": 12345}
invalid_company_name = {**valid_data, "company_name": 12345}
invalid_hq_location = {**valid_data, "hq_location": 12345}
invalid_logo_url = {**valid_data, "logo_url": 12345}
invalid_market_cap = {**valid_data, "market_cap": "not_a_marketcap"}
invalid_completed_at = {**valid_data, "completed_at": "not_a_valid_timestamp"}

invalid_data = [
    invalid_ticker,
    invalid_company_name,
    invalid_hq_location,
    invalid_logo_url,
    invalid_market_cap,
    invalid_completed_at,
]


def test_TickerInfoResult_accepts_valid_data():
    t = TickerInfoResult(**valid_data)
    assert t.ticker == "AAPL"
    assert t.company_name == "Apple Inc."
    assert t.hq_location == {"city": "Cupertino", "state": "CA"}
    assert t.logo_url == valid_data["logo_url"]
    assert t.market_cap == 4514709583000.0
    assert isinstance(t.completed_at, int)


def test_TickerInfoResult_rejects_invalid_data():
    for d in invalid_data:
        with pytest.raises(pydantic.ValidationError):
            TickerInfoResult(**d)
