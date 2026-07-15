import httpx, asyncio

from shared.config import MASSIVE_KEY

class Client:
    def __init__(self):
        self._client = httpx.AsyncClient(timeout=3)

    async def fetch(self, url: str, retries: int = 2) -> dict | None:
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
            except httpx.TransportError:         
                if attempt == retries:
                    raise
                await asyncio.sleep(1)

    async def close(self):
        await self._client.aclose()
