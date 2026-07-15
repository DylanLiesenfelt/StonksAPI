from fastapi import APIRouter

from services.stonksAPI.v1.market_data.routers import router as market_data_router

router = APIRouter(prefix="/v1")
router.include_router(market_data_router)
