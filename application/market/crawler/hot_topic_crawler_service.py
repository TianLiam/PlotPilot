import logging
from datetime import datetime
from typing import List, Dict, Any
from uuid import uuid4
from domain.market.entities.hot_topic import HotTopic
from domain.market.repositories.hot_topic_repository import HotTopicRepository
from infrastructure.crawler import WeiboCrawler, BaiduCrawler, ZhihuCrawler

logger = logging.getLogger(__name__)


class HotTopicCrawlerService:
    def __init__(self, hot_topic_repository: HotTopicRepository):
        self.hot_topic_repository = hot_topic_repository
        self.weibo_crawler = WeiboCrawler()
        self.baidu_crawler = BaiduCrawler()
        self.zhihu_crawler = ZhihuCrawler()

    async def crawl_weibo(self) -> List[HotTopic]:
        topics = []
        try:
            data = await self.weibo_crawler.crawl_hot_topics(limit=20)
            
            for item in data:
                topic = HotTopic(
                    id=str(uuid4()),
                    source=HotTopic.SOURCE_WEIBO,
                    title=item.get("title", ""),
                    rank=item.get("rank", 0),
                    hot_value=item.get("hot_value", 0),
                    category=self._map_category(item.get("category", "娱乐")),
                    keywords=item.get("keywords", []),
                    related_topics=self._get_related_topics(item.get("category", "娱乐")),
                    collected_at=datetime.utcnow(),
                    extra_data=item.get("extra_data", {})
                )
                topics.append(topic)
            
            if topics:
                self.hot_topic_repository.save_batch(topics)
                logger.info(f"Crawled {len(topics)} real hot topics from Weibo")
            else:
                logger.warning("Weibo crawler returned empty data, using fallback")
                topics = self._generate_fallback_topics(HotTopic.SOURCE_WEIBO)
                self.hot_topic_repository.save_batch(topics)
                
        except Exception as e:
            logger.error(f"Failed to crawl Weibo: {e}, using fallback")
            topics = self._generate_fallback_topics(HotTopic.SOURCE_WEIBO)
            self.hot_topic_repository.save_batch(topics)
        
        return topics

    async def crawl_baidu(self) -> List[HotTopic]:
        topics = []
        try:
            data = await self.baidu_crawler.crawl_hot_topics(limit=20)
            
            for item in data:
                topic = HotTopic(
                    id=str(uuid4()),
                    source=HotTopic.SOURCE_BAIDU,
                    title=item.get("title", ""),
                    rank=item.get("rank", 0),
                    hot_value=item.get("hot_value", 0),
                    category=self._map_category(item.get("category", "娱乐")),
                    keywords=item.get("keywords", []),
                    related_topics=self._get_related_topics(item.get("category", "娱乐")),
                    collected_at=datetime.utcnow(),
                    extra_data=item.get("extra_data", {})
                )
                topics.append(topic)
            
            if topics:
                self.hot_topic_repository.save_batch(topics)
                logger.info(f"Crawled {len(topics)} real hot topics from Baidu")
            else:
                logger.warning("Baidu crawler returned empty data, using fallback")
                topics = self._generate_fallback_topics(HotTopic.SOURCE_BAIDU)
                self.hot_topic_repository.save_batch(topics)
                
        except Exception as e:
            logger.error(f"Failed to crawl Baidu: {e}, using fallback")
            topics = self._generate_fallback_topics(HotTopic.SOURCE_BAIDU)
            self.hot_topic_repository.save_batch(topics)
        
        return topics

    async def crawl_zhihu(self) -> List[HotTopic]:
        topics = []
        try:
            data = await self.zhihu_crawler.crawl_hot_topics(limit=20)
            
            for item in data:
                topic = HotTopic(
                    id=str(uuid4()),
                    source=HotTopic.SOURCE_ZHIHU,
                    title=item.get("title", ""),
                    rank=item.get("rank", 0),
                    hot_value=item.get("hot_value", 0),
                    category=self._map_category(item.get("category", "讨论")),
                    keywords=item.get("keywords", []),
                    related_topics=self._get_related_topics(item.get("category", "讨论")),
                    collected_at=datetime.utcnow(),
                    extra_data=item.get("extra_data", {})
                )
                topics.append(topic)
            
            if topics:
                self.hot_topic_repository.save_batch(topics)
                logger.info(f"Crawled {len(topics)} real hot topics from Zhihu")
            else:
                logger.warning("Zhihu crawler returned empty data, using fallback")
                topics = self._generate_fallback_topics(HotTopic.SOURCE_ZHIHU)
                self.hot_topic_repository.save_batch(topics)
                
        except Exception as e:
            logger.error(f"Failed to crawl Zhihu: {e}, using fallback")
            topics = self._generate_fallback_topics(HotTopic.SOURCE_ZHIHU)
            self.hot_topic_repository.save_batch(topics)
        
        return topics

    async def crawl_all_sources(self) -> Dict[str, List[HotTopic]]:
        results = {}
        results['weibo'] = await self.crawl_weibo()
        results['baidu'] = await self.crawl_baidu()
        results['zhihu'] = await self.crawl_zhihu()
        logger.info(f"Crawled all sources, total {sum(len(v) for v in results.values())} hot topics")
        return results

    def _map_category(self, category: str) -> str:
        category_map = {
            "游戏": "游戏",
            "娱乐": "娱乐",
            "都市": "都市",
            "玄幻": "玄幻",
            "历史": "历史",
            "科幻": "科幻",
            "悬疑": "悬疑",
            "仙侠": "仙侠",
            "军事": "军事",
            "言情": "言情",
            "讨论": "娱乐",
            "社会": "娱乐",
            "科技": "科幻",
            "财经": "都市",
            "体育": "游戏",
        }
        return category_map.get(category, "娱乐")

    def _get_related_topics(self, category: str) -> List[str]:
        import random
        related_map = {
            "游戏": ["电竞", "网游", "手游", "直播"],
            "娱乐": ["明星", "综艺", "影视", "音乐"],
            "都市": ["职场", "创业", "生活", "美食"],
            "玄幻": ["修仙", "奇幻", "武侠", "仙侠"],
            "历史": ["穿越", "古代", "争霸", "文化"],
            "科幻": ["末世", "星际", "未来", "科技"],
            "悬疑": ["推理", "破案", "惊悚", "恐怖"],
            "仙侠": ["修仙", "玄幻", "武侠", "神话"],
            "军事": ["战争", "谍战", "特种兵", "历史"],
            "言情": ["爱情", "豪门", "总裁", "甜宠"],
            "讨论": ["明星", "综艺", "影视", "音乐"],
        }
        return random.sample(related_map.get(category, []), min(2, len(related_map.get(category, []))))

    def _generate_fallback_topics(self, source: str) -> List[HotTopic]:
        import random
        topics = []
        
        if source == HotTopic.SOURCE_WEIBO:
            hot_keywords = [
                ("全民转职热潮来袭", "游戏"),
                ("直播带货新模式", "娱乐"),
                ("神豪系统火爆全网", "都市"),
                ("高武世界崛起", "玄幻"),
                ("娱乐圈明星转型", "娱乐"),
                ("都市重生逆袭", "都市"),
                ("穿越古代种田", "历史"),
                ("末世生存指南", "科幻"),
                ("悬疑推理新剧", "悬疑"),
                ("仙侠剧火热开播", "仙侠"),
            ]
            hot_value_range = (100000, 5000000)
        elif source == HotTopic.SOURCE_BAIDU:
            hot_keywords = [
                ("全民转职游戏", "游戏"),
                ("直播带货技巧", "娱乐"),
                ("神豪小说推荐", "都市"),
                ("高武世界小说", "玄幻"),
                ("娱乐圈最新消息", "娱乐"),
                ("都市重生小说", "都市"),
                ("穿越古代小说", "历史"),
                ("末世小说推荐", "科幻"),
                ("悬疑电视剧", "悬疑"),
                ("仙侠小说排行榜", "仙侠"),
            ]
            hot_value_range = (50000, 3000000)
        else:
            hot_keywords = [
                ("为什么全民转职小说这么火", "游戏"),
                ("直播行业的未来发展", "娱乐"),
                ("神豪小说为什么受欢迎", "都市"),
                ("高武世界设定分析", "玄幻"),
                ("娱乐圈乱象治理", "娱乐"),
                ("都市重生文的套路", "都市"),
                ("穿越到古代怎么生存", "历史"),
                ("末世生存的可能性", "科幻"),
                ("悬疑小说的写作技巧", "悬疑"),
                ("仙侠小说的世界观", "仙侠"),
            ]
            hot_value_range = (10000, 500000)
        
        for i, (title, category) in enumerate(hot_keywords, 1):
            topics.append(HotTopic(
                id=str(uuid4()),
                source=source,
                title=title,
                rank=i,
                hot_value=random.randint(*hot_value_range),
                category=category,
                keywords=title.split(),
                related_topics=self._get_related_topics(category),
                collected_at=datetime.utcnow(),
                extra_data={"source": "fallback", "trend_type": "hot"}
            ))
        
        logger.info(f"Generated {len(topics)} fallback hot topics for {source}")
        return topics