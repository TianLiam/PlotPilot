from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends
from typing import Dict, List, Any
import logging

from application.market.crawler.ranking_crawler_service import RankingCrawlerService
from application.market.crawler.hot_topic_crawler_service import HotTopicCrawlerService
from infrastructure.persistence.database.connection import get_database
from infrastructure.persistence.database.market.sqlite_ranking_repository import SqliteRankingRepository
from infrastructure.persistence.database.market.sqlite_hot_topic_repository import SqliteHotTopicRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/market/crawler", tags=["market-crawler"])


def get_ranking_crawler_service() -> RankingCrawlerService:
    repo = SqliteRankingRepository(get_database())
    return RankingCrawlerService(repo)


def get_hot_topic_crawler_service() -> HotTopicCrawlerService:
    repo = SqliteHotTopicRepository(get_database())
    return HotTopicCrawlerService(repo)


@router.post("/rankings/qidian")
async def crawl_qidian(
    service: RankingCrawlerService = Depends(get_ranking_crawler_service)
):
    try:
        results = await service.crawl_qidian()
        return {"message": f"Crawled {len(results)} rankings from Qidian", "count": len(results)}
    except Exception as e:
        logger.error(f"Failed to crawl Qidian: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to crawl Qidian: {str(e)}")


@router.post("/rankings/fanqie")
async def crawl_fanqie(
    service: RankingCrawlerService = Depends(get_ranking_crawler_service)
):
    try:
        results = await service.crawl_fanqie()
        return {"message": f"Crawled {len(results)} rankings from Fanqie", "count": len(results)}
    except Exception as e:
        logger.error(f"Failed to crawl Fanqie: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to crawl Fanqie: {str(e)}")


@router.post("/rankings/qimao")
async def crawl_qimao(
    service: RankingCrawlerService = Depends(get_ranking_crawler_service)
):
    try:
        results = await service.crawl_qimao()
        return {"message": f"Crawled {len(results)} rankings from Qimao", "count": len(results)}
    except Exception as e:
        logger.error(f"Failed to crawl Qimao: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to crawl Qimao: {str(e)}")


@router.post("/rankings/all")
async def crawl_all_rankings(
    service: RankingCrawlerService = Depends(get_ranking_crawler_service)
):
    try:
        results = await service.crawl_all_platforms()
        total = sum(len(v) for v in results.values())
        return {
            "message": f"Crawled {total} rankings from all platforms",
            "count_by_platform": {k: len(v) for k, v in results.items()}
        }
    except Exception as e:
        logger.error(f"Failed to crawl all rankings: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to crawl all rankings: {str(e)}")


@router.post("/hot-topics/weibo")
async def crawl_weibo(
    service: HotTopicCrawlerService = Depends(get_hot_topic_crawler_service)
):
    try:
        results = await service.crawl_weibo()
        return {"message": f"Crawled {len(results)} hot topics from Weibo", "count": len(results)}
    except Exception as e:
        logger.error(f"Failed to crawl Weibo: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to crawl Weibo: {str(e)}")


@router.post("/hot-topics/baidu")
async def crawl_baidu(
    service: HotTopicCrawlerService = Depends(get_hot_topic_crawler_service)
):
    try:
        results = await service.crawl_baidu()
        return {"message": f"Crawled {len(results)} hot topics from Baidu", "count": len(results)}
    except Exception as e:
        logger.error(f"Failed to crawl Baidu: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to crawl Baidu: {str(e)}")


@router.post("/hot-topics/zhihu")
async def crawl_zhihu(
    service: HotTopicCrawlerService = Depends(get_hot_topic_crawler_service)
):
    try:
        results = await service.crawl_zhihu()
        return {"message": f"Crawled {len(results)} hot topics from Zhihu", "count": len(results)}
    except Exception as e:
        logger.error(f"Failed to crawl Zhihu: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to crawl Zhihu: {str(e)}")


@router.post("/hot-topics/all")
async def crawl_all_hot_topics(
    service: HotTopicCrawlerService = Depends(get_hot_topic_crawler_service)
):
    try:
        results = await service.crawl_all_sources()
        total = sum(len(v) for v in results.values())
        return {
            "message": f"Crawled {total} hot topics from all sources",
            "count_by_source": {k: len(v) for k, v in results.items()}
        }
    except Exception as e:
        logger.error(f"Failed to crawl all hot topics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to crawl all hot topics: {str(e)}")


@router.post("/all")
async def crawl_everything(
    background_tasks: BackgroundTasks,
    ranking_service: RankingCrawlerService = Depends(get_ranking_crawler_service),
    hot_topic_service: HotTopicCrawlerService = Depends(get_hot_topic_crawler_service)
):
    async def crawl_all():
        await ranking_service.crawl_all_platforms()
        await hot_topic_service.crawl_all_sources()
    
    background_tasks.add_task(crawl_all)
    return {"message": "Crawling started in background", "status": "processing"}