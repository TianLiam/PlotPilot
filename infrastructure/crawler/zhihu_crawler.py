import logging
import json
from typing import List, Dict, Any
from datetime import datetime

from infrastructure.crawler.base_crawler import BaseCrawler

logger = logging.getLogger(__name__)


class ZhihuCrawler(BaseCrawler):
    BASE_URL = "https://www.zhihu.com"
    HOT_TOPICS_API = "https://www.zhihu.com/api/v3/feed/topstory/hot-list"

    async def crawl_hot_topics(self, limit: int = 20) -> List[Dict[str, Any]]:
        results = []
        
        try:
            params = {
                "limit": limit,
                "desktop": True,
            }

            headers = self._get_default_headers(referer=self.BASE_URL)
            response = await self.safe_request("get", self.HOT_TOPICS_API, params=params, headers=headers)
            
            if response is None:
                return results

            data = response.json()
            
            if not data.get("data"):
                logger.warning(f"Zhihu API returned empty data: {data}")
                return results

            hot_list = data["data"]
            
            for item in hot_list[:limit]:
                target = item.get("target", {})
                result = {
                    "source": "zhihu",
                    "title": self.clean_text(target.get("title")),
                    "rank": self.parse_int(item.get("rankIndex")),
                    "hot_value": self.parse_int(item.get("detailText", "0").replace("万", "0000")),
                    "category": self.clean_text(target.get("type", "讨论")),
                    "keywords": [self.clean_text(target.get("title"))],
                    "related_topics": [],
                    "collected_at": datetime.utcnow(),
                    "extra_data": {
                        "source": "zhihu_api",
                        "url": f"{self.BASE_URL}/question/{target.get('id')}",
                        "answer_count": self.parse_int(target.get("answerCount")),
                        "follower_count": self.parse_int(target.get("followerCount")),
                    },
                }
                results.append(result)

            logger.info(f"Crawled {len(results)} hot topics from Zhihu")
            await self._delay()

        except Exception as e:
            logger.error(f"Failed to crawl Zhihu hot topics: {e}")

        return results