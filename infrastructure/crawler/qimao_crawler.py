import logging
import json
from typing import List, Dict, Any
from datetime import datetime

from infrastructure.crawler.base_crawler import BaseCrawler

logger = logging.getLogger(__name__)


class QimaoCrawler(BaseCrawler):
    BASE_URL = "https://www.qimao.com"
    RANKING_API = "https://www.qimao.com/api/rank/list"

    CATEGORIES = {
        "都市": {"cat_id": 1},
        "玄幻": {"cat_id": 2},
        "仙侠": {"cat_id": 3},
        "奇幻": {"cat_id": 4},
        "历史": {"cat_id": 5},
        "游戏": {"cat_id": 6},
        "科幻": {"cat_id": 7},
        "悬疑": {"cat_id": 8},
        "言情": {"cat_id": 9},
        "军事": {"cat_id": 10},
    }

    async def crawl_ranking(self, category: str, limit: int = 20) -> List[Dict[str, Any]]:
        results = []
        category_info = self.CATEGORIES.get(category)
        if not category_info:
            logger.warning(f"Unknown category: {category}")
            return results

        try:
            params = {
                "cat_id": category_info["cat_id"],
                "page": 1,
                "page_size": limit,
            }

            headers = self._get_default_headers(referer=self.BASE_URL)
            response = await self.safe_request("get", self.RANKING_API, params=params, headers=headers)
            
            if response is None:
                return results

            data = response.json()
            
            if data.get("code") != 200 or not data.get("data"):
                logger.warning(f"Qimao API returned error: {data}")
                return results

            books = data["data"].get("list", [])
            for rank, book in enumerate(books, 1):
                result = {
                    "platform": "qimao",
                    "category": category,
                    "rank": rank,
                    "novel_name": self.clean_text(book.get("book_name")),
                    "author": self.clean_text(book.get("author_name")),
                    "description": self.clean_text(book.get("intro")),
                    "tags": ",".join(book.get("tags", [])),
                    "word_count": self.parse_int(book.get("word_count")),
                    "popularity": self.parse_int(book.get("hot_value")),
                    "score": self.parse_float(book.get("score", 0)),
                    "comments": self.parse_int(book.get("comment_count")),
                    "favorites": self.parse_int(book.get("collect_count")),
                    "collected_at": datetime.utcnow(),
                    "extra_data": {
                        "source": "qimao_api",
                        "book_id": book.get("book_id"),
                        "url": f"{self.BASE_URL}/book/{book.get('book_id')}",
                    },
                }
                results.append(result)

            logger.info(f"Crawled {len(results)} novels from Qimao category: {category}")
            await self._delay()

        except Exception as e:
            logger.error(f"Failed to crawl Qimao ranking for {category}: {e}")

        return results

    async def crawl_all_categories(self, limit: int = 20) -> List[Dict[str, Any]]:
        all_results = []
        for category in self.CATEGORIES.keys():
            results = await self.crawl_ranking(category, limit)
            all_results.extend(results)
        logger.info(f"Total crawled {len(all_results)} novels from Qimao")
        return all_results