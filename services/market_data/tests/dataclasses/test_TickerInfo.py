from market_data.models.schemas import TickerInfo
import pydantic
import pytest

valid_data = {
    "ticker" : "AAPL",
    "company_name" : "Apple Inc.", 
    "hq_location" : "Cuppertino, CA",
    "logo_url" : "https://api.massive.com/v1/reference/company-branding/YXBwbGUuY29t/images/2026-08-01_logo.svg",
    "market_cap" : 4514709583000.0
}

invalid_ticker = {
   "ticker" : 12345,
    "company_name" : "Apple Inc.", 
    "hq_location" : "Cuppertino, CA",
    "logo_url" : "https://api.massive.com/v1/reference/company-branding/YXBwbGUuY29t/images/2026-08-01_logo.svg",
    "market_cap" : 4514709583000.0
}

invalid_name = {
    "ticker": "AAPL",
    "company_name" : 12345, 
    "hq_location" : "Cuppertino, CA",
    "logo_url" : "https://api.massive.com/v1/reference/company-branding/YXBwbGUuY29t/images/2026-08-01_logo.svg",
    "market_cap" : 4514709583000.0
}

invalid_location = {
    "ticker": "AAPL",
    "company_name" : "Apple Inc.", 
    "hq_location" : 12345,
    "logo_url" : "https://api.massive.com/v1/reference/company-branding/YXBwbGUuY29t/images/2026-08-01_logo.svg",
    "market_cap" : 4514709583000.0
}

invalid_logo = {
    "ticker": "AAPL",
    "company_name" : "Apple Inc.", 
    "hq_location" : "Cuppertino, CA",
    "logo_url" : 12345,
    "market_cap" : 4514709583000.0
}

invalid_marketcap = {
    "ticker": "AAPL",
    "company_name" : "Apple Inc.", 
    "hq_location" : "Cuppertino, CA",
    "logo_url" : "https://api.massive.com/v1/reference/company-branding/YXBwbGUuY29t/images/2026-08-01_logo.svg",
    "market_cap" : "not_a_marketcap"
}

invalid_data = [invalid_ticker, invalid_location, invalid_name, invalid_marketcap, invalid_logo]


def test_TickerInfo_accepts_valid_data():
    t = TickerInfo(**valid_data)
    assert t.ticker == "AAPL"
    assert t.company_name == "Apple Inc."
    assert t.hq_location == "Cuppertino, CA"
    assert t.logo_url == "https://api.massive.com/v1/reference/company-branding/YXBwbGUuY29t/images/2026-08-01_logo.svg"
    assert t.market_cap == 4514709583000.0


def test_TickerInfo_rejects_invalid_data():
    for d in invalid_data:
        with pytest.raises(pydantic.ValidationError):
            TickerInfo(**d)