import logging
from datetime import datetime
from typing import Any, Dict, List
from uuid import NAMESPACE_URL, uuid5

from domain.market.entities.ranking import Ranking
from domain.market.repositories.ranking_repository import RankingRepository
from infrastructure.crawler import FanqieCrawler, QidianCrawler, QimaoCrawler

logger = logging.getLogger(__name__)


class RankingCrawlerService:
    """Fetch and persist verified external rankings.

    Empty, malformed, fallback, or font-obfuscated records are never persisted.
    Callers can inspect ``last_errors`` to distinguish a genuine empty result from
    a successful crawl.
    """

    def __init__(self, ranking_repository: RankingRepository):
        self.ranking_repository = ranking_repository
        self.qidian_crawler = QidianCrawler()
        self.fanqie_crawler = FanqieCrawler()
        self.qimao_crawler = QimaoCrawler()
        self.last_errors: Dict[str, str] = {}
        self.rejected_counts: Dict[str, int] = {}

    @staticmethod
    def _contains_private_use(text: str) -> bool:
        return any(0xE000 <= ord(char) <= 0xF8FF for char in text or "")

    def _is_valid_item(self, item: Dict[str, Any]) -> bool:
        extra_data = item.get("extra_data") or {}
        name = str(item.get("novel_name") or "").strip()
        author = str(item.get("author") or "").strip()
        rank = item.get("rank") or 0
        book_id = str(extra_data.get("book_id") or "").strip()

        return bool(
            name
            and author
            and book_id
            and isinstance(rank, int)
            and rank > 0
            and extra_data.get("source") != "fallback"
            and not extra_data.get("text_obfuscated")
            and not self._contains_private_use(name)
            and not self._contains_private_use(author)
        )

    def _to_rankings(
        self,
        platform: str,
        data: List[Dict[str, Any]],
    ) -> List[Ranking]:
        collected_at = datetime.utcnow()
        rankings: List[Ranking] = []
        seen = set()

        for item in data:
            if not self._is_valid_item(item):
                continue

            extra_data = dict(item.get("extra_data") or {})
            book_id = str(extra_data["book_id"])
            category = str(item.get("category") or "未分类").strip() or "未分类"
            dedupe_key = (platform, category, book_id)
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)

            rankings.append(
                Ranking(
                    id=str(uuid5(NAMESPACE_URL, ":".join(dedupe_key))),
                    platform=platform,
                    category=category,
                    rank=int(item.get("rank") or 0),
                    novel_name=str(item.get("novel_name") or "").strip(),
                    author=str(item.get("author") or "").strip(),
                    description=str(item.get("description") or "").strip(),
                    tags=str(item.get("tags") or "").strip(),
                    update_time=item.get("update_time"),
                    word_count=int(item.get("word_count") or 0),
                    popularity=int(item.get("popularity") or 0),
                    score=float(item.get("score") or 0),
                    comments=int(item.get("comments") or 0),
                    favorites=int(item.get("favorites") or 0),
                    collected_at=collected_at,
                    extra_data=extra_data,
                )
            )

        self.rejected_counts[platform] = max(0, len(data) - len(rankings))
        return rankings

    async def _crawl(self, platform: str, crawler: Any, limit: int) -> List[Ranking]:
        self.last_errors.pop(platform, None)
        try:
            data = await crawler.crawl_all_categories(limit=limit)
            rankings = self._to_rankings(platform, data)
            if not rankings:
                reason = getattr(crawler, "last_error", None)
                rejected = self.rejected_counts.get(platform, 0)
                if not reason and rejected:
                    reason = f"Rejected {rejected} records that failed data-quality validation"
                self.last_errors[platform] = reason or "Crawler returned no valid ranking data"
                logger.warning("%s crawl unavailable: %s", platform, self.last_errors[platform])
                return []

            self.ranking_repository.save_batch(rankings)
            logger.info("Crawled and saved %s verified rankings from %s", len(rankings), platform)
            return rankings
        except Exception as exc:
            self.last_errors[platform] = f"{type(exc).__name__}: {exc}"
            logger.exception("Failed to crawl %s", platform)
            return []

    async def crawl_qidian(self) -> List[Ranking]:
        return await self._crawl(Ranking.PLATFORM_QIDIAN, self.qidian_crawler, 20)

    async def crawl_fanqie(self) -> List[Ranking]:
        return await self._crawl(Ranking.PLATFORM_FANQIE, self.fanqie_crawler, 10)

    async def crawl_qimao(self) -> List[Ranking]:
        return await self._crawl(Ranking.PLATFORM_QIMAO, self.qimao_crawler, 30)

    async def crawl_all_platforms(self) -> Dict[str, List[Ranking]]:
        results = {
            Ranking.PLATFORM_QIDIAN: await self.crawl_qidian(),
            Ranking.PLATFORM_FANQIE: await self.crawl_fanqie(),
            Ranking.PLATFORM_QIMAO: await self.crawl_qimao(),
        }
        logger.info(
            "Ranking crawl completed: %s verified records, errors=%s",
            sum(len(items) for items in results.values()),
            self.last_errors,
        )
        return results

    async def close(self) -> None:
        await self.qidian_crawler.close()
        await self.fanqie_crawler.close()
        await self.qimao_crawler.close()
