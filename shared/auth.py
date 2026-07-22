from fastapi import Header

from shared.error_handler import InvalidAPIKeyError
from shared.request_log import resolve_caller


async def verify_api_key(
    x_api_key: str | None = Header(default=None, description="Your StonksAPI access key. Required for all /v1 endpoints."),
) -> str:
    caller = resolve_caller(x_api_key)
    if caller is None:
        raise InvalidAPIKeyError()
    return caller
