from fastapi import APIRouter, Depends, Query, Request

from shared.client import Client
from services.stonksAPI.v1.market_data.ticker_info.provider import TickerInfoProvider
from services.stonksAPI.v1.market_data.ticker_info.service import TickerInfoService

from services.stonksAPI.v1.market_data.ticker_info.schema import TickerInfoResponse
from services.stonksAPI.v1.market_data.ticker_info.schema import RelatedResponse


router = APIRouter(prefix="/tickerinfo", tags=["Ticker Info"])


def get_client(request: Request) -> Client:
    return request.app.state.http


def get_provider(client: Client = Depends(get_client)) -> TickerInfoProvider:
    return TickerInfoProvider(client)


def get_service(provider: TickerInfoProvider = Depends(get_provider)) -> TickerInfoService:
    return TickerInfoService(provider)


@router.get("", response_model=TickerInfoResponse)
async def get_ticker_info(
    ticker: str = Query(..., description="Stock ticker symbol, e.g. AAPL"),
    date: str|int|None = Query(None, description="Look up ticker info as of this date (MM-DD-YYYY). Defaults to the current date if omitted."),
    service: TickerInfoService = Depends(get_service),
):
    return await service.get_ticker_info(ticker, date)

@router.get("/related", response_model=RelatedResponse)
async def get_related(
    ticker: str = Query(..., description="Stock ticker symbol, e.g. AAPL"),
    service: TickerInfoService = Depends(get_service)
):
    return await service.get_related(ticker)