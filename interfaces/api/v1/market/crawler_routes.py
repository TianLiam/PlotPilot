from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List, Any
import logging

from application.market.crawler.ranking_crawler_service import RankingCrawlerService
from application.market.crawler.hot_topic_crawler_service import HotTopicCrawlerService
from infrastructure.persistence.database.connection import get_database
from infrastructure.persistence.database.market.sqlite_ranking_repository import SqliteRankingRepository
from infrastructure.persistence.database.market.sqlite_hot_topic_repository import SqliteHotTopicRepository
from infrastructure.persistence.database.market.sqlite_snapshot_repository import (
    SqliteSnapshotRepository,
    SqliteTrendAlertRepository,
)
from application.market.trend.trend_analysis_service import TrendAnalysisService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/market/crawler", tags=["market-crawler"])


async def get_ranking_crawler_service():
    repo = SqliteRankingRepository(get_database())
    service = RankingCrawlerService(repo)
    try:
        yield service
    finally:
        await service.close()


async def get_hot_topic_crawler_service():
    repo = SqliteHotTopicRepository(get_database())
    service = HotTopicCrawlerService(repo)
    try:
        yield service
    finally:
        await service.close()


def _require_results(results, source: str, errors: Dict[str, str]):
    if results:
        return {
            "status": "success",
            "source": source,
            "count": len(results),
            "message": f"Crawled {len(results)} verified records from {source}",
        }
    raise HTTPException(
        status_code=502,
        detail={
            "status": "failed",
            "source": source,
            "count": 0,
            "error": errors.get(source, "Crawler returned no verified data"),
        },
    )


async def _save_ranking_snapshots(results: Dict[str, List[Any]]) -> int:
    db = get_database()
    trend_service = TrendAnalysisService(
        SqliteSnapshotRepository(db),
        SqliteTrendAlertRepository(db),
    )
    return await trend_service.save_crawl_snapshots(results)


@router.post("/rankings/qidian")
async def crawl_qidian(
    service: RankingCrawlerService = Depends(get_ranking_crawler_service)
):
    try:
        results = await service.crawl_qidian()
        response = _require_results(results, "qidian", service.last_errors)
        response["snapshot_count"] = await _save_ranking_snapshots({"qidian": results})
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to crawl Qidian: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to crawl Qidian: {str(e)}")


@router.post("/rankings/fanqie")
async def crawl_fanqie(
    service: RankingCrawlerService = Depends(get_ranking_crawler_service)
):
    try:
        results = await service.crawl_fanqie()
        response = _require_results(results, "fanqie", service.last_errors)
        response["snapshot_count"] = await _save_ranking_snapshots({"fanqie": results})
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to crawl Fanqie: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to crawl Fanqie: {str(e)}")


@router.post("/rankings/qimao")
async def crawl_qimao(
    service: RankingCrawlerService = Depends(get_ranking_crawler_service)
):
    try:
        results = await service.crawl_qimao()
        response = _require_results(results, "qimao", service.last_errors)
        response["snapshot_count"] = await _save_ranking_snapshots({"qimao": results})
        return response
    except HTTPException:
        raise
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
        if total == 0:
            raise HTTPException(
                status_code=502,
                detail={
                    "status": "failed",
                    "message": "No platform returned verified ranking data",
                    "count_by_platform": {k: len(v) for k, v in results.items()},
                    "errors": service.last_errors,
                },
            )
        status = "partial" if service.last_errors else "success"
        snapshot_count = await _save_ranking_snapshots(results)
        return {
            "status": status,
            "message": f"Crawled {total} verified rankings from all platforms",
            "total_count": total,
            "count_by_platform": {k: len(v) for k, v in results.items()},
            "errors": service.last_errors,
            "rejected_count_by_platform": service.rejected_counts,
            "snapshot_count": snapshot_count,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to crawl all rankings: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to crawl all rankings: {str(e)}")


@router.post("/hot-topics/weibo")
async def crawl_weibo(
    service: HotTopicCrawlerService = Depends(get_hot_topic_crawler_service)
):
    try:
        results = await service.crawl_weibo()
        return _require_results(results, "weibo", service.last_errors)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to crawl Weibo: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to crawl Weibo: {str(e)}")


@router.post("/hot-topics/baidu")
async def crawl_baidu(
    service: HotTopicCrawlerService = Depends(get_hot_topic_crawler_service)
):
    try:
        results = await service.crawl_baidu()
        return _require_results(results, "baidu", service.last_errors)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to crawl Baidu: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to crawl Baidu: {str(e)}")


@router.post("/hot-topics/zhihu")
async def crawl_zhihu(
    service: HotTopicCrawlerService = Depends(get_hot_topic_crawler_service)
):
    try:
        results = await service.crawl_zhihu()
        return _require_results(results, "zhihu", service.last_errors)
    except HTTPException:
        raise
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
        if total == 0:
            raise HTTPException(
                status_code=502,
                detail={
                    "status": "failed",
                    "message": "No source returned verified hot-topic data",
                    "count_by_source": {k: len(v) for k, v in results.items()},
                    "errors": service.last_errors,
                },
            )
        return {
            "status": "partial" if service.last_errors else "success",
            "message": f"Crawled {total} verified hot topics from all sources",
            "total_count": total,
            "count_by_source": {k: len(v) for k, v in results.items()},
            "errors": service.last_errors,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to crawl all hot topics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to crawl all hot topics: {str(e)}")


@router.post("/all")
async def crawl_everything(
    ranking_service: RankingCrawlerService = Depends(get_ranking_crawler_service),
    hot_topic_service: HotTopicCrawlerService = Depends(get_hot_topic_crawler_service)
):
    ranking_results = await ranking_service.crawl_all_platforms()
    topic_results = await hot_topic_service.crawl_all_sources()
    ranking_count = sum(len(items) for items in ranking_results.values())
    topic_count = sum(len(items) for items in topic_results.values())
    errors = {**ranking_service.last_errors, **hot_topic_service.last_errors}
    if ranking_count + topic_count == 0:
        raise HTTPException(
            status_code=502,
            detail={"status": "failed", "message": "No verified external data was collected", "errors": errors},
        )
    snapshot_count = await _save_ranking_snapshots(ranking_results) if ranking_count else 0
    return {
        "status": "partial" if errors else "success",
        "ranking_count": ranking_count,
        "hot_topic_count": topic_count,
        "snapshot_count": snapshot_count,
        "errors": errors,
    }
