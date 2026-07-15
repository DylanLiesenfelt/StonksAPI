from fastapi import APIRouter, Depends, Query, Request

from shared.client import Client
from services.stonksAPI.v1.market_data.ticker_info.provider import TickerInfoProvider
from services.stonksAPI.v1.market_data.ticker_info.schema import TickerInfoResponse
from services.stonksAPI.v1.market_data.ticker_info.service import TickerInfoService

router = APIRouter(prefix="/tickerinfo", tags=["ticker info"])


def get_client(request: Request) -> Client:
    return request.app.state.http


def get_provider(client: Client = Depends(get_client)) -> TickerInfoProvider:
    return TickerInfoProvider(client)


def get_service(provider: TickerInfoProvider = Depends(get_provider)) -> TickerInfoService:
    return TickerInfoService(provider)


@router.get("", response_model=TickerInfoResponse)
async def get_tickerinfo(
    ticker: str,
    date: str|int|None = None,
    service: TickerInfoService = Depends(get_service),
):
    return await service.get_tickerinfo(ticker, date)
