from fastapi import APIRouter, Depends

from services.stonksAPI.v1.market_data.routers import router as market_data_router
from shared.auth import verify_api_key

router = APIRouter(prefix="/v1", dependencies=[Depends(verify_api_key)])
router.include_router(market_data_router)
