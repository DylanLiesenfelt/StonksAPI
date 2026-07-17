import logging

import httpx

from shared.client import Client
from shared.logging_config import setup_logging
from shared.config import get_ADMIN_KEY, get_MASSIVE_KEY, get_STONKS_KEYS

from services.stonksAPI.utils.print_logo import print_logo

setup_logging()
logger = logging.getLogger("app")

def check_config():
    ADMIN = get_ADMIN_KEY()
    STONKS_KEYS = get_STONKS_KEYS()
    MASSIVE_KEY = get_MASSIVE_KEY()

    status = True if ADMIN and STONKS_KEYS and MASSIVE_KEY else False

    if not ADMIN:
        logger.warning("ADMIN_KEY is not set. System will not function properly.")
    if not STONKS_KEYS:
        logger.warning("STONKS_KEYS is not set. System will not function properly.")
    if not MASSIVE_KEY:
        logger.warning("MASSIVE_KEY is not set. System will not function properly.")

    return status

async def check_massive_health() -> bool:
    BASE = "https://api.massive.com/"
    KEY = f"apiKey={get_MASSIVE_KEY()}"
    DEFAULT_TICKER = "AAPL"

    # Mirrors the endpoints each v1/market_data provider actually calls
    URLS = {
        "related": BASE + f"v1/related-companies/{DEFAULT_TICKER}?" + KEY,
        "quotes": BASE + f"v3/snapshot?order=asc&limit=250&sort=ticker&ticker.any_of={DEFAULT_TICKER}&" + KEY,
        "ticker_info": BASE + f"v3/reference/tickers/{DEFAULT_TICKER}?" + KEY,
        "historical": BASE + f"v2/aggs/ticker/{DEFAULT_TICKER}/range/1/day/2023-01-03/2023-01-10?adjusted=true&sort=asc&limit=50000&" + KEY,
    }

    up = []
    down = []

    async with httpx.AsyncClient(timeout=5) as client:
        for endpoint, url in URLS.items():
            try:
                response = await client.get(url)
                status = response.status_code
            except httpx.HTTPError:
                status = None

            if status == 200:
                up.append(endpoint)
            else:
                down.append(endpoint)

    if down:
        for endpoint in down:
            logger.error(f"{endpoint} is down. Service will not function properly ❌")
        return False

    logger.info("All Massive API endpoints are up and running ✅")
    return True


async def healthy() -> bool:
    return await check_massive_health()

def ready() -> bool:

    if not check_config():
        return False

    return True


async def run_startup() -> tuple[Client, bool, bool]:
    logger.info("Starting Main Server... Standby")
    print_logo()

    client = Client()
    is_ready = ready()
    is_healthy = await healthy()

    logger.info(f"Main Server Ready: {'yes' if is_ready else 'no'}")
    logger.info(f"Main Server Healthy: {'yes' if is_healthy else 'no'}")

    return client, is_ready, is_healthy