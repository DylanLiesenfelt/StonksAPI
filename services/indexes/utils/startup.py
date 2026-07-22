import logging


from shared.client import Client
from shared.logging_config import setup_logging
from shared.config import get_ADMIN_KEY, get_MASSIVE_KEY, get_STONKS_KEYS


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


async def healthy() -> bool:
    return True

def ready() -> bool:

    if not check_config():
        return False

    return True


async def run_startup() -> tuple[Client, bool, bool]:
    logger.info("Starting Indexes Server... Standby")

    client = Client()
    is_ready = ready()
    is_healthy = await healthy()

    logger.info(f"Indexes Server Ready: {'yes' if is_ready else 'no'}")
    logger.info(f"Indexes Server Healthy: {'yes' if is_healthy else 'no'}")

    return client, is_ready, is_healthy