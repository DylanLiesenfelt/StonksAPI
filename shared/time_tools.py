"""
Time related utility functions.
This application uses time format MM-DD-YYYY HH:MM:SS EST
"""
import holidays

from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

PRE_MARKET_OPEN = time(4, 0)
MARKET_OPEN = time(9, 30)
MARKET_CLOSE = time(16, 0)
TZ = "America/New_York"


def nyse_holidays(start_year: int, end_year: int) -> holidays.HolidayBase:
    """
    Freshly builds an NYSE holiday calendar covering [start_year, end_year].
    Built (never cached) on every call with explicit years so callers always
    get a fully populated range, instead of relying on holidays' per-year
    lazy loading, which silently omits years nobody has looked up yet.
    """
    return holidays.NYSE(years=range(start_year, end_year + 1))


def parse(date_str: str) -> datetime:
    dt = datetime.strptime(date_str, "%m-%d-%Y %H:%M:%S")
    return dt.replace(tzinfo=ZoneInfo(TZ))


# Get Times
# =================================================================
def get_current_time() -> str:
    return datetime.now(ZoneInfo(TZ)).strftime("%H:%M:%S")

def get_current_date() -> str:
    return datetime.now(ZoneInfo(TZ)).strftime("%m-%d-%Y")

def get_current_datetime() -> str:
    return datetime.now(ZoneInfo(TZ)).strftime("%m-%d-%Y %H:%M:%S")

# Conversions
# =================================================================
def convert_to_ms(date_str: str) -> int:
    dt = parse(date_str)
    return int(dt.timestamp() * 1000)

def convert_from_ms(ms: int) -> str:
    dt = datetime.fromtimestamp(ms / 1000, tz=ZoneInfo(TZ))
    return dt.strftime("%m-%d-%Y %H:%M:%S")

def convert_from_ns(ns: int) -> str:
    dt = datetime.fromtimestamp(ns / 1_000_000_000, tz=ZoneInfo(TZ))
    return dt.strftime("%m-%d-%Y %H:%M:%S")

# Flags
# =================================================================
def day_of_week(date_str: str) -> str:
    return parse(date_str).strftime("%A")

def is_holiday(date_str: str) -> bool:
    dt = parse(date_str)
    return dt.date() in nyse_holidays(dt.year, dt.year)

def is_weekend(date_str: str) -> bool:
    return parse(date_str).weekday() >= 5

def is_trading_day(date_str: str) -> bool:
    return not is_holiday(date_str) and not is_weekend(date_str)

def is_pre_market(date_str: str) -> bool:
    if not is_trading_day(date_str):
        return False
    return PRE_MARKET_OPEN <= parse(date_str).time() < MARKET_OPEN

def is_market_hours(date_str: str) -> bool:
    if not is_trading_day(date_str):
        return False
    return MARKET_OPEN <= parse(date_str).time() <= MARKET_CLOSE

def is_after_hours(date_str: str) -> bool:
    if not is_trading_day(date_str):
        return False
    return parse(date_str).time() > MARKET_CLOSE

# Date Deltas
# =================================================================
def next_holiday(date_str: str) -> tuple[str, int | None]:
    "returns the next holiday in MM-DD-YYYY format and how many days until that holiday"
    dt = parse(date_str)
    nyse_holidays = nyse_holidays(dt.year, dt.year + 1)
    for holiday_date in sorted(nyse_holidays):
        if holiday_date > dt.date():
            days_until = (holiday_date - dt.date()).days
            return holiday_date.strftime("%m-%d-%Y"), days_until
    return "", None

def next_trading_day(date_str: str) -> str:
    dt = parse(date_str)
    nyse_holidays = nyse_holidays(dt.year, dt.year + 1)
    next_day = dt.date()
    while True:
        next_day += timedelta(days=1)
        if next_day not in nyse_holidays and next_day.weekday() < 5:
            break
    return next_day.strftime("%m-%d-%Y")

def previous_trading_day(date_str: str) -> str:
    dt = parse(date_str)
    nyse_holidays = nyse_holidays(dt.year - 1, dt.year)
    prev_day = dt.date()
    while True:
        prev_day -= timedelta(days=1)
        if prev_day not in nyse_holidays and prev_day.weekday() < 5:
            break
    return prev_day.strftime("%m-%d-%Y")

def last_trading_day_of_week(date_str: str) -> str:
    dt = parse(date_str)
    nyse_holidays = nyse_holidays(dt.year - 1, dt.year)
    last_day = dt.date()
    while True:
        if last_day.weekday() == 4 and last_day not in nyse_holidays:
            break
        last_day -= timedelta(days=1)
    return last_day.strftime("%m-%d-%Y")

def last_trading_day_of_month(date_str: str) -> str:
    dt = parse(date_str)
    nyse_holidays = nyse_holidays(dt.year - 1, dt.year)
    last_day = dt.date().replace(day=1) + timedelta(days=32)
    last_day = last_day.replace(day=1) - timedelta(days=1)
    while True:
        if last_day.weekday() < 5 and last_day not in nyse_holidays:
            break
        last_day -= timedelta(days=1)
    return last_day.strftime("%m-%d-%Y")

def last_trading_day_ndays_ago(date_str: str, n: int) -> str:
    dt = parse(date_str)
    # ~252 trading days/year; overestimate the calendar-year span so the
    # walk below never steps outside the populated holiday range.
    years_back = n // 200 + 2
    nyse_holidays = nyse_holidays(dt.year - years_back, dt.year)
    last_day = dt.date()
    count = 0
    while count < n:
        last_day -= timedelta(days=1)
        if last_day.weekday() < 5 and last_day not in nyse_holidays:
            count += 1
    return last_day.strftime("%m-%d-%Y")
