import logging
import json
from typing import List, Dict, Any
from datetime import datetime

from infrastructure.crawler.base_crawler import BaseCrawler

logger = logging.getLogger(__name__)


class QidianCrawler(BaseCrawler):
    BASE_URL = "https://www.qidian.com"
    RANKING_API = "https://api.qidian.com/api/rank/h5"

    CATEGORIES = {
        "玄幻": {"type": 1, "subType": 1},
        "奇幻": {"type": 1, "subType": 2},
        "武侠": {"type": 2, "subType": 1},
        "仙侠": {"type": 2, "subType": 2},
        "都市": {"type": 4, "subType": 1},
        "历史": {"type": 5, "subType": 1},
        "游戏": {"type": 6, "subType": 1},
        "科幻": {"type": 7, "subType": 1},
        "悬疑": {"type": 8, "subType": 1},
        "军事": {"type": 9, "subType": 1},
    }

    async def crawl_ranking(self, category: str, limit: int = 20) -> List[Dict[str, Any]]:
        results = []
        category_info = self.CATEGORIES.get(category)
        if not category_info:
            logger.warning(f"Unknown category: {category}")
            return results

        try:
            params = {
                "type": category_info["type"],
                "subType": category_info["subType"],
                "pageNum": 1,
                "pageSize": limit,
            }

            headers = self._get_default_headers(referer=self.BASE_URL)
            response = await self.safe_request("get", self.RANKING_API, params=params, headers=headers)
            
            if response is None:
                return results

            data = response.json()
            
            if data.get("code") != 0 or not data.get("data"):
                logger.warning(f"Qidian API returned error: {data}")
                return results

            books = data["data"].get("books", [])
            for rank, book in enumerate(books, 1):
                result = {
                    "platform": "qidian",
                    "category": category,
                    "rank": rank,
                    "novel_name": self.clean_text(book.get("name")),
                    "author": self.clean_text(book.get("author")),
                    "description": self.clean_text(book.get("shortIntro")),
                    "tags": ",".join(book.get("tags", [])),
                    "word_count": self.parse_int(book.get("wordCount")),
                    "popularity": self.parse_int(book.get("totalClick")),
                    "score": self.parse_float(book.get("rating", {}).get("score", 0)),
                    "comments": self.parse_int(book.get("totalRecommend")),
                    "favorites": self.parse_int(book.get("collectCount")),
                    "collected_at": datetime.utcnow(),
                    "extra_data": {
                        "source": "qidian_api",
                        "book_id": book.get("bookId"),
                        "url": f"{self.BASE_URL}/book/{book.get('bookId')}",
                    },
                }
                results.append(result)

            logger.info(f"Crawled {len(results)} novels from Qidian category: {category}")
            await self._delay()

        except Exception as e:
            logger.error(f"Failed to crawl Qidian ranking for {category}: {e}")

        return results

    async def crawl_all_categories(self, limit: int = 20) -> List[Dict[str, Any]]:
        all_results = []
        for category in self.CATEGORIES.keys():
            results = await self.crawl_ranking(category, limit)
            all_results.extend(results)
        logger.info(f"Total crawled {len(all_results)} novels from Qidian")
        return all_results