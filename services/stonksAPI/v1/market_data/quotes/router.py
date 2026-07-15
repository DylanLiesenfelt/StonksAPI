from fastapi import APIRouter, Depends, Query, Request

from shared.client import Client
from services.stonksAPI.v1.market_data.quotes.provider import QuotesProvider
from services.stonksAPI.v1.market_data.quotes.schema import QuotesResponse
from services.stonksAPI.v1.market_data.quotes.service import QuotesService

router = APIRouter(prefix="/quotes", tags=["quotes"])


def get_client(request: Request) -> Client:
    return request.app.state.http


def get_provider(client: Client = Depends(get_client)) -> QuotesProvider:
    return QuotesProvider(client)


def get_service(provider: QuotesProvider = Depends(get_provider)) -> QuotesService:
    return QuotesService(provider)


@router.get("", response_model=QuotesResponse)
async def get_quotes(
    tickers: list[str] = Query(...),
    service: QuotesService = Depends(get_service),
):
    return await service.get_quotes(tickers)
