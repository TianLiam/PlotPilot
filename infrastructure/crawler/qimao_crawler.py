import logging
import re
from typing import List, Dict, Any
from datetime import datetime

from lxml import html as lxml_html

from infrastructure.crawler.base_crawler import BaseCrawler

logger = logging.getLogger(__name__)


class QimaoCrawler(BaseCrawler):
    BASE_URL = "https://www.qimao.com"
    RANKING_PAGE = "https://www.qimao.com/paihang"

    CATEGORIES = {
        "都市": {"cat_id": 1},
        "玄幻": {"cat_id": 2},
        "仙侠": {"cat_id": 3},
        "奇幻": {"cat_id": 4},
        "历史": {"cat_id": 5},
        "游戏": {"cat_id": 6},
        "科幻": {"cat_id": 7},
        "悬疑": {"cat_id": 8},
        "言情": {"cat_id": 9},
        "军事": {"cat_id": 10},
    }

    async def _crawl_page(self, limit: int = 30) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        try:
            headers = self._get_default_headers(referer=self.BASE_URL)
            response = await self.safe_request("get", self.RANKING_PAGE, headers=headers, max_retries=2)
            if response is None:
                return results

            document = lxml_html.fromstring(response.content.decode("utf-8", errors="replace"))
            items = document.find_class("rank-list-item")
            for fallback_rank, item in enumerate(items[:limit], 1):
                title_nodes = item.find_class("s-book-title")
                info_nodes = item.find_class("s-book-info")
                if not title_nodes or not info_nodes:
                    continue

                title_node = title_nodes[0]
                info_links = info_nodes[0].xpath(".//a")
                info_em = [self.clean_text(node.text_content()) for node in info_nodes[0].xpath(".//em")]
                url = title_node.get("href") or ""
                book_id_match = re.search(r"/shuku/(\d+)/", url)
                category = self.clean_text(info_links[1].text_content()) if len(info_links) > 1 else ""
                subcategory = self.clean_text(info_links[2].text_content()) if len(info_links) > 2 else ""
                word_text = next((value for value in info_em if "字" in value), "")
                rank_nodes = item.xpath(".//*[contains(concat(' ', normalize-space(@class), ' '), ' rank-number ')]")
                popularity_nodes = item.find_class("rank-num")
                unit_nodes = item.find_class("rank-unit")
                rank = self.parse_int(rank_nodes[0].text_content(), fallback_rank) if rank_nodes else fallback_rank
                popularity_text = "".join([
                    popularity_nodes[0].text_content() if popularity_nodes else "",
                    unit_nodes[0].text_content() if unit_nodes else "",
                ])
                author = self.clean_text(info_links[0].text_content()) if info_links else ""
                intro_nodes = item.find_class("s-book-intro")
                result = {
                    "platform": "qimao",
                    "category": category,
                    "rank": rank,
                    "novel_name": self.clean_text(title_node.text_content()),
                    "author": author,
                    "description": self.clean_text(intro_nodes[0].text_content()) if intro_nodes else "",
                    "tags": ",".join(filter(None, [category, subcategory])),
                    "word_count": self.parse_int(word_text),
                    "popularity": self.parse_int(popularity_text),
                    "score": 0.0,
                    "comments": 0,
                    "favorites": 0,
                    "collected_at": datetime.utcnow(),
                    "extra_data": {
                        "source": "qimao_html",
                        "book_id": book_id_match.group(1) if book_id_match else "",
                        "subcategory": subcategory,
                        "ranking_metric": "heat",
                        "url": url,
                    },
                }
                results.append(result)

            if not results:
                self.last_error = "Qimao ranking page did not contain valid rank-list-item entries"
            logger.info(f"Crawled {len(results)} novels from Qimao ranking page")
            await self._delay()

        except Exception as e:
            self.last_error = f"{type(e).__name__}: {e}"
            logger.error(f"Failed to crawl Qimao ranking page: {e}")

        return results

    async def crawl_ranking(self, category: str, limit: int = 20) -> List[Dict[str, Any]]:
        if category not in self.CATEGORIES:
            logger.warning(f"Unknown category: {category}")
            return []
        results = await self._crawl_page(max(limit, 30))
        return [item for item in results if item.get("category") == category][:limit]

    async def crawl_all_categories(self, limit: int = 20) -> List[Dict[str, Any]]:
        all_results = await self._crawl_page(limit)
        logger.info(f"Total crawled {len(all_results)} novels from Qimao")
        return all_results
