import logging
import json
from typing import List, Dict, Any
from datetime import datetime

from infrastructure.crawler.base_crawler import BaseCrawler

logger = logging.getLogger(__name__)


class BaiduCrawler(BaseCrawler):
    BASE_URL = "https://www.baidu.com"
    HOT_TOPICS_API = "https://top.baidu.com/api/board"

    async def crawl_hot_topics(self, limit: int = 20) -> List[Dict[str, Any]]:
        results = []
        
        try:
            params = {
                "tab": "realtime",
            }

            headers = self._get_default_headers(referer=self.BASE_URL)
            response = await self.safe_request("get", self.HOT_TOPICS_API, params=params, headers=headers)
            
            if response is None:
                return results

            data = response.json()
            
            if data.get("code") != 0 or not data.get("data"):
                logger.warning(f"Baidu API returned error: {data}")
                return results

            hot_list = data["data"].get("cards", [])
            
            for item in hot_list[:limit]:
                result = {
                    "source": "baidu",
                    "title": self.clean_text(item.get("word")),
                    "rank": self.parse_int(item.get("index")),
                    "hot_value": self.parse_int(item.get("hotScore")),
                    "category": self.clean_text(item.get("category", "娱乐")),
                    "keywords": [self.clean_text(item.get("word"))],
                    "related_topics": [],
                    "collected_at": datetime.utcnow(),
                    "extra_data": {
                        "source": "baidu_api",
                        "url": f"https://www.baidu.com/s?wd={item.get('word')}",
                        "desc": self.clean_text(item.get("desc")),
                    },
                }
                results.append(result)

            logger.info(f"Crawled {len(results)} hot topics from Baidu")
            await self._delay()

        except Exception as e:
            logger.error(f"Failed to crawl Baidu hot topics: {e}")

        return results