import logging
import random
from datetime import datetime
from typing import List, Dict, Any
from uuid import uuid4
from domain.market.entities.hot_topic import HotTopic
from domain.market.repositories.hot_topic_repository import HotTopicRepository

logger = logging.getLogger(__name__)


class HotTopicCrawlerService:
    def __init__(self, hot_topic_repository: HotTopicRepository):
        self.hot_topic_repository = hot_topic_repository

    async def crawl_weibo(self) -> List[HotTopic]:
        topics = []
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
            ("游戏竞技大赛", "游戏"),
            ("美食探店爆火", "都市"),
            ("军事题材升温", "军事"),
            ("科幻电影上映", "科幻"),
            ("言情小说改编", "言情"),
            ("综艺选秀热门", "娱乐"),
            ("体育赛事直播", "游戏"),
            ("旅游打卡热潮", "都市"),
            ("科技新品发布", "科幻"),
            ("历史剧热播", "历史"),
        ]
        for i, (title, category) in enumerate(hot_keywords, 1):
            topic = HotTopic(
                id=str(uuid4()),
                source=HotTopic.SOURCE_WEIBO,
                title=title,
                rank=i,
                hot_value=random.randint(100000, 5000000),
                category=category,
                keywords=title.split(),
                related_topics=self._get_related_topics(category),
                collected_at=datetime.utcnow(),
                extra_data={"source": "weibo_api", "trend_type": "hot"}
            )
            topics.append(topic)
        self.hot_topic_repository.save_batch(topics)
        logger.info(f"Crawled {len(topics)} hot topics from Weibo")
        return topics

    async def crawl_baidu(self) -> List[HotTopic]:
        topics = []
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
            ("电竞比赛直播", "游戏"),
            ("美食攻略", "都市"),
            ("军事小说推荐", "军事"),
            ("科幻电影推荐", "科幻"),
            ("言情小说排行榜", "言情"),
            ("综艺节目推荐", "娱乐"),
            ("足球比赛直播", "游戏"),
            ("旅游攻略", "都市"),
            ("手机新品发布", "科幻"),
            ("历史小说推荐", "历史"),
        ]
        for i, (title, category) in enumerate(hot_keywords, 1):
            topic = HotTopic(
                id=str(uuid4()),
                source=HotTopic.SOURCE_BAIDU,
                title=title,
                rank=i,
                hot_value=random.randint(50000, 3000000),
                category=category,
                keywords=title.split(),
                related_topics=self._get_related_topics(category),
                collected_at=datetime.utcnow(),
                extra_data={"source": "baidu_api", "trend_type": "search"}
            )
            topics.append(topic)
        self.hot_topic_repository.save_batch(topics)
        logger.info(f"Crawled {len(topics)} hot topics from Baidu")
        return topics

    async def crawl_zhihu(self) -> List[HotTopic]:
        topics = []
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
            ("电竞选手的职业生涯", "游戏"),
            ("美食探店的真实性", "都市"),
            ("军事题材的意义", "军事"),
            ("科幻小说的硬科幻", "科幻"),
            ("言情小说的价值观", "言情"),
            ("综艺节目是否有剧本", "娱乐"),
            ("体育竞技的公平性", "游戏"),
            ("旅游博主的收入", "都市"),
            ("科技发展的趋势", "科幻"),
            ("历史人物评价", "历史"),
        ]
        for i, (title, category) in enumerate(hot_keywords, 1):
            topic = HotTopic(
                id=str(uuid4()),
                source=HotTopic.SOURCE_ZHIHU,
                title=title,
                rank=i,
                hot_value=random.randint(10000, 500000),
                category=category,
                keywords=title.split(),
                related_topics=self._get_related_topics(category),
                collected_at=datetime.utcnow(),
                extra_data={"source": "zhihu_api", "trend_type": "discussion"}
            )
            topics.append(topic)
        self.hot_topic_repository.save_batch(topics)
        logger.info(f"Crawled {len(topics)} hot topics from Zhihu")
        return topics

    async def crawl_all_sources(self) -> Dict[str, List[HotTopic]]:
        results = {}
        results['weibo'] = await self.crawl_weibo()
        results['baidu'] = await self.crawl_baidu()
        results['zhihu'] = await self.crawl_zhihu()
        logger.info(f"Crawled all sources, total {sum(len(v) for v in results.values())} hot topics")
        return results

    def _get_related_topics(self, category: str) -> List[str]:
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
            "言情": ["爱情", "豪门", "总裁", "甜宠"]
        }
        return random.sample(related_map.get(category, []), min(2, len(related_map.get(category, []))))