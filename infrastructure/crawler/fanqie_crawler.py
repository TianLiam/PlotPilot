import logging
import json
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

            html = response.text
            
            import re
            data_match = re.search(r'window\.__INITIAL_STATE__\s*=\s*({.*?});', html, re.DOTALL)
            if not data_match:
                data_match = re.search(r'"data"\s*:\s*({.*?})', html, re.DOTALL)
            
            if data_match:
                try:
                    data_str = data_match.group(1)
                    data = json.loads(data_str)
                    
                    books = []
                    if isinstance(data, dict):
                        for key, value in data.items():
                            if isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
                                books = value
                                break
                            elif isinstance(value, dict) and 'rankingList' in value:
                                books = value['rankingList']
                                break
                    
                    if not books:
                        books = data.get('rankingList', [])
                    
                    for rank, book in enumerate(books[:limit], 1):
                        result = {
                            "platform": "fanqie",
                            "category": category,
                            "rank": rank,
                            "novel_name": self.clean_text(book.get("bookName") or book.get("name") or book.get("title")),
                            "author": self.clean_text(book.get("authorName") or book.get("author")),
                            "description": self.clean_text(book.get("intro") or book.get("description")),
                            "tags": ",".join(book.get("tags", [])),
                            "word_count": self.parse_int(book.get("wordCount") or book.get("word")),
                            "popularity": self.parse_int(book.get("totalRead") or book.get("readCount")),
                            "score": self.parse_float(book.get("score", 0)),
                            "comments": self.parse_int(book.get("commentCount") or book.get("comments")),
                            "favorites": self.parse_int(book.get("collectCount") or book.get("favorites")),
                            "collected_at": datetime.utcnow(),
                            "extra_data": {
                                "source": "fanqie_html",
                                "book_id": book.get("bookId") or book.get("id"),
                                "ranking_id": ranking_id,
                            },
                        }
                        results.append(result)

                    logger.info(f"Crawled {len(results)} novels from Fanqie category: {category}")
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse Fanqie JSON: {e}")
            else:
                logger.warning("Could not find data in Fanqie HTML")
            
            await self._delay()

        except Exception as e:
            logger.error(f"Failed to crawl Fanqie ranking for {category}: {e}")

        return results

    async def crawl_all_categories(self, limit: int = 20) -> List[Dict[str, Any]]:
        all_results = []
        for category in self.CATEGORIES.keys():
            results = await self.crawl_ranking(category, limit)
            all_results.extend(results)
        logger.info(f"Total crawled {len(all_results)} novels from Fanqie")
        return all_results
