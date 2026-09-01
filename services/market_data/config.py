import os
from dotenv import load_dotenv

load_dotenv()

MASSIVE_KEY = os.getenv("MASSIVE_KEY")
REQUEST_TIMEOUT_SECONDS = float(os.getenv("MARKET_DATA_REQUEST_TIMEOUT_SECONDS", "10"))
MAX_RETRIES = int(os.getenv("MARKET_DATA_MAX_RETRIES", "3"))
RETRY_BACKOFF_SECONDS = float(os.getenv("MARKET_DATA_RETRY_BACKOFF_SECONDS", "0.5"))
