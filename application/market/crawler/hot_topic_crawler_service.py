import logging
from datetime import datetime
from typing import Any, Dict, List
from uuid import NAMESPACE_URL, uuid5

from domain.market.entities.hot_topic import HotTopic
from domain.market.repositories.hot_topic_repository import HotTopicRepository
from infrastructure.crawler import BaiduCrawler, WeiboCrawler, ZhihuCrawler

logger = logging.getLogger(__name__)


class HotTopicCrawlerService:
    """Fetch hot topics without manufacturing fallback records."""

    def __init__(self, hot_topic_repository: HotTopicRepository):
        self.hot_topic_repository = hot_topic_repository
        self.weibo_crawler = WeiboCrawler()
        self.baidu_crawler = BaiduCrawler()
        self.zhihu_crawler = ZhihuCrawler()
        self.last_errors: Dict[str, str] = {}

    async def _crawl(self, source: str, crawler: Any, default_category: str) -> List[HotTopic]:
        self.last_errors.pop(source, None)
        try:
            data = await crawler.crawl_hot_topics(limit=20)
            topics: List[HotTopic] = []
            seen = set()
            collected_at = datetime.utcnow()
            for item in data:
                title = str(item.get("title") or "").strip()
                rank = int(item.get("rank") or 0)
                if not title or rank <= 0 or (item.get("extra_data") or {}).get("source") == "fallback":
                    continue
                key = (source, title)
                if key in seen:
                    continue
                seen.add(key)
                category = self._map_category(str(item.get("category") or default_category))
                topics.append(
                    HotTopic(
                        id=str(uuid5(NAMESPACE_URL, f"hot-topic:{source}:{title}")),
                        source=source,
                        title=title,
                        rank=rank,
                        hot_value=int(item.get("hot_value") or 0),
                        category=category,
                        keywords=list(item.get("keywords") or []),
                        related_topics=self._get_related_topics(category),
                        collected_at=collected_at,
                        extra_data=dict(item.get("extra_data") or {}),
                    )
                )

            if not topics:
                self.last_errors[source] = getattr(crawler, "last_error", None) or "Crawler returned no valid hot topics"
                logger.warning("%s hot-topic crawl unavailable: %s", source, self.last_errors[source])
                return []

            self.hot_topic_repository.save_batch(topics)
            return topics
        except Exception as exc:
            self.last_errors[source] = f"{type(exc).__name__}: {exc}"
            logger.exception("Failed to crawl hot topics from %s", source)
            return []

    async def crawl_weibo(self) -> List[HotTopic]:
        return await self._crawl(HotTopic.SOURCE_WEIBO, self.weibo_crawler, "娱乐")

    async def crawl_baidu(self) -> List[HotTopic]:
        return await self._crawl(HotTopic.SOURCE_BAIDU, self.baidu_crawler, "娱乐")

    async def crawl_zhihu(self) -> List[HotTopic]:
        return await self._crawl(HotTopic.SOURCE_ZHIHU, self.zhihu_crawler, "讨论")

    async def crawl_all_sources(self) -> Dict[str, List[HotTopic]]:
        return {
            HotTopic.SOURCE_WEIBO: await self.crawl_weibo(),
            HotTopic.SOURCE_BAIDU: await self.crawl_baidu(),
            HotTopic.SOURCE_ZHIHU: await self.crawl_zhihu(),
        }

    def _map_category(self, category: str) -> str:
        category_map = {
            "游戏": "游戏", "娱乐": "娱乐", "都市": "都市", "玄幻": "玄幻",
            "历史": "历史", "科幻": "科幻", "悬疑": "悬疑", "仙侠": "仙侠",
            "军事": "军事", "言情": "言情", "讨论": "娱乐", "社会": "娱乐",
            "科技": "科幻", "财经": "都市", "体育": "游戏",
        }
        return category_map.get(category, "娱乐")

    @staticmethod
    def _get_related_topics(category: str) -> List[str]:
        related_map = {
            "游戏": ["电竞", "网游"], "娱乐": ["明星", "影视"],
            "都市": ["职场", "生活"], "玄幻": ["修仙", "奇幻"],
            "历史": ["穿越", "古代"], "科幻": ["末世", "星际"],
            "悬疑": ["推理", "破案"], "仙侠": ["修仙", "神话"],
            "军事": ["战争", "谍战"], "言情": ["爱情", "甜宠"],
        }
        return related_map.get(category, [])

    async def close(self) -> None:
        await self.weibo_crawler.close()
        await self.baidu_crawler.close()
        await self.zhihu_crawler.close()
