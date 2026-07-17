import httpx, asyncio

from shared.config import MASSIVE_KEY
from shared.error_handler import (
    UpstreamBadRequestError,
    UpstreamAuthError,
    UpstreamRateLimitedError,
    UpstreamUnavailableError,
    UpstreamTimeoutError,
    UpstreamError,
)

class Client:
    def __init__(self):
        self._client = httpx.AsyncClient(timeout=3)

    async def fetch(self, url: str, retries: int = 2) -> dict:
        for attempt in range(retries + 1):
            try:
                r = await self._client.get(url)
                r.raise_for_status()
                result = r.json()
                if "next_url" in result:
                    # Polygon's next_url omits the key; the initial request appended it, so continuation must too
                    next_url = result["next_url"] + "&apiKey=" + MASSIVE_KEY
                    fetched = await self.fetch(next_url)
                    if fetched:
                        result["results"] += fetched["results"]
                return result
            except httpx.HTTPStatusError as e:
                status = e.response.status_code
                if status in (400, 404):
                    # Massive returns 400 for some bad-request cases and 404 ("Ticker not found")
                    # for others (e.g. v3/reference/tickers/{ticker}) - both mean the same thing
                    # to our callers: the request itself was invalid.
                    raise UpstreamBadRequestError(upstream_status=status) from e
                if status in (401, 403):
                    raise UpstreamAuthError(upstream_status=status) from e
                if status == 429:
                    raise UpstreamRateLimitedError(upstream_status=status) from e
                if status >= 500:
                    raise UpstreamUnavailableError(upstream_status=status) from e
                raise UpstreamError(upstream_status=status) from e
            except httpx.TimeoutException as e:
                if attempt == retries:
                    raise UpstreamTimeoutError() from e
                await asyncio.sleep(1)
            except httpx.TransportError as e:
                if attempt == retries:
                    raise UpstreamUnavailableError() from e
                await asyncio.sleep(1)

    async def close(self):
        await self._client.aclose()
