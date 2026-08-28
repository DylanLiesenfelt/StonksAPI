import os
from dotenv import load_dotenv
from massive import RESTClient

from market_data.utils import ms_now
from market_data.data.providers.Provider import Provider
from market_data.data.providers.schemas import (
    PriceBarsRequest,
    PriceBarsResult,
    PriceBar,
    QuotesRequest,
    QuotesResult,
    Quote,
    TickerInfoRequest,
    TickerInfoResult,
)

load_dotenv()


class MassiveProvider(Provider):
    def __init__(self):
        self.key = os.getenv("MASSIVE_KEY")
        self.client = RESTClient(self.key)

    def get_quotes(self, request: QuotesRequest) -> QuotesResult:
        data = {}
        for ticker in request.tickers:
            res = self.client.get_snapshot_ticker("stocks", str(ticker))
            data[ticker] = Quote(price=res.min.close, ts=res.min.timestamp)

        return QuotesResult(
            request_id=request.request_id,
            tickers=request.tickers,
            data=data,
            completed_at=ms_now()
        )

    def get_ticker_info(self, request: TickerInfoRequest) -> TickerInfoResult:
        res = self.client.get_ticker_details(str(request.ticker))

        return TickerInfoResult(
            request_id=request.request_id,
            ticker=request.ticker,
            company_name=res.name,
            hq_location={"city": res.address.city, "state": res.address.state},
            logo_url=res.branding.logo_url,
            market_cap=res.market_cap,
            completed_at=ms_now()
        )

    def get_ticker_bars(self, request: PriceBarsRequest) -> PriceBarsResult:
        aggs = self.client.list_aggs(
            request.ticker,
            request.window,
            request.timeframe,
            request.start,
            request.end,
            adjusted=True,
            sort="asc",
            limit=32000
        )

        data = {
            agg.timestamp: PriceBar(
                open=agg.open,
                high=agg.high,
                low=agg.low,
                close=agg.close,
                volume=agg.volume,
                ts=agg.timestamp
            )
            for agg in aggs
        }

        return PriceBarsResult(
            request_id=request.request_id,
            ticker=request.ticker,
            data=data,
            completed_at=ms_now()
        )

MASSIVE = MassiveProvider()