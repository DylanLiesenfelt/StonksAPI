from fastapi import APIRouter, Depends, Query, Request

from shared.client import Client
from services.stonksAPI.v1.market_data.historical.provider import HistoricalProvider
from services.stonksAPI.v1.market_data.historical.schema import HistoricalResponse
from services.stonksAPI.v1.market_data.historical.service import HistoricalService

router = APIRouter(prefix="/historical", tags=["Historical"])


def get_client(request: Request) -> Client:
    return request.app.state.http


def get_provider(client: Client = Depends(get_client)) -> HistoricalProvider:
    return HistoricalProvider(client)


def get_service(provider: HistoricalProvider = Depends(get_provider)) -> HistoricalService:
    return HistoricalService(provider)


@router.get("", response_model=HistoricalResponse)
async def get_historical(
    ticker: str = Query(..., description="Stock ticker symbol, e.g. AAPL"),
    interval: int = Query(15, description="Size of each bar, paired with timeframe (e.g. 15 + minute = 15-minute bars)"),
    timeframe: str = Query("minute", description="Bar unit: minute, hour, day, week, month, quarter, or year"),
    start_date: str|int|None = Query(None, description="Start of the range (MM-DD-YYYY). Defaults to 01-02-2026 if omitted."),
    end_date: str|int|None = Query(None, description="End of the range (MM-DD-YYYY). Defaults to the current date if omitted."),
    service: HistoricalService = Depends(get_service),
):
    return await service.get_historical(ticker, interval, timeframe, start_date, end_date)
