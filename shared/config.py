import os
import json

from dotenv import load_dotenv

load_dotenv()

# Environment Variables
ENVIRONMENT = os.getenv("ENVIRONMENT")
STONKS_KEYS = json.loads(os.getenv("STONKS_KEYS"))
ADMIN_KEY = STONKS_KEYS['admin']

# External Keys
MASSIVE_KEY = os.getenv("MASSIVE_KEY")

# Internal URLs
INDEXES_URL = os.getenv("INDEXES_URL")
TRADES_URL = os.getenv("TRADES_URL")

INDEXES_DB_URL = os.getenv("INDEXES_DB_URL")
TRADES_DB_URL = os.getenv("TRADES_DB_URL")

def get_MASSIVE_KEY() -> str | None:
    return MASSIVE_KEY

def get_ADMIN_KEY() -> str | None:
    return ADMIN_KEY

def get_STONKS_KEYS() -> dict | None:
    return STONKS_KEYS    