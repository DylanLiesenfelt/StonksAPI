import secrets

from starlette.requests import Request

from shared.config import get_STONKS_KEYS


def resolve_caller(api_key: str | None) -> str | None:
    if not api_key:
        return None

    for name, valid_key in get_STONKS_KEYS().items():
        if secrets.compare_digest(api_key, valid_key):
            return name

    return None


def describe_request(request: Request) -> str:
    path = request.url.path
    if request.url.query:
        path += "?" + request.url.query

    raw_key = request.headers.get("x-api-key")
    if raw_key is None:
        caller = "none"
    else:
        caller = resolve_caller(raw_key) or "invalid"

    return f"{request.method} {path} | caller: {caller}"
