import asyncio
import logging
import random
import re
import time
from typing import Dict, Any, Optional, Tuple
from datetime import datetime

import httpx

logger = logging.getLogger(__name__)


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/121.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]


class BaseCrawler:
    def __init__(self, timeout: int = 10, delay_range: Tuple[float, float] = (0.5, 1.0)):
        self.timeout = timeout
        self.delay_range = delay_range
        self._client: Optional[httpx.AsyncClient] = None
        self.last_error: Optional[str] = None

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=self.timeout,
                follow_redirects=True,
                limits=httpx.Limits(max_connections=10, max_keepalive_connections=5),
            )
        return self._client

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None

    def _get_random_user_agent(self) -> str:
        return random.choice(USER_AGENTS)

    def _get_default_headers(self, referer: str = "") -> Dict[str, str]:
        headers = {
            "User-Agent": self._get_random_user_agent(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Cache-Control": "max-age=0",
        }
        if referer:
            headers["Referer"] = referer
        return headers

    async def _delay(self):
        delay = random.uniform(*self.delay_range)
        await asyncio.sleep(delay)

    async def get(self, url: str, headers: Optional[Dict[str, str]] = None, **kwargs) -> httpx.Response:
        if headers is None:
            headers = self._get_default_headers()
        else:
            headers = {**self._get_default_headers(), **headers}

        try:
            response = await self.client.get(url, headers=headers, **kwargs)
            response.raise_for_status()
            return response
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code} for {url}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error for {url}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error for {url}: {e}")
            raise

    async def post(self, url: str, data: Optional[Dict[str, Any]] = None, 
                   headers: Optional[Dict[str, str]] = None, **kwargs) -> httpx.Response:
        if headers is None:
            headers = self._get_default_headers()
        else:
            headers = {**self._get_default_headers(), **headers}

        try:
            response = await self.client.post(url, data=data, headers=headers, **kwargs)
            response.raise_for_status()
            return response
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code} for {url}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error for {url}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error for {url}: {e}")
            raise

    async def safe_request(self, method: str, url: str, max_retries: int = 1, **kwargs) -> Optional[httpx.Response]:
        self.last_error = None
        for attempt in range(max_retries):
            try:
                if method.lower() == 'get':
                    return await self.get(url, **kwargs)
                elif method.lower() == 'post':
                    return await self.post(url, **kwargs)
                else:
                    raise ValueError(f"Unsupported method: {method}")
            except httpx.HTTPStatusError as e:
                logger.warning(f"HTTP error {e.response.status_code} for {url}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(1)
                else:
                    self.last_error = f"HTTP {e.response.status_code}: {url}"
                    return None
            except Exception as e:
                logger.warning(f"Request attempt {attempt + 1} failed for {url}: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(1)
                else:
                    logger.error(f"All {max_retries} attempts failed for {url}")
                    self.last_error = f"{type(e).__name__}: {e}"
                    return None

    def parse_int(self, value: Any, default: int = 0) -> int:
        if value is None:
            return default

        text = str(value).replace(',', '').strip()
        match = re.search(r"-?\d+(?:\.\d+)?", text)
        if not match:
            return default

        multiplier = 100_000_000 if "亿" in text else (10_000 if "万" in text else 1)
        try:
            return int(float(match.group(0)) * multiplier)
        except (ValueError, TypeError, OverflowError):
            return default

    def parse_float(self, value: Any, default: float = 0.0) -> float:
        try:
            return float(str(value).replace(',', ''))
        except (ValueError, TypeError):
            return default

    def clean_text(self, text: Any) -> str:
        if text is None:
            return ""
        return str(text).strip().replace('\n', '').replace('\r', '').replace('\t', '')
