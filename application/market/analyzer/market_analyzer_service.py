import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
from uuid import uuid4
from collections import Counter
from domain.market.entities.ranking import Ranking
from domain.market.entities.hot_topic import HotTopic
from domain.market.entities.market_analysis import MarketAnalysis, GenreTrend
from domain.market.repositories.ranking_repository import RankingRepository
from domain.market.repositories.hot_topic_repository import HotTopicRepository
from domain.market.repositories.market_analysis_repository import MarketAnalysisRepository
from domain.ai.services.llm_service import LLMService

logger = logging.getLogger(__name__)


class MarketAnalyzerService:
    def __init__(
        self,
        ranking_repository: RankingRepository,
        hot_topic_repository: HotTopicRepository,
        market_analysis_repository: MarketAnalysisRepository,
        llm_service: LLMService = None
    ):
        self.ranking_repository = ranking_repository
        self.hot_topic_repository = hot_topic_repository
        self.market_analysis_repository = market_analysis_repository
        self.llm_service = llm_service

    def analyze_rankings(self, days: int = 7) -> Dict[str, Any]:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        rankings = self.ranking_repository.get_by_date_range(start_date, end_date)
        
        if not rankings:
            return {"error": "No ranking data found"}
        
        return self._compute_ranking_stats(rankings)

    def analyze_hot_topics(self, days: int = 7) -> Dict[str, Any]:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        hot_topics = self.hot_topic_repository.get_by_date_range(start_date, end_date)
        
        if not hot_topics:
            return {"error": "No hot topic data found"}
        
        return self._compute_hot_topic_stats(hot_topics)

    async def generate_full_analysis(self, days: int = 7) -> MarketAnalysis:
        logger.info("Starting full market analysis...")
        
        end_date = datetime.utcnow()
        
        ranking_stats = self.analyze_rankings(days)
        hot_topic_stats = self.analyze_hot_topics(days)
        
        genre_trends = self._calculate_genre_trends(ranking_stats)
        
        recommendations = self._generate_recommendations(genre_trends, hot_topic_stats)
        
        ai_explanation = ""
        if self.llm_service:
            ai_explanation = await self._generate_ai_explanation(genre_trends, recommendations)
        
        analysis = MarketAnalysis(
            id=str(uuid4()),
            analysis_date=end_date,
            platform_summary=ranking_stats.get('platform_summary', {}),
            genre_trends=genre_trends,
            hot_topics_summary=hot_topic_stats,
            recommendations=recommendations,
            ai_explanation=ai_explanation
        )
        
        self.market_analysis_repository.save(analysis)
        logger.info("Market analysis completed and saved")
        
        return analysis

    def _compute_ranking_stats(self, rankings: List[Ranking]) -> Dict[str, Any]:
        stats = {
            "total_rankings": len(rankings),
            "platform_summary": {},
            "genre_stats": {},
            "tag_stats": {},
            "average_word_count": 0,
            "average_score": 0,
            "popularity_distribution": {}
        }
        
        platform_counter = Counter()
        genre_counter = Counter()
        tag_counter = Counter()
        word_counts = []
        scores = []
        popularity_values = []
        
        for r in rankings:
            platform_counter[r.platform] += 1
            genre_counter[r.category] += 1
            if r.tags:
                tags = [t.strip() for t in r.tags.split(",") if t.strip()]
                tag_counter.update(tags)
            if r.word_count:
                word_counts.append(r.word_count)
            if r.score:
                scores.append(r.score)
            if r.popularity:
                popularity_values.append(r.popularity)
        
        stats["platform_summary"] = dict(platform_counter)
        
        for genre, count in genre_counter.most_common(20):
            stats["genre_stats"][genre] = {
                "count": count,
                "percentage": round(count / len(rankings) * 100, 2)
            }
        
        for tag, count in tag_counter.most_common(30):
            stats["tag_stats"][tag] = count
        
        stats["average_word_count"] = round(sum(word_counts) / len(word_counts)) if word_counts else 0
        stats["average_score"] = round(sum(scores) / len(scores), 2) if scores else 0
        
        if popularity_values:
            stats["popularity_distribution"] = {
                "min": min(popularity_values),
                "max": max(popularity_values),
                "average": round(sum(popularity_values) / len(popularity_values)),
                "median": sorted(popularity_values)[len(popularity_values) // 2]
            }
        
        return stats

    def _compute_hot_topic_stats(self, hot_topics: List[HotTopic]) -> Dict[str, Any]:
        stats = {
            "total_topics": len(hot_topics),
            "source_summary": {},
            "category_stats": {},
            "hot_keywords": [],
            "average_hot_value": 0,
            "top_topics": []
        }
        
        source_counter = Counter()
        category_counter = Counter()
        keyword_counter = Counter()
        hot_values = []
        
        for ht in hot_topics:
            source_counter[ht.source] += 1
            category_counter[ht.category] += 1
            if ht.keywords:
                keyword_counter.update(ht.keywords)
            if ht.hot_value:
                hot_values.append(ht.hot_value)
        
        stats["source_summary"] = dict(source_counter)
        
        for category, count in category_counter.most_common(10):
            stats["category_stats"][category] = {
                "count": count,
                "percentage": round(count / len(hot_topics) * 100, 2)
            }
        
        stats["hot_keywords"] = [kw for kw, _ in keyword_counter.most_common(20)]
        stats["average_hot_value"] = round(sum(hot_values) / len(hot_values)) if hot_values else 0
        
        sorted_topics = sorted(hot_topics, key=lambda x: x.hot_value or 0, reverse=True)[:10]
        stats["top_topics"] = [
            {"title": t.title, "source": t.source, "rank": t.rank, "hot_value": t.hot_value}
            for t in sorted_topics
        ]
        
        return stats

    def _calculate_genre_trends(self, ranking_stats: Dict[str, Any]) -> List[GenreTrend]:
        trends = []
        
        genre_stats = ranking_stats.get("genre_stats", {})
        tag_stats = ranking_stats.get("tag_stats", {})
        
        sorted_genres = sorted(genre_stats.items(), key=lambda x: x[1]["count"], reverse=True)
        
        for rank, (genre, stats) in enumerate(sorted_genres[:10], 1):
            trend_value = self._calculate_trend_value(genre, tag_stats)
            trend = GenreTrend.TREND_UP if trend_value > 5 else (GenreTrend.TREND_DOWN if trend_value < -5 else GenreTrend.TREND_STABLE)
            
            hot_tags = self._get_hot_tags_for_genre(genre, tag_stats)
            
            trend_entity = GenreTrend(
                id=str(uuid4()),
                genre=genre,
                rank=rank,
                popularity_score=stats["percentage"],
                trend=trend,
                trend_value=trend_value,
                hot_tags=hot_tags,
                analysis_date=datetime.utcnow()
            )
            trends.append(trend_entity)
        
        return trends

    def _calculate_trend_value(self, genre: str, tag_stats: Dict[str, int]) -> float:
        trend_tags = {
            "玄幻": ["系统", "重生", "无敌"],
            "都市": ["神豪", "重生", "直播"],
            "仙侠": ["修仙", "长生", "渡劫"],
            "历史": ["穿越", "争霸", "种田"],
            "游戏": ["网游", "电竞", "直播"],
            "科幻": ["末世", "星际", "机甲"],
            "悬疑": ["推理", "破案", "惊悚"],
            "娱乐": ["明星", "综艺", "直播"],
            "武侠": ["江湖", "宗师", "内功"],
            "奇幻": ["魔法", "异世界", "精灵"]
        }
        
        genre_tags = trend_tags.get(genre, [])
        total_tag_count = sum(tag_stats.get(tag, 0) for tag in genre_tags)
        
        if total_tag_count == 0:
            return 0.0
        
        max_tag_count = max(tag_stats.values()) if tag_stats else 1
        return round((total_tag_count / max_tag_count) * 20 - 10, 2)

    def _get_hot_tags_for_genre(self, genre: str, tag_stats: Dict[str, int]) -> List[str]:
        genre_tag_map = {
            "玄幻": ["系统", "重生", "穿越", "无敌", "神豪"],
            "都市": ["神豪", "重生", "都市", "医生", "兵王", "直播"],
            "仙侠": ["修仙", "长生", "渡劫", "炼丹", "御剑"],
            "历史": ["穿越", "古代", "争霸", "三国", "隋唐", "种田"],
            "游戏": ["网游", "电竞", "游戏", "直播", "虚拟"],
            "科幻": ["末世", "星际", "机甲", "科幻", "未来"],
            "悬疑": ["推理", "悬疑", "破案", "惊悚", "恐怖"],
            "娱乐": ["明星", "综艺", "直播", "总裁", "豪门"],
            "武侠": ["江湖", "武侠", "宗师", "侠客", "内功"],
            "奇幻": ["魔法", "异世界", "剑与魔法", "精灵", "龙族"]
        }
        
        genre_tags = genre_tag_map.get(genre, [])
        sorted_tags = sorted(genre_tags, key=lambda x: tag_stats.get(x, 0), reverse=True)
        return sorted_tags[:5]

    def _generate_recommendations(self, genre_trends: List[GenreTrend], hot_topic_stats: Dict[str, Any]) -> List[Dict[str, Any]]:
        recommendations = []
        
        hot_categories = hot_topic_stats.get("category_stats", {})
        
        for trend in genre_trends[:6]:
            hot_value = hot_categories.get(trend.genre, {}).get("percentage", 0)
            
            score = self._calculate_recommendation_score(trend, hot_value)
            
            recommendation = {
                "genre": trend.genre,
                "score": score,
                "stars": self._score_to_stars(score),
                "trend": trend.trend,
                "trend_value": trend.trend_value,
                "hot_topics": trend.hot_tags,
                "reason": self._generate_reason(trend, hot_value)
            }
            recommendations.append(recommendation)
        
        return sorted(recommendations, key=lambda x: x["score"], reverse=True)

    def _calculate_recommendation_score(self, trend: GenreTrend, hot_value: float) -> float:
        score = 0.0
        
        score += trend.popularity_score * 4
        
        if trend.trend == GenreTrend.TREND_UP:
            score += min(trend.trend_value, 10) * 3
        elif trend.trend == GenreTrend.TREND_DOWN:
            score += max(trend.trend_value, -10) * 2
        
        score += hot_value * 3
        
        return min(100, max(0, round(score, 2)))

    def _score_to_stars(self, score: float) -> str:
        if score >= 90:
            return "★★★★★"
        elif score >= 80:
            return "★★★★☆"
        elif score >= 70:
            return "★★★☆☆"
        elif score >= 60:
            return "★★☆☆☆"
        else:
            return "★☆☆☆☆"

    def _generate_reason(self, trend: GenreTrend, hot_value: float) -> str:
        reasons = []
        
        if trend.trend == GenreTrend.TREND_UP:
            reasons.append(f"最近热度上涨{trend.trend_value:.1f}%")
        elif trend.trend == GenreTrend.TREND_STABLE:
            reasons.append("热度保持稳定")
        else:
            reasons.append(f"热度有所下降{abs(trend.trend_value):.1f}%")
        
        if hot_value > 15:
            reasons.append("当前热点匹配度高")
        elif hot_value > 10:
            reasons.append("有一定热点匹配度")
        
        if trend.hot_tags:
            reasons.append(f"热门标签：{', '.join(trend.hot_tags[:3])}")
        
        return "，".join(reasons)

    async def _generate_ai_explanation(self, genre_trends: List[GenreTrend], recommendations: List[Dict[str, Any]]) -> str:
        prompt = f"""
你是一个网文市场分析专家，请根据以下数据生成一份趋势分析报告：

【题材趋势数据】
{json.dumps([{"genre": t.genre, "trend": t.trend, "trend_value": t.trend_value, "hot_tags": t.hot_tags} for t in genre_trends], ensure_ascii=False)}

【推荐数据】
{json.dumps(recommendations, ensure_ascii=False)}

请分析：
1. 为什么最近都市神豪题材上涨？
2. 为什么某些题材热度下降？
3. 当前有哪些新兴题材值得关注？
4. 给作者的创作建议是什么？

请用简洁明了的语言回答，不要超过500字。
"""
        try:
            result = await self.llm_service.generate(prompt)
            return result.content.strip() if hasattr(result, 'content') else str(result)
        except Exception as e:
            logger.warning(f"Failed to generate AI explanation: {e}")
            return ""