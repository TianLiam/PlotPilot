import json
from datetime import datetime

import pytest

from application.market.crawler.ranking_crawler_service import RankingCrawlerService
from application.market.discovery.template_discovery_service import TemplateDiscoveryService
from application.market.scheduler.discovery_scheduler import MarketDiscoveryScheduler
from application.market.trend.trend_analysis_service import TrendAnalysisService
from domain.market.entities.ranking import Ranking
from domain.market.entities.trend_snapshot import RankingSnapshot, RankingSnapshotItem
from infrastructure.crawler.base_crawler import BaseCrawler
from infrastructure.crawler.fanqie_crawler import FanqieCrawler
from infrastructure.crawler.qidian_crawler import QidianCrawler
from infrastructure.crawler.qimao_crawler import QimaoCrawler
from infrastructure.persistence.database.connection import DatabaseConnection
from infrastructure.persistence.database.market.sqlite_snapshot_repository import (
    SqliteSnapshotRepository,
    SqliteTrendAlertRepository,
)


class _Response:
    def __init__(self, *, data=None, content=b""):
        self._data = data
        self.content = content

    def json(self):
        return self._data


class _RankingRepo:
    def __init__(self):
        self.saved = []

    def save_batch(self, items):
        self.saved.extend(items)


def _ranking(category="玄幻", rank=1, book_id="book-1"):
    return Ranking(
        id=f"rank-{book_id}",
        platform="qidian",
        category=category,
        rank=rank,
        novel_name=f"小说{book_id}",
        author="作者",
        word_count=100_000,
        popularity=10_000,
        tags=f"{category},系统",
        collected_at=datetime.utcnow(),
        extra_data={"source": "qidian_mobile_api", "book_id": book_id},
    )


def test_parse_int_understands_chinese_units():
    crawler = BaseCrawler()
    assert crawler.parse_int("5.49万月票") == 54_900
    assert crawler.parse_int("142.6万热度") == 1_426_000
    assert crawler.parse_int("1.2亿") == 120_000_000
    assert crawler.parse_int("无数据", 7) == 7


@pytest.mark.asyncio
async def test_qidian_uses_mobile_api_and_maps_verified_fields(monkeypatch):
    crawler = QidianCrawler(delay_range=(0, 0))

    async def token():
        return "csrf"

    async def request(*args, **kwargs):
        return _Response(data={
            "code": 0,
            "data": {
                "isLast": 1,
                "records": [{
                    "bid": "1035420986",
                    "bName": "玄鉴仙族",
                    "bAuth": "季越人",
                    "desc": "简介",
                    "cat": "仙侠",
                    "catId": 22,
                    "subCat": "修真文明",
                    "subCatId": 18,
                    "cnt": "602.36万字",
                    "rankCnt": "5.49万月票",
                    "rankNum": 1,
                }],
            },
        })

    monkeypatch.setattr(crawler, "_ensure_csrf_token", token)
    monkeypatch.setattr(crawler, "safe_request", request)
    rows = await crawler.crawl_ranking("仙侠", 20)

    assert len(rows) == 1
    assert rows[0]["novel_name"] == "玄鉴仙族"
    assert rows[0]["word_count"] == 6_023_600
    assert rows[0]["popularity"] == 54_900
    assert rows[0]["extra_data"]["source"] == "qidian_mobile_api"


def test_fanqie_initial_state_parser_handles_function_wrapper():
    state = {"rank": {"book_list": [{"bookId": "1"}]}}
    html = f"<script>(function(){{window.__INITIAL_STATE__={json.dumps(state)};}})()</script>"
    assert FanqieCrawler._extract_initial_state(html) == state


@pytest.mark.asyncio
async def test_obfuscated_fanqie_rows_are_not_persisted():
    repo = _RankingRepo()
    service = RankingCrawlerService(repo)

    class _Crawler:
        last_error = None

        async def crawl_all_categories(self, limit):
            return [{
                "category": "都市",
                "rank": 1,
                "novel_name": "归\ue412留洋",
                "author": "作者",
                "extra_data": {
                    "source": "fanqie_html",
                    "book_id": "1",
                    "text_obfuscated": True,
                },
            }]

    rows = await service._crawl("fanqie", _Crawler(), 10)
    assert rows == []
    assert repo.saved == []
    assert service.rejected_counts["fanqie"] == 1
    assert "data-quality" in service.last_errors["fanqie"]


@pytest.mark.asyncio
async def test_qimao_parses_current_ranking_html(monkeypatch):
    crawler = QimaoCrawler(delay_range=(0, 0))
    page = """
    <ul><li class="rank-list-item"><div>
      <a href="https://www.qimao.com/shuku/195958/"><span class="rank-number first">1</span></a>
      <a class="s-book-title" href="https://www.qimao.com/shuku/195958/">盖世神医</a>
      <span class="s-book-info clearfix">
        <a>狐颜乱语</a><a>都市</a><a>都市高武</a><em>连载中</em><em>881.04万字</em>
      </span>
      <span class="s-book-intro">小说简介</span>
      <span class="rank-num">142.6</span><span class="rank-unit">万</span>
    </div></li></ul>
    """.encode()

    async def request(*args, **kwargs):
        return _Response(content=page)

    monkeypatch.setattr(crawler, "safe_request", request)
    rows = await crawler.crawl_all_categories(30)

    assert len(rows) == 1
    assert rows[0]["novel_name"] == "盖世神医"
    assert rows[0]["author"] == "狐颜乱语"
    assert rows[0]["category"] == "都市"
    assert rows[0]["word_count"] == 8_810_400
    assert rows[0]["popularity"] == 1_426_000
    assert rows[0]["extra_data"]["book_id"] == "195958"


@pytest.mark.asyncio
async def test_template_discovery_reads_ranking_entities_and_applies_limit():
    class _Repo:
        def get_by_platform_and_category(self, platform, category):
            return [_ranking(category, 2, "b"), _ranking(category, 1, "a")]

    service = object.__new__(TemplateDiscoveryService)
    service.ranking_repo = _Repo()
    rows = await service._get_top_rankings("qidian", "玄幻", 1)
    assert [row.rank for row in rows] == [1]


@pytest.mark.asyncio
async def test_template_discovery_reports_ai_failure_in_result():
    class _Repo:
        def get_by_platform(self, platform):
            return [_ranking()]

    class _ContentCrawler:
        async def crawl_novel_for_analysis(self, **kwargs):
            return {"chapters": [{"content": "正文"}], "crawled_chapters": 1}

        async def get_novel_text_for_analysis(self, novel_data, max_words):
            return "正文"

    class _AnalysisAgent:
        async def analyze_novel(self, novel_text, novel_info):
            return {"error": "LLM is not configured"}

    service = TemplateDiscoveryService(
        _Repo(),
        object(),
        content_crawler=_ContentCrawler(),
        analysis_agent=_AnalysisAgent(),
    )

    result = await service.discover_from_top_novels(top_n=1, max_chapters=5)

    assert result["analyzed_novels"] == 0
    assert result["completed_at"] is not None
    assert result["errors"] == [
        "AI analysis failed for 小说book-1: LLM is not configured"
    ]


@pytest.mark.asyncio
async def test_template_discovery_sets_completion_time_when_no_rankings():
    class _Repo:
        def get_by_platform(self, platform):
            return []

    service = TemplateDiscoveryService(_Repo(), object())

    result = await service.discover_from_top_novels(top_n=1, max_chapters=5)

    assert result["errors"] == ["No rankings found"]
    assert result["completed_at"] is not None


@pytest.mark.asyncio
async def test_scheduler_saves_real_rankings_as_category_snapshots(tmp_path, monkeypatch):
    db = DatabaseConnection(str(tmp_path / "market.db"))
    scheduler = MarketDiscoveryScheduler(db)

    class _RankingCrawler:
        last_errors = {}

        async def crawl_all_platforms(self):
            return {"qidian": [_ranking("玄幻", 1, "a"), _ranking("都市", 1, "b")]}

        async def close(self):
            pass

    class _HotCrawler:
        last_errors = {}

        async def crawl_all_sources(self):
            return {"weibo": []}

        async def close(self):
            pass

    monkeypatch.setattr(
        scheduler,
        "_get_services",
        lambda: (object(), _RankingCrawler(), _HotCrawler()),
    )
    result = await scheduler.daily_crawl_task()

    snapshot_repo = SqliteSnapshotRepository(db)
    assert result["status"] == "success"
    assert result["snapshot_count"] == 2
    assert len(await snapshot_repo.get_ranking_history("qidian", "玄幻", 1)) == 1
    assert len(await snapshot_repo.get_ranking_history("qidian", "都市", 1)) == 1


@pytest.mark.asyncio
async def test_trend_dashboard_uses_persisted_history_without_estimates(tmp_path):
    db = DatabaseConnection(str(tmp_path / "trend.db"))
    snapshot_repo = SqliteSnapshotRepository(db)
    service = TrendAnalysisService(snapshot_repo, SqliteTrendAlertRepository(db))
    older = RankingSnapshot(
        snapshot_date="2026-07-17",
        platform="qidian",
        category="玄幻",
        items=[RankingSnapshotItem("qidian", "玄幻", "a", "小说A", "作者", 10, popularity=100, tags=["系统"])],
        total_count=1,
    )
    newer = RankingSnapshot(
        snapshot_date="2026-07-18",
        platform="qidian",
        category="玄幻",
        items=[RankingSnapshotItem("qidian", "玄幻", "a", "小说A", "作者", 1, popularity=10_000, tags=["系统"])],
        total_count=1,
    )
    await snapshot_repo.save_ranking_snapshot(older)
    await snapshot_repo.save_ranking_snapshot(newer)

    dashboard = await service.get_dashboard(30)
    assert dashboard["data_state"] == "historical"
    assert dashboard["snapshot_count"] == 2
    assert dashboard["line_series"][0]["data_points"][0]["date"] == "2026-07-17"
    assert dashboard["hot_tags"] == [{"name": "系统", "value": 1}]
