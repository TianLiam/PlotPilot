"""Agent2: 趋势分析Agent - 分析榜单趋势"""
import logging
from typing import Dict, Any

from engine.pipeline.agents.base_agent import BaseAgent
from engine.pipeline.entities.pipeline_entities import AgentType

logger = logging.getLogger(__name__)


class TrendAnalysisAgent(BaseAgent):
    """趋势分析Agent
    
    基于扫榜数据分析题材趋势、发现机会。
    """
    
    agent_type = AgentType.TREND_ANALYSIS
    
    def get_required_inputs(self) -> list:
        return [AgentType.SCAN_RANKING]
    
    async def execute(self, context: PipelineContext) -> Dict[str, Any]:
        """执行趋势分析"""
        scan_result = context.scan_result
        
        # 构建分析提示词
        prompt = self._build_prompt(scan_result)
        
        # 调用LLM分析
        response = await self.generate(prompt, max_tokens=3000, temperature=0.5)
        
        # 解析结果
        result = self.parse_json_response(response)
        
        # 确保必要字段存在
        result.setdefault("rising_genres", [])
        result.setdefault("declining_genres", [])
        result.setdefault("opportunities", [])
        result.setdefault("alerts", [])
        result.setdefault("summary", "")
        
        return result
    
    def _build_prompt(self, scan_result: Dict[str, Any]) -> str:
        """构建趋势分析提示词"""
        rankings = scan_result.get("rankings", {})
        hot_topics = scan_result.get("hot_topics", {})
        
        # 提取热门题材
        all_genres = []
        for platform, novels in rankings.items():
            for novel in novels[:30]:
                category = novel.get("category") or novel.get("categoryName", "")
                if category:
                    all_genres.append(category)
        
        genre_str = ", ".join(set(all_genres[:20])) if all_genres else "未知"
        
        # 提取热点
        hot_str = ""
        for source, topics in hot_topics.items():
            titles = [t.get("title", "") for t in topics[:5]]
            hot_str += f"{source}: {', '.join(titles)}\n"
        
        return f"""你是一位专业的网文市场分析师。请基于以下数据，分析当前市场趋势。

## 今日榜单数据
热门题材: {genre_str}

## 今日热点话题
{hot_str}

请分析：
1. 哪些题材正在上升（rising_genres）
2. 哪些题材正在下降（declining_genres）
3. 有什么创作机会（opportunities）
4. 有什么需要注意的预警（alerts）

以JSON格式输出：

```json
{
  "rising_genres": [
    {"genre": "题材名", "reason": "原因", "confidence": 0.8}
  ],
  "declining_genres": [
    {"genre": "题材名", "reason": "原因"}
  ],
  "opportunities": [
    {"opportunity": "机会描述", "suggested_genre": "建议题材"}
  ],
  "alerts": [
    {"alert": "预警信息", "severity": "warning"}
  ],
  "summary": "简短总结"
}
```

只输出JSON。"""


class RankingCrawler:
    """榜单爬虫（简化版）"""
    async def crawl_fanqie_rankings(self):
        from infrastructure.crawler.fanqie_crawler import FanqieCrawler
        crawler = FanqieCrawler()
        return await crawler.crawl_rankings()
    
    async def crawl_qidian_rankings(self):
        from infrastructure.crawler.qidian_crawler import QidianCrawler
        crawler = QidianCrawler()
        return await crawler.crawl_rankings()
    
    async def crawl_qimao_rankings(self):
        from infrastructure.crawler.qimao_crawler import QimaoCrawler
        crawler = QimaoCrawler()
        return await crawler.crawl_rankings()


class HotTopicCrawler:
    """热点爬虫（简化版）"""
    async def crawl_all_sources(self):
        from infrastructure.crawler.baidu_crawler import BaiduCrawler
        from infrastructure.crawler.weibo_crawler import WeiboCrawler
        crawler = BaiduCrawler()
        return {"baidu": await crawler.crawl_hot_topics()}