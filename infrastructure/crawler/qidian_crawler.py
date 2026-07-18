import logging
import re
from typing import List, Dict, Any
from datetime import datetime

from infrastructure.crawler.base_crawler import BaseCrawler

logger = logging.getLogger(__name__)


class QidianCrawler(BaseCrawler):
    BASE_URL = "https://m.qidian.com"
    RANKING_PAGE = f"{BASE_URL}/rank/yuepiao/"
    RANKING_API = f"{BASE_URL}/majax/rank/yuepiaolist"
    MOBILE_USER_AGENT = (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
    )

    CATEGORIES = {
        "玄幻": 21,
        "奇幻": 1,
        "武侠": 2,
        "仙侠": 22,
        "都市": 4,
        "历史": 5,
        "游戏": 7,
        "科幻": 9,
        "悬疑": 10,
        "军事": 6,
    }

    async def _ensure_csrf_token(self) -> str:
        existing = self.client.cookies.get("_csrfToken") or ""
        if existing:
            return existing
        headers = self._get_default_headers(referer=self.BASE_URL)
        headers["User-Agent"] = self.MOBILE_USER_AGENT
        response = await self.safe_request("get", self.RANKING_PAGE, headers=headers, max_retries=2)
        if response is None:
            return ""
        token = response.cookies.get("_csrfToken") or self.client.cookies.get("_csrfToken") or ""
        if not token:
            set_cookie = response.headers.get("set-cookie", "")
            match = re.search(r"(?:^|[,;]\s*)_csrfToken=([^;,]+)", set_cookie)
            token = match.group(1) if match else ""
        if not token:
            self.last_error = "Qidian ranking page did not issue a CSRF token"
        return token

    async def crawl_ranking(self, category: str, limit: int = 20) -> List[Dict[str, Any]]:
        results = []
        category_id = self.CATEGORIES.get(category)
        if not category_id:
            logger.warning(f"Unknown category: {category}")
            return results

        try:
            token = await self._ensure_csrf_token()
            if not token:
                return results

            headers = self._get_default_headers(referer=self.RANKING_PAGE)
            headers["User-Agent"] = self.MOBILE_USER_AGENT
            page_num = 1
            while len(results) < limit:
                params = {
                    "gender": "male",
                    "catId": category_id,
                    "pageNum": page_num,
                    "_csrfToken": token,
                }
                response = await self.safe_request(
                    "get", self.RANKING_API, params=params, headers=headers, max_retries=2
                )
                if response is None:
                    break

                data = response.json()
                if data.get("code") != 0 or not isinstance(data.get("data"), dict):
                    self.last_error = f"Qidian API error: {data.get('msg', 'unknown error')}"
                    logger.warning(self.last_error)
                    break

                books = data["data"].get("records", [])
                if not books:
                    break

                for book in books:
                    book_id = str(book.get("bid") or "")
                    actual_category = self.clean_text(book.get("cat")) or category
                    result = {
                        "platform": "qidian",
                        "category": actual_category,
                        "rank": self.parse_int(book.get("rankNum"), len(results) + 1),
                        "novel_name": self.clean_text(book.get("bName")),
                        "author": self.clean_text(book.get("bAuth")),
                        "description": self.clean_text(book.get("desc")),
                        "tags": ",".join(filter(None, [actual_category, self.clean_text(book.get("subCat"))])),
                        "word_count": self.parse_int(book.get("cnt")),
                        "popularity": self.parse_int(book.get("rankCnt")),
                        "score": 0.0,
                        "comments": 0,
                        "favorites": 0,
                        "collected_at": datetime.utcnow(),
                        "extra_data": {
                            "source": "qidian_mobile_api",
                            "book_id": book_id,
                            "category_id": book.get("catId"),
                            "subcategory_id": book.get("subCatId"),
                            "ranking_metric": "monthly_tickets",
                            "url": f"{self.BASE_URL}/book/{book_id}.html" if book_id else "",
                        },
                    }
                    results.append(result)
                    if len(results) >= limit:
                        break

                if data["data"].get("isLast") or len(books) == 0:
                    break
                page_num += 1

            logger.info(f"Crawled {len(results)} novels from Qidian category: {category}")
            await self._delay()

        except Exception as e:
            self.last_error = f"{type(e).__name__}: {e}"
            logger.error(f"Failed to crawl Qidian ranking for {category}: {e}")

        return results

    async def crawl_all_categories(self, limit: int = 20) -> List[Dict[str, Any]]:
        all_results = []
        for category in self.CATEGORIES.keys():
            results = await self.crawl_ranking(category, limit)
            all_results.extend(results)
        logger.info(f"Total crawled {len(all_results)} novels from Qidian")
        return all_results
