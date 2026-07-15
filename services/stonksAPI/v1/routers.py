from fastapi import APIRouter

from services.stonksAPI.v1.market_data.quotes.router import router as quotes_router

router = APIRouter(prefix="/v1")
router.include_router(quotes_router)
