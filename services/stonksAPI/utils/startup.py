import logging
from shared.client import Client
from shared.logging_config import setup_logging

from services.stonksAPI.utils.print_logo import print_logo

setup_logging()
logger = logging.getLogger("app")

async def run_startup() -> Client:
    logger.info("Starting Main Server... Standby")
    print_logo()

    # More shit here later

    return Client()