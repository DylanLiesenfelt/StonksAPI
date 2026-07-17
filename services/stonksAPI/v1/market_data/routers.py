from fastapi import APIRouter

from services.stonksAPI.v1.market_data.quotes.router import router as quotes
from services.stonksAPI.v1.market_data.historical.router import router as historical
from services.stonksAPI.v1.market_data.ticker_info.router import router as tickerinfo
from services.stonksAPI.v1.market_data.market_status.router import router as marketstatus

router = APIRouter(prefix="/marketdata")
router.include_router(quotes)
router.include_router(historical)
router.include_router(tickerinfo)
router.include_router(marketstatus)
