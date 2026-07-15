from fastapi import APIRouter

from services.stonksAPI.v1.market_data.quotes.router import router as quotes_router
from services.stonksAPI.v1.market_data.historical.router import router as historical_router

router = APIRouter(prefix="/v1")
router.include_router(quotes_router)
router.include_router(historical_router)
