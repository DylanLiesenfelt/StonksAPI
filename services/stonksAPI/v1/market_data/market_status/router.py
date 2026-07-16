from fastapi import APIRouter, Depends, Request
from fastapi import Query
from services.stonksAPI.v1.market_data.market_status.schema import MarketStatus
from services.stonksAPI.v1.market_data.market_status.service import MarketStatusService

router = APIRouter(prefix="/marketstatus", tags=["Market Status"])

def get_service():
    return MarketStatusService()

@router.get("", response_model=MarketStatus)
async def get_market_status(
    service: MarketStatusService = Depends(get_service)
):
    return await service.get_market_status()
