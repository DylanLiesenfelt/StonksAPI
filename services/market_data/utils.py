from datetime import datetime, timezone


def dt_to_unixMS(dt: datetime) -> int:
    return int(dt.timestamp() * 1000)


def unixMS_to_dt(ms: int) -> datetime:
    return datetime.fromtimestamp(ms / 1000, timezone.utc)
