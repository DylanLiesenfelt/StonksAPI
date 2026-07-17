import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from shared.request_log import describe_request

logger = logging.getLogger("app")


class APIError(Exception):
    """Base for every error this API deliberately raises and translates to JSON."""
    status_code = 500
    code = "internal_error"

    def __init__(self, message: str | None = None):
        self.message = message or "An unexpected error occurred."
        super().__init__(self.message)


class InvalidAPIKeyError(APIError):
    status_code = 401
    code = "invalid_api_key"

    def __init__(self):
        super().__init__("Missing or invalid API key.")


class UpstreamError(APIError):
    """Base for failures talking to the upstream market-data provider (Massive)."""
    status_code = 502
    code = "upstream_error"

    def __init__(self, message: str | None = None, *, upstream_status: int | None = None):
        self.upstream_status = upstream_status
        super().__init__(message or "The upstream market data provider returned an unexpected error.")


class UpstreamBadRequestError(UpstreamError):
    """Massive 400/404 - in practice almost always an invalid/unknown ticker."""
    status_code = 400
    code = "invalid_request"

    def __init__(self, message: str | None = None, *, upstream_status: int | None = None):
        super().__init__(
            message or "The upstream provider rejected this request - check the ticker and query parameters.",
            upstream_status=upstream_status,
        )


class UpstreamAuthError(UpstreamError):
    """Massive 401/403 - our MASSIVE_KEY is missing/invalid/revoked. Mapped to 502,
    NOT 401/403: this is our server's fault, not the caller's."""
    status_code = 502
    code = "upstream_auth_error"


class UpstreamRateLimitedError(UpstreamError):
    """Massive 429 - passed through as 429, it's accurate for our clients too."""
    status_code = 429
    code = "upstream_rate_limited"


class UpstreamUnavailableError(UpstreamError):
    """Massive 5xx, or a non-timeout httpx.TransportError after retries exhausted."""
    status_code = 502
    code = "upstream_unavailable"


class UpstreamTimeoutError(UpstreamUnavailableError):
    """httpx.TimeoutException after retries exhausted."""
    status_code = 504
    code = "upstream_timeout"


class MalformedUpstreamPayloadError(UpstreamError):
    """Massive returned 2xx but the JSON body was missing an expected key."""
    status_code = 502
    code = "malformed_upstream_response"


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(APIError)
    async def handle_api_error(request: Request, exc: APIError):
        logger.warning(f"{describe_request(request)} | {exc.code}: {exc.message}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": exc.code, "message": exc.message}},
        )

    @app.exception_handler(Exception)
    async def handle_unhandled_exception(request: Request, exc: Exception):
        logger.exception(f"Unhandled exception on {describe_request(request)}")
        return JSONResponse(
            status_code=500,
            content={"error": {"code": "internal_error", "message": "An unexpected error occurred."}},
        )
