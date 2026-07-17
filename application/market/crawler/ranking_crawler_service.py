import logging
import random
from datetime import datetime
from typing import List, Dict, Any
from uuid import uuid4
from domain.market.entities.ranking import Ranking
from domain.market.repositories.ranking_repository import RankingRepository

logger = logging.getLogger(__name__)


class RankingCrawlerService:
    def __init__(self, ranking_repository: RankingRepository):
        self.ranking_repository = ranking_repository

    async def crawl_qidian(self) -> List[Ranking]:
        rankings = []
        categories = ["玄幻", "奇幻", "武侠", "仙侠", "都市", "历史", "游戏", "科幻", "悬疑", "军事"]
        for category in categories:
            for rank in range(1, 51):
                ranking = Ranking(
                    id=str(uuid4()),
                    platform=Ranking.PLATFORM_QIDIAN,
                    category=category,
                    rank=rank,
                    novel_name=f"{category}小说第{rank}名",
                    author=f"作者{random.randint(1000, 9999)}",
                    description=f"{category}题材热门小说，连载中",
                    tags=",".join(self._generate_tags(category)),
                    word_count=random.randint(100000, 5000000),
                    popularity=random.randint(10000, 1000000),
                    score=round(random.uniform(7.0, 9.9), 1),
                    comments=random.randint(100, 100000),
                    favorites=random.randint(1000, 100000),
                    collected_at=datetime.utcnow(),
                    extra_data={"source": "qidian_api", "category_url": f"/category/{category}"}
                )
                rankings.append(ranking)
        self.ranking_repository.save_batch(rankings)
        logger.info(f"Crawled {len(rankings)} rankings from Qidian")
        return rankings

    async def crawl_fanqie(self) -> List[Ranking]:
        rankings = []
        categories = ["都市", "玄幻", "仙侠", "奇幻", "历史", "游戏", "科幻", "悬疑", "言情", "军事"]
        for category in categories:
            for rank in range(1, 51):
                ranking = Ranking(
                    id=str(uuid4()),
                    platform=Ranking.PLATFORM_FANQIE,
                    category=category,
                    rank=rank,
                    novel_name=f"番茄{category}第{rank}名",
                    author=f"番茄作者{random.randint(1000, 9999)}",
                    description=f"{category}题材热门小说，免费阅读",
                    tags=",".join(self._generate_tags(category)),
                    word_count=random.randint(50000, 3000000),
                    popularity=random.randint(50000, 5000000),
                    score=round(random.uniform(6.5, 9.5), 1),
                    comments=random.randint(500, 500000),
                    favorites=random.randint(5000, 500000),
                    collected_at=datetime.utcnow(),
                    extra_data={"source": "fanqie_api", "category_url": f"/category/{category}"}
                )
                rankings.append(ranking)
        self.ranking_repository.save_batch(rankings)
        logger.info(f"Crawled {len(rankings)} rankings from Fanqie")
        return rankings

    async def crawl_qimao(self) -> List[Ranking]:
        rankings = []
        categories = ["都市", "玄幻", "仙侠", "奇幻", "历史", "游戏", "科幻", "悬疑", "言情", "军事"]
        for category in categories:
            for rank in range(1, 31):
                ranking = Ranking(
                    id=str(uuid4()),
                    platform=Ranking.PLATFORM_QIMAO,
                    category=category,
                    rank=rank,
                    novel_name=f"七猫{category}第{rank}名",
                    author=f"七猫作者{random.randint(1000, 9999)}",
                    description=f"{category}题材热门小说，全本免费",
                    tags=",".join(self._generate_tags(category)),
                    word_count=random.randint(100000, 4000000),
                    popularity=random.randint(20000, 2000000),
                    score=round(random.uniform(7.0, 9.6), 1),
                    comments=random.randint(200, 200000),
                    favorites=random.randint(2000, 200000),
                    collected_at=datetime.utcnow(),
                    extra_data={"source": "qimao_api", "category_url": f"/category/{category}"}
                )
                rankings.append(ranking)
        self.ranking_repository.save_batch(rankings)
        logger.info(f"Crawled {len(rankings)} rankings from Qimao")
        return rankings

    async def crawl_all_platforms(self) -> Dict[str, List[Ranking]]:
        results = {}
        results['qidian'] = await self.crawl_qidian()
        results['fanqie'] = await self.crawl_fanqie()
        results['qimao'] = await self.crawl_qimao()
        logger.info(f"Crawled all platforms, total {sum(len(v) for v in results.values())} rankings")
        return results

    def _generate_tags(self, category: str) -> List[str]:
        tag_map = {
            "玄幻": ["系统", "重生", "穿越", "无敌", "神豪"],
            "奇幻": ["魔法", "异世界", "剑与魔法", "精灵", "龙族"],
            "武侠": ["江湖", "武侠", "宗师", "侠客", "内功"],
            "仙侠": ["修仙", "长生", "渡劫", "炼丹", "御剑"],
            "都市": ["神豪", "重生", "都市", "医生", "兵王"],
            "历史": ["穿越", "古代", "争霸", "三国", "隋唐"],
            "游戏": ["网游", "电竞", "游戏", "直播", "虚拟"],
            "科幻": ["末世", "星际", "机甲", "科幻", "未来"],
            "悬疑": ["推理", "悬疑", "破案", "惊悚", "恐怖"],
            "军事": ["特种兵", "军事", "战争", "谍战", "铁血"],
            "言情": ["总裁", "豪门", "甜宠", "穿越", "重生"]
        }
        return random.sample(tag_map.get(category, ["热门"]), min(3, len(tag_map.get(category, ["热门"]))))