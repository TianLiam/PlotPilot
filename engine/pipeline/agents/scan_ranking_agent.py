"""Agent1: 扫榜Agent - 爬取各大平台榜单"""
import logging
from typing import Dict, Any
from datetime import datetime

from engine.pipeline.agents.base_agent import BaseAgent
from engine.pipeline.entities.pipeline_entities import AgentType
from infrastructure.crawler.ranking_crawler import RankingCrawler
from infrastructure.crawler.hot_topic_crawler import HotTopicCrawler

logger = logging.getLogger(__name__)


class ScanRankingAgent(BaseAgent):
    """扫榜Agent
    
    爬取起点、番茄、七猫等平台的排行榜数据，
    以及微博、百度、知乎的热点话题。
    """
    
    agent_type = AgentType.SCAN_RANKING
    
    def __init__(self, llm_client=None):
        super().__init__(llm_client)
        self.ranking_crawler = RankingCrawler()
        self.hot_topic_crawler = HotTopicCrawler()
    
    async def execute(self, context: PipelineContext) -> Dict[str, Any]:
        """执行扫榜"""
        user_request = context.user_request
        platforms = user_request.get("platforms", ["fanqie", "qidian"])
        
        result = {
            "platforms": platforms,
            "rankings": {},
            "hot_topics": {},
            "collected_at": datetime.utcnow().isoformat(),
        }
        
        # 爬取榜单
        for platform in platforms:
            try:
                if platform == "fanqie":
                    data = await self.ranking_crawler.crawl_fanqie_rankings()
                elif platform == "qidian":
                    data = await self.ranking_crawler.crawl_qidian_rankings()
                elif platform == "qimao":
                    data = await self.ranking_crawler.crawl_qimao_rankings()
                else:
                    continue
                
                result["rankings"][platform] = data
                logger.info(f"Crawled {platform} rankings: {len(data)} novels")
                
            except Exception as e:
                logger.error(f"Failed to crawl {platform}: {e}")
                result["rankings"][platform] = []
        
        # 爬取热点
        try:
            hot_topics = await self.hot_topic_crawler.crawl_all_sources()
            result["hot_topics"] = hot_topics
            logger.info(f"Crawled hot topics from {len(hot_topics)} sources")
        except Exception as e:
            logger.error(f"Failed to crawl hot topics: {e}")
            result["hot_topics"] = {}
        
        return result