import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from shared.request_log import describe_request

logger = logging.getLogger("app")

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()
        summary = describe_request(request)

        try:
            response = await call_next(request)
        except Exception:
            duration = time.perf_counter() - start_time
            logger.exception(
                f"{summary} | "
                f"Status: 500 (unhandled) | "
                f"Latency: {duration:.4f}s"
            )
            raise

        duration = time.perf_counter() - start_time

        logger.info(
            f"{summary} | "
            f"Status: {response.status_code} | "
            f"Latency: {duration:.4f}s"
        )
        return response
