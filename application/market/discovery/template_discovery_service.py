"""模板自动发现服务 - 从爆款中自动发现新模板"""
import logging
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime

from domain.market.entities.dynamic_template import DiscoveredTemplate, TemplateType
from domain.market.repositories.dynamic_template_repository import DynamicTemplateRepository
from infrastructure.persistence.database.connection import DatabaseConnection
from infrastructure.persistence.database.market.sqlite_ranking_repository import SqliteRankingRepository
from infrastructure.persistence.database.market.sqlite_dynamic_template_repository import SqliteDynamicTemplateRepository
from infrastructure.crawler.novel_content_crawler import NovelContentCrawler
from application.market.analyzer.bestseller_analysis_agent import BestsellerAnalysisAgent

logger = logging.getLogger(__name__)


class TemplateDiscoveryService:
    """模板自动发现服务
    
    核心流程：
    1. 获取热门榜单
    2. 爬取免费章节
    3. AI分析提取模板
    4. 保存到模板库
    """
    
    def __init__(
        self,
        ranking_repo,
        template_repo: DynamicTemplateRepository,
        content_crawler: Optional[NovelContentCrawler] = None,
        analysis_agent: Optional[BestsellerAnalysisAgent] = None,
    ):
        self.ranking_repo = ranking_repo
        self.template_repo = template_repo
        self.content_crawler = content_crawler or NovelContentCrawler()
        self.analysis_agent = analysis_agent or BestsellerAnalysisAgent(template_repo)
    
    async def discover_from_top_novels(
        self,
        platform: str = "fanqie",
        category: Optional[str] = None,
        top_n: int = 5,
        max_chapters: int = 20,
        max_words: int = 30000,
    ) -> Dict[str, Any]:
        """从热门小说中发现模板
        
        Args:
            platform: 平台（fanqie, qidian）
            category: 分类（可选，如"都市"、"玄幻"）
            top_n: 分析前N本小说
            max_chapters: 每本最大章节数
            max_words: 分析文本最大字数
        
        Returns:
            发现结果统计
        """
        result = {
            "platform": platform,
            "category": category,
            "analyzed_novels": 0,
            "total_templates_found": 0,
            "templates_saved": 0,
            "errors": [],
            "started_at": datetime.utcnow().isoformat(),
            "completed_at": None,
        }
        
        try:
            # 1. 获取热门小说列表
            rankings = await self._get_top_rankings(platform, category, top_n)
            
            if not rankings:
                logger.warning(f"No rankings found for platform={platform}, category={category}")
                result["errors"].append("No rankings found")
                return result
            
            logger.info(f"Found {len(rankings)} top novels to analyze")
            
            # 2. 逐本分析
            for rank_item in rankings:
                try:
                    book_id = str(rank_item.get("book_id") or rank_item.get("novel_id", ""))
                    book_name = rank_item.get("novel_name", rank_item.get("name", ""))
                    
                    if not book_id:
                        continue
                    
                    logger.info(f"Analyzing novel: {book_name} (ID: {book_id})")
                    
                    # 爬取章节
                    novel_data = await self.content_crawler.crawl_novel_for_analysis(
                        platform=platform,
                        book_id=book_id,
                        max_chapters=max_chapters,
                    )
                    
                    if not novel_data or not novel_data.get("chapters"):
                        logger.warning(f"No chapters crawled for {book_name}")
                        continue
                    
                    # 合并文本用于分析
                    analysis_text = await self.content_crawler.get_novel_text_for_analysis(
                        novel_data,
                        max_words=max_words,
                    )
                    
                    # 准备小说信息
                    novel_info = {
                        **novel_data,
                        "platform": platform,
                        "rank": rank_item.get("rank", 0),
                        "popularity": rank_item.get("popularity", 0),
                        "score": rank_item.get("score", 0),
                    }
                    
                    # AI分析
                    analysis_result = await self.analysis_agent.analyze_novel(
                        analysis_text,
                        novel_info,
                    )
                    
                    if analysis_result.get("error"):
                        logger.warning(f"Analysis failed for {book_name}: {analysis_result.get('error')}")
                        continue
                    
                    # 提取模板
                    templates = await self.analysis_agent.extract_templates_from_analysis(
                        analysis_result,
                        novel_info,
                    )
                    
                    # 保存模板
                    saved_count = await self.analysis_agent.save_templates(templates)
                    
                    result["analyzed_novels"] += 1
                    result["total_templates_found"] += len(templates)
                    result["templates_saved"] += saved_count
                    
                    logger.info(f"Saved {saved_count} templates from {book_name}")
                    
                    # 避免过于频繁的请求
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    error_msg = f"Failed to analyze {rank_item.get('novel_name', 'unknown')}: {str(e)}"
                    logger.error(error_msg)
                    result["errors"].append(error_msg)
                    continue
            
        except Exception as e:
            error_msg = f"Discovery process failed: {str(e)}"
            logger.error(error_msg)
            result["errors"].append(error_msg)
        
        result["completed_at"] = datetime.utcnow().isoformat()
        
        return result
    
    async def _get_top_rankings(
        self,
        platform: str,
        category: Optional[str],
        limit: int,
    ) -> List[Dict[str, Any]]:
        """获取热门榜单数据"""
        try:
            # 从数据库获取最新榜单
            rankings = self.ranking_repo.get_by_platform_and_category(
                platform=platform,
                category=category,
                limit=limit,
            )
            
            return rankings
            
        except Exception as e:
            logger.error(f"Failed to get rankings: {e}")
            return []
    
    async def run_daily_discovery(
        self,
        platforms: List[str] = None,
        categories: List[str] = None,
        top_n: int = 3,
    ) -> Dict[str, Any]:
        """每日自动发现任务
        
        Args:
            platforms: 要扫描的平台列表
            categories: 要扫描的分类列表
            top_n: 每个分类分析前N本
        
        Returns:
            汇总结果
        """
        if platforms is None:
            platforms = ["fanqie"]
        
        if categories is None:
            categories = ["都市", "玄幻", "言情", "仙侠"]
        
        summary = {
            "started_at": datetime.utcnow().isoformat(),
            "platforms": platforms,
            "categories": categories,
            "results": [],
            "total_templates_saved": 0,
            "total_errors": 0,
        }
        
        for platform in platforms:
            for category in categories:
                logger.info(f"Running discovery: {platform}/{category}")
                
                try:
                    result = await self.discover_from_top_novels(
                        platform=platform,
                        category=category,
                        top_n=top_n,
                    )
                    
                    summary["results"].append(result)
                    summary["total_templates_saved"] += result.get("templates_saved", 0)
                    summary["total_errors"] += len(result.get("errors", []))
                    
                except Exception as e:
                    logger.error(f"Discovery failed for {platform}/{category}: {e}")
                    summary["total_errors"] += 1
        
        summary["completed_at"] = datetime.utcnow().isoformat()
        
        return summary
    
    async def get_discovered_templates(
        self,
        pattern_type: Optional[TemplateType] = None,
        genre: Optional[str] = None,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """获取已发现的模板"""
        templates = []
        
        try:
            if pattern_type and genre:
                templates = await self.template_repo.search("", pattern_type, genre, limit)
            elif pattern_type:
                templates = await self.template_repo.list_by_type(pattern_type, limit)
            elif genre:
                templates = await self.template_repo.list_by_genre(genre, limit)
            else:
                templates = await self.template_repo.list_trending(limit)
            
            return [t.to_dict() for t in templates]
            
        except Exception as e:
            logger.error(f"Failed to get templates: {e}")
            return []
    
    async def get_trending_templates(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取热门模板"""
        try:
            templates = await self.template_repo.list_trending(limit)
            return [t.to_dict() for t in templates]
        except Exception as e:
            logger.error(f"Failed to get trending templates: {e}")
            return []
    
    async def get_recent_discoveries(self, days: int = 7, limit: int = 20) -> List[Dict[str, Any]]:
        """获取最近发现的模板"""
        try:
            templates = await self.template_repo.list_recent(days, limit)
            return [t.to_dict() for t in templates]
        except Exception as e:
            logger.error(f"Failed to get recent discoveries: {e}")
            return []
    
    async def search_templates(
        self,
        keyword: str,
        pattern_type: Optional[TemplateType] = None,
        genre: Optional[str] = None,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """搜索模板"""
        try:
            templates = await self.template_repo.search(keyword, pattern_type, genre, limit)
            return [t.to_dict() for t in templates]
        except Exception as e:
            logger.error(f"Failed to search templates: {e}")
            return []
