import logging
import json
from typing import List, Dict, Any
from datetime import datetime

from infrastructure.crawler.base_crawler import BaseCrawler

logger = logging.getLogger(__name__)


class WeiboCrawler(BaseCrawler):
    BASE_URL = "https://s.weibo.com"
    HOT_TOPICS_API = "https://s.weibo.com/top/summary"

    async def crawl_hot_topics(self, limit: int = 20) -> List[Dict[str, Any]]:
        results = []
        
        try:
            headers = self._get_default_headers(referer=self.BASE_URL)
            response = await self.safe_request("get", self.HOT_TOPICS_API, headers=headers)
            
            if response is None:
                return results

            import re
            
            html_content = response.text
            
            match = re.search(r'var _render_data = (\[.*?\]);', html_content)
            if not match:
                logger.warning("Failed to find Weibo hot topics data")
                return results

            try:
                data = json.loads(match.group(1))
                hot_list = data[0].get("data", {}).get("hotList", [])
                
                for item in hot_list[:limit]:
                    result = {
                        "source": "weibo",
                        "title": self.clean_text(item.get("word")),
                        "rank": self.parse_int(item.get("rank")),
                        "hot_value": self.parse_int(item.get("hot")),
                        "category": self.clean_text(item.get("category", "娱乐")),
                        "keywords": [self.clean_text(item.get("word"))],
                        "related_topics": [],
                        "collected_at": datetime.utcnow(),
                        "extra_data": {
                            "source": "weibo_web",
                            "url": f"{self.BASE_URL}/weibo?q={item.get('word')}",
                            "topic_id": item.get("topicid"),
                        },
                    }
                    results.append(result)

                logger.info(f"Crawled {len(results)} hot topics from Weibo")
                
            except (json.JSONDecodeError, IndexError) as e:
                logger.error(f"Failed to parse Weibo hot topics: {e}")

            await self._delay()

        except Exception as e:
            logger.error(f"Failed to crawl Weibo hot topics: {e}")

        return results