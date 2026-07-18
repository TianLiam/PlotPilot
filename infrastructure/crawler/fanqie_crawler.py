import logging
import json
import re
from typing import List, Dict, Any
from datetime import datetime

from infrastructure.crawler.base_crawler import BaseCrawler

logger = logging.getLogger(__name__)


class FanqieCrawler(BaseCrawler):
    BASE_URL = "https://fanqienovel.com"
    
    CATEGORIES = {
        "都市": {"gender": 1, "rankMold": 2, "categoryId": 262},
        "玄幻": {"gender": 1, "rankMold": 2, "categoryId": 257},
        "仙侠": {"gender": 1, "rankMold": 2, "categoryId": 1140},
        "奇幻": {"gender": 1, "rankMold": 2, "categoryId": 1141},
        "历史": {"gender": 1, "rankMold": 2, "categoryId": 1142},
        "游戏": {"gender": 1, "rankMold": 2, "categoryId": 263},
        "科幻": {"gender": 1, "rankMold": 2, "categoryId": 8},
        "悬疑": {"gender": 1, "rankMold": 2, "categoryId": 264},
        "言情": {"gender": 0, "rankMold": 2, "categoryId": 265},
        "军事": {"gender": 1, "rankMold": 2, "categoryId": 266},
    }

    @staticmethod
    def _extract_initial_state(html: str) -> Dict[str, Any]:
        marker = "window.__INITIAL_STATE__="
        start = html.find(marker)
        if start < 0:
            return {}
        try:
            state, _ = json.JSONDecoder().raw_decode(html[start + len(marker):].lstrip())
            return state if isinstance(state, dict) else {}
        except json.JSONDecodeError:
            return {}

    @staticmethod
    def _contains_private_use(text: str) -> bool:
        return any(0xE000 <= ord(char) <= 0xF8FF for char in text or "")

    async def crawl_ranking(self, category: str, limit: int = 20) -> List[Dict[str, Any]]:
        results = []
        category_info = self.CATEGORIES.get(category)
        if not category_info:
            logger.warning(f"Unknown category: {category}")
            return results

        try:
            ranking_id = f"{category_info['gender']}_{category_info['rankMold']}_{category_info['categoryId']}"
            url = f"{self.BASE_URL}/rank/{ranking_id}"
            
            headers = self._get_default_headers(referer=self.BASE_URL)
            response = await self.safe_request("get", url, headers=headers)
            
            if response is None:
                return results

            html = response.content.decode("utf-8", errors="replace")
            state = self._extract_initial_state(html)
            rank_state = state.get("rank", {}) if isinstance(state, dict) else {}
            books = rank_state.get("book_list", []) if isinstance(rank_state, dict) else []

            if books:
                    for rank, book in enumerate(books[:limit], 1):
                        book_name = self.clean_text(book.get("bookName"))
                        author = self.clean_text(book.get("author"))
                        text_obfuscated = self._contains_private_use(book_name) or self._contains_private_use(author)
                        result = {
                            "platform": "fanqie",
                            "category": category,
                            "rank": rank,
                            "novel_name": book_name,
                            "author": author,
                            "description": self.clean_text(book.get("abstract")),
                            "tags": ",".join(book.get("tags", [])),
                            "word_count": self.parse_int(book.get("wordNumber")),
                            "popularity": self.parse_int(book.get("read_count") or book.get("readCount")),
                            "score": self.parse_float(book.get("score", 0)),
                            "comments": self.parse_int(book.get("commentCount") or book.get("comments")),
                            "favorites": self.parse_int(book.get("collectCount") or book.get("favorites")),
                            "collected_at": datetime.utcnow(),
                            "extra_data": {
                                "source": "fanqie_html",
                                "book_id": book.get("bookId"),
                                "ranking_id": ranking_id,
                                "rank_version": rank_state.get("rankVersion"),
                                "text_obfuscated": text_obfuscated,
                                "url": f"{self.BASE_URL}/page/{book.get('bookId')}" if book.get("bookId") else "",
                            },
                        }
                        results.append(result)

                    logger.info(f"Crawled {len(results)} novels from Fanqie category: {category}")
            else:
                self.last_error = "Fanqie page did not contain rank.book_list"
                logger.warning("Could not find data in Fanqie HTML")
            
            await self._delay()

        except Exception as e:
            self.last_error = f"{type(e).__name__}: {e}"
            logger.error(f"Failed to crawl Fanqie ranking for {category}: {e}")

        return results

    async def crawl_all_categories(self, limit: int = 20) -> List[Dict[str, Any]]:
        all_results = []
        for category in self.CATEGORIES.keys():
            results = await self.crawl_ranking(category, limit)
            all_results.extend(results)
            if results and all((item.get("extra_data") or {}).get("text_obfuscated") for item in results):
                self.last_error = (
                    "Fanqie returned dynamically font-obfuscated text; records were rejected "
                    "to prevent corrupted names from entering the database"
                )
                break
        logger.info(f"Total crawled {len(all_results)} novels from Fanqie")
        return all_results
