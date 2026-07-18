"""定时任务调度器 - 每日自动扫描发现模板"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, List
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from infrastructure.persistence.database.connection import DatabaseConnection, get_database
from infrastructure.persistence.database.market.sqlite_ranking_repository import SqliteRankingRepository
from infrastructure.persistence.database.market.sqlite_hot_topic_repository import SqliteHotTopicRepository
from infrastructure.persistence.database.market.sqlite_dynamic_template_repository import SqliteDynamicTemplateRepository
from infrastructure.persistence.database.market.sqlite_snapshot_repository import (
    SqliteSnapshotRepository,
    SqliteTrendAlertRepository,
)
from application.market.discovery.template_discovery_service import TemplateDiscoveryService
from application.market.trend.trend_analysis_service import TrendAnalysisService
from application.market.crawler.ranking_crawler_service import RankingCrawlerService
from application.market.crawler.hot_topic_crawler_service import HotTopicCrawlerService

logger = logging.getLogger(__name__)


class MarketDiscoveryScheduler:
    """市场发现定时任务调度器"""
    
    def __init__(
        self,
        db: Optional[DatabaseConnection] = None,
    ):
        self.db = db or get_database()
        self.scheduler = AsyncIOScheduler()
        self._running = False
    
    def _get_services(self):
        """获取服务实例"""
        ranking_repo = SqliteRankingRepository(self.db)
        template_repo = SqliteDynamicTemplateRepository(self.db)
        discovery_service = TemplateDiscoveryService(ranking_repo, template_repo)
        
        ranking_crawler = RankingCrawlerService(ranking_repo)
        hot_topic_crawler = HotTopicCrawlerService(
            SqliteHotTopicRepository(self.db)
        )
        
        return discovery_service, ranking_crawler, hot_topic_crawler
    
    async def daily_crawl_task(self):
        """每日爬取任务
        
        上午9点执行：爬取榜单 + 热点 + 保存快照
        """
        logger.info("Starting daily crawl task...")
        
        ranking_crawler = None
        hot_topic_crawler = None
        try:
            _, ranking_crawler, hot_topic_crawler = self._get_services()
            
            # 1. 爬取所有平台榜单
            logger.info("Crawling rankings from all platforms...")
            rankings_result = await ranking_crawler.crawl_all_platforms()
            logger.info(f"Rankings crawled: {sum(len(v) for v in rankings_result.values())} novels")
            
            # 2. 爬取热点
            logger.info("Crawling hot topics from all sources...")
            hot_topics_result = await hot_topic_crawler.crawl_all_sources()
            logger.info(f"Hot topics crawled: {sum(len(v) for v in hot_topics_result.values())} topics")
            
            # 3. 保存榜单快照（用于趋势分析）
            logger.info("Saving ranking snapshots...")
            snapshot_repo = SqliteSnapshotRepository(self.db)
            trend_service = TrendAnalysisService(
                snapshot_repo,
                SqliteTrendAlertRepository(self.db),
            )
            saved_count = await trend_service.save_crawl_snapshots(rankings_result)
            
            logger.info(f"Saved {saved_count} snapshots")
            logger.info("Daily crawl task completed successfully")
            errors = {**ranking_crawler.last_errors, **hot_topic_crawler.last_errors}
            return {
                "status": "partial" if errors else "success",
                "ranking_count": sum(len(v) for v in rankings_result.values()),
                "hot_topic_count": sum(len(v) for v in hot_topics_result.values()),
                "snapshot_count": saved_count,
                "errors": errors,
            }
            
        except Exception as e:
            logger.error(f"Daily crawl task failed: {e}")
            return {"status": "failed", "error": str(e)}
        finally:
            if ranking_crawler:
                await ranking_crawler.close()
            if hot_topic_crawler:
                await hot_topic_crawler.close()
    
    async def daily_trend_analysis_task(self):
        """每日趋势分析任务
        
        下午3点执行：分析所有题材的趋势并生成预警
        """
        logger.info("Starting daily trend analysis task...")
        
        try:
            snapshot_repo = SqliteSnapshotRepository(self.db)
            alert_repo = SqliteTrendAlertRepository(self.db)
            trend_service = TrendAnalysisService(snapshot_repo, alert_repo)
            
            # 分析所有平台和分类
            platforms = ["fanqie", "qidian", "qimao"]
            categories = ["都市", "玄幻", "言情", "仙侠", "科幻", "历史", "游戏", "体育"]
            
            all_trends = []
            for platform in platforms:
                trends = await trend_service.analyze_all_genres(platform, categories, days=7)
                all_trends.extend(trends)
            
            # 生成预警
            alerts = await trend_service.generate_alerts_from_trends(all_trends)
            
            logger.info(f"Analyzed {len(all_trends)} trends, generated {len(alerts)} alerts")
            
        except Exception as e:
            logger.error(f"Daily trend analysis task failed: {e}")
    
    async def daily_discovery_task(self):
        """每日发现任务
        
        晚上10点执行：从热门小说中发现模板
        """
        logger.info("Starting daily discovery task...")
        
        try:
            discovery_service, _, _ = self._get_services()
            
            result = await discovery_service.run_daily_discovery(
                platforms=["qidian"],
                categories=["都市", "玄幻", "言情", "仙侠"],
                top_n=3,
            )
            
            logger.info(f"Daily discovery completed: {result.get('total_templates_saved', 0)} templates saved")
            
        except Exception as e:
            logger.error(f"Daily discovery task failed: {e}")
        finally:
            if 'discovery_service' in locals():
                await discovery_service.close()
    
    async def weekly_deep_discovery_task(self):
        """每周深度发现任务
        
        周日凌晨2点执行：深入分析更多小说
        """
        logger.info("Starting weekly deep discovery task...")
        
        try:
            discovery_service, _, _ = self._get_services()
            
            result = await discovery_service.run_daily_discovery(
                platforms=["qidian"],
                categories=["都市", "玄幻", "言情", "仙侠", "科幻", "历史"],
                top_n=5,
            )
            
            logger.info(f"Weekly deep discovery completed: {result.get('total_templates_saved', 0)} templates saved")
            
        except Exception as e:
            logger.error(f"Weekly deep discovery task failed: {e}")
        finally:
            if 'discovery_service' in locals():
                await discovery_service.close()
    
    def setup_jobs(self):
        """配置定时任务"""
        
        # 每日爬取+保存快照：每天上午9点
        self.scheduler.add_job(
            self.daily_crawl_task,
            CronTrigger(hour=9, minute=0),
            id="daily_crawl",
            name="每日爬取榜单和热点+保存快照",
            replace_existing=True,
        )
        
        # 每日趋势分析：每天下午3点
        self.scheduler.add_job(
            self.daily_trend_analysis_task,
            CronTrigger(hour=15, minute=0),
            id="daily_trend_analysis",
            name="每日趋势分析",
            replace_existing=True,
        )
        
        # 每日发现：每天晚上10点
        self.scheduler.add_job(
            self.daily_discovery_task,
            CronTrigger(hour=22, minute=0),
            id="daily_discovery",
            name="每日模板发现",
            replace_existing=True,
        )
        
        # 每周深度发现：周日凌晨2点
        self.scheduler.add_job(
            self.weekly_deep_discovery_task,
            CronTrigger(day_of_week="sun", hour=2, minute=0),
            id="weekly_deep_discovery",
            name="每周深度模板发现",
            replace_existing=True,
        )
        
        logger.info("Scheduled jobs configured:")
        logger.info("  - daily_crawl: 09:00 every day")
        logger.info("  - daily_trend_analysis: 15:00 every day")
        logger.info("  - daily_discovery: 22:00 every day")
        logger.info("  - weekly_deep_discovery: 02:00 every Sunday")
    
    def start(self):
        """启动调度器"""
        if self._running:
            logger.warning("Scheduler is already running")
            return
        
        self.setup_jobs()
        self.scheduler.start()
        self._running = True
        logger.info("Market discovery scheduler started")
    
    def stop(self):
        """停止调度器"""
        if not self._running:
            return
        
        self.scheduler.shutdown(wait=True)
        self._running = False
        logger.info("Market discovery scheduler stopped")
    
    def run_once(self, task_name: str = "daily_crawl"):
        """手动执行一次任务"""
        if task_name == "daily_crawl":
            asyncio.create_task(self.daily_crawl_task())
        elif task_name == "daily_trend_analysis":
            asyncio.create_task(self.daily_trend_analysis_task())
        elif task_name == "daily_discovery":
            asyncio.create_task(self.daily_discovery_task())
        elif task_name == "weekly_deep_discovery":
            asyncio.create_task(self.weekly_deep_discovery_task())
        else:
            logger.warning(f"Unknown task: {task_name}")


# 全局调度器实例
_scheduler_instance: Optional[MarketDiscoveryScheduler] = None


def get_scheduler() -> MarketDiscoveryScheduler:
    """获取调度器实例"""
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = MarketDiscoveryScheduler()
    return _scheduler_instance


def start_scheduler():
    """启动调度器"""
    scheduler = get_scheduler()
    scheduler.start()


def stop_scheduler():
    """停止调度器"""
    global _scheduler_instance
    if _scheduler_instance:
        _scheduler_instance.stop()
