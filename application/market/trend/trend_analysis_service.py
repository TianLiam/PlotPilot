"""趋势分析服务 - 分析历史数据并生成趋势预测"""
import logging
from collections import Counter
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from statistics import mean, stdev

from domain.market.entities.trend_snapshot import (
    RankingSnapshot,
    RankingSnapshotItem,
    GenreTrend,
    TrendAlert,
)
from domain.market.repositories.snapshot_repository import (
    SnapshotRepository,
    TrendAlertRepository,
)
from infrastructure.persistence.database.connection import DatabaseConnection

logger = logging.getLogger(__name__)


class TrendAnalysisService:
    """趋势分析服务
    
    核心算法：
    1. 热度分计算：根据排名、字数、热度、评分综合评分
    2. 趋势方向：对比历史数据计算涨跌
    3. 趋势强度：使用线性回归斜率或连续天数
    4. 预警生成：检测连续上涨/下跌超过阈值
    """
    
    # 趋势阈值
    RISING_THRESHOLD = 5.0          # 涨幅超过5%判定为上涨
    DECLINING_THRESHOLD = -5.0      # 跌幅超过5%判定为下跌
    STRONG_RISING_THRESHOLD = 15.0  # 强上涨
    STRONG_DECLINING_THRESHOLD = -15.0  # 强下跌
    SURGE_THRESHOLD = 30.0          # 暴涨阈值
    DECLINE_THRESHOLD = -30.0       # 暴跌阈值
    CONTINUOUS_DAYS = 3             # 连续天数触发预警
    
    def __init__(
        self,
        snapshot_repo: SnapshotRepository,
        alert_repo: TrendAlertRepository,
    ):
        self.snapshot_repo = snapshot_repo
        self.alert_repo = alert_repo
    
    async def save_daily_snapshot(
        self,
        platform: str,
        category: str,
        items: List[Dict[str, Any]],
    ) -> RankingSnapshot:
        """保存每日快照
        
        Args:
            platform: 平台
            category: 分类
            items: 榜单数据，每项包含 novel_id, novel_name, rank, popularity 等
        
        Returns:
            保存的快照
        """
        today = datetime.utcnow().strftime("%Y-%m-%d")
        
        snapshot_items = []
        for item in items:
            snapshot_items.append(RankingSnapshotItem(
                platform=platform,
                category=category,
                novel_id=str(item.get("novel_id") or item.get("bookId") or item.get("book_id", "")),
                novel_name=item.get("novel_name") or item.get("bookName") or item.get("name", ""),
                author=item.get("author") or item.get("authorName", ""),
                rank=item.get("rank") or item.get("index", 0),
                word_count=item.get("word_count") or item.get("wordCount", 0),
                popularity=item.get("popularity") or item.get("totalRead", 0),
                score=item.get("score", 0.0),
                tags=list(item.get("tags") or []),
            ))
        
        snapshot = RankingSnapshot(
            snapshot_date=today,
            platform=platform,
            category=category,
            items=snapshot_items,
            total_count=len(snapshot_items),
        )
        
        await self.snapshot_repo.save_ranking_snapshot(snapshot)
        logger.info(f"Saved snapshot: {today} {platform}/{category} - {len(snapshot_items)} items")
        
        return snapshot

    async def save_crawl_snapshots(self, rankings_by_platform: Dict[str, List[Any]]) -> int:
        """Persist verified crawler entities as today's per-category snapshots."""
        saved_count = 0
        for platform, rankings in rankings_by_platform.items():
            rankings_by_category: Dict[str, List[Any]] = {}
            for item in rankings:
                category = str(getattr(item, "category", "") or "").strip()
                if category:
                    rankings_by_category.setdefault(category, []).append(item)

            for category, category_items in rankings_by_category.items():
                snapshot_items = []
                for item in sorted(
                    category_items,
                    key=lambda value: int(getattr(value, "rank", 0) or 0),
                )[:50]:
                    raw_tags = getattr(item, "tags", "") or ""
                    tags = (
                        [str(tag).strip() for tag in raw_tags if str(tag).strip()]
                        if isinstance(raw_tags, list)
                        else [tag.strip() for tag in str(raw_tags).split(",") if tag.strip()]
                    )
                    extra_data = getattr(item, "extra_data", {}) or {}
                    snapshot_items.append(
                        {
                            "novel_id": str(extra_data.get("book_id") or getattr(item, "id", "")),
                            "novel_name": getattr(item, "novel_name", ""),
                            "author": getattr(item, "author", ""),
                            "rank": int(getattr(item, "rank", 0) or 0),
                            "word_count": int(getattr(item, "word_count", 0) or 0),
                            "popularity": int(getattr(item, "popularity", 0) or 0),
                            "score": float(getattr(item, "score", 0.0) or 0.0),
                            "tags": tags,
                        }
                    )
                if snapshot_items:
                    await self.save_daily_snapshot(platform, category, snapshot_items)
                    saved_count += 1
        return saved_count
    
    async def analyze_genre_trend(
        self,
        platform: str,
        category: str,
        days: int = 7,
    ) -> Optional[GenreTrend]:
        """分析某题材的趋势
        
        Args:
            platform: 平台
            category: 分类
            days: 分析最近N天
        
        Returns:
            趋势分析结果
        """
        history = await self.snapshot_repo.get_ranking_history(platform, category, days)
        
        if not history:
            logger.debug(f"No history for {platform}/{category}")
            return None
        
        # 按日期排序（从旧到新）
        history = sorted(history, key=lambda s: s.snapshot_date)
        
        # 计算每日热度分
        daily_scores = []
        daily_top_ranks = []
        history_points = []
        
        for snapshot in history:
            score = self._calculate_genre_score(snapshot)
            top_rank = self._get_top_rank(snapshot)
            
            daily_scores.append(score)
            daily_top_ranks.append(top_rank)
            history_points.append({
                "date": snapshot.snapshot_date,
                "score": round(score, 2),
                "top_rank": top_rank,
                "novel_count": snapshot.total_count,
            })
        
        # 当前数据
        current_score = daily_scores[-1] if daily_scores else 0.0
        current_top_rank = daily_top_ranks[-1] if daily_top_ranks else 999
        
        # 计算变化
        change_1d = self._calculate_change(daily_scores, 1)
        change_3d = self._calculate_change(daily_scores, 3)
        change_7d = self._calculate_change(daily_scores, min(7, len(daily_scores) - 1))
        
        # 判断趋势
        trend, trend_strength = self._determine_trend(daily_scores)
        
        # 判断预警等级
        alert_level, alert_message = self._determine_alert(
            change_1d, change_3d, change_7d, trend, daily_scores
        )
        
        return GenreTrend(
            genre=category,
            platform=platform,
            current_score=current_score,
            current_top_rank=current_top_rank,
            score_change_1d=change_1d,
            score_change_3d=change_3d,
            score_change_7d=change_7d,
            trend=trend,
            trend_strength=trend_strength,
            alert_level=alert_level,
            alert_message=alert_message,
            history=history_points,
        )
    
    def _calculate_genre_score(self, snapshot: RankingSnapshot) -> float:
        """计算题材热度分
        
        公式：
        - 排名分（50%）：排名越前分越高
        - 热度分（30%）：总热度值
        - 评分分（20%）：平均评分
        """
        if not snapshot.items:
            return 0.0
        
        # 排名分（前10名加权）
        rank_score = 0.0
        for item in snapshot.items[:20]:
            # rank 1 = 100分, rank 20 = 50分
            rank_score += max(0, 100 - (item.rank - 1) * 5)
        
        rank_score = rank_score / 20  # 归一化
        
        # 热度分（对数处理）
        total_popularity = sum(item.popularity for item in snapshot.items)
        if total_popularity > 0:
            import math
            pop_score = math.log10(total_popularity + 1) * 20
        else:
            pop_score = 0.0
        
        # 评分分
        scores = [item.score for item in snapshot.items if item.score > 0]
        avg_score = mean(scores) * 20 if scores else 0.0  # 假设评分0-5
        
        # 综合分
        total = rank_score * 0.5 + pop_score * 0.3 + avg_score * 0.2
        return round(total, 2)
    
    def _get_top_rank(self, snapshot: RankingSnapshot) -> int:
        """获取最高排名"""
        if not snapshot.items:
            return 999
        return min(item.rank for item in snapshot.items if item.rank > 0)
    
    def _calculate_change(self, scores: List[float], days_back: int) -> float:
        """计算N天前的变化率"""
        if len(scores) < days_back + 1:
            return 0.0
        
        current = scores[-1]
        past = scores[-(days_back + 1)]
        
        if past == 0:
            return 0.0
        
        return round((current - past) / past * 100, 2)
    
    def _determine_trend(self, scores: List[float]) -> Tuple[str, float]:
        """判断趋势方向和强度
        
        使用线性回归计算趋势强度
        """
        if len(scores) < 2:
            return "stable", 0.0
        
        # 计算斜率
        n = len(scores)
        x = list(range(n))
        x_mean = mean(x)
        y_mean = mean(scores)
        
        if y_mean == 0:
            return "stable", 0.0
        
        numerator = sum((x[i] - x_mean) * (scores[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return "stable", 0.0
        
        slope = numerator / denominator
        # 归一化强度：相对于平均值的百分比变化率
        strength = abs(slope * (n - 1) / y_mean * 100) if y_mean != 0 else 0
        strength = min(1.0, strength / 50)  # 归一化到0-1
        
        if slope > 1:  # 上升
            return "rising", round(strength, 2)
        elif slope < -1:  # 下降
            return "declining", round(strength, 2)
        else:
            return "stable", round(strength, 2)
    
    def _determine_alert(
        self,
        change_1d: float,
        change_3d: float,
        change_7d: float,
        trend: str,
        scores: List[float],
    ) -> Tuple[str, str]:
        """判断预警等级和消息"""
        # 暴涨/暴跌
        if change_1d >= self.SURGE_THRESHOLD:
            return "warning", f"⚡ 单日暴涨 {change_1d:.1f}%，建议立即关注"
        if change_1d <= self.DECLINE_THRESHOLD:
            return "danger", f"📉 单日暴跌 {abs(change_1d):.1f}%，可能正在退潮"
        
        # 连续3天大幅变化
        if len(scores) >= 4:
            recent_3d = scores[-3:]
            is_rising_3d = all(
                recent_3d[i] > recent_3d[i-1] 
                for i in range(1, len(recent_3d))
            )
            is_declining_3d = all(
                recent_3d[i] < recent_3d[i-1] 
                for i in range(1, len(recent_3d))
            )
            
            if is_rising_3d and change_3d >= 10:
                return "warning", f"📈 连续3天上涨，累计 {change_3d:.1f}%，处于上升通道"
            if is_declining_3d and change_3d <= -10:
                return "warning", f"📉 连续3天下跌，累计 {abs(change_3d):.1f}%，需要警惕"
        
        # 7天趋势
        if change_7d >= self.STRONG_RISING_THRESHOLD:
            return "info", f"📈 7天上涨 {change_7d:.1f}%，趋势向好"
        if change_7d <= self.STRONG_DECLINING_THRESHOLD:
            return "warning", f"📉 7天下跌 {abs(change_7d):.1f}%，热度消退"
        
        return "normal", ""
    
    async def analyze_all_genres(
        self,
        platform: str,
        categories: List[str],
        days: int = 7,
    ) -> List[GenreTrend]:
        """分析所有题材的趋势"""
        trends = []
        
        for category in categories:
            try:
                trend = await self.analyze_genre_trend(platform, category, days)
                if trend:
                    trends.append(trend)
            except Exception as e:
                logger.error(f"Failed to analyze {platform}/{category}: {e}")
        
        return trends
    
    async def generate_alerts_from_trends(
        self,
        trends: List[GenreTrend],
    ) -> List[TrendAlert]:
        """从趋势数据生成预警"""
        alerts = []
        
        for trend in trends:
            if trend.alert_level == "normal":
                continue
            
            # 判断预警类型
            if trend.trend == "rising" and trend.score_change_3d >= 10:
                alert_type = "rising"
            elif trend.trend == "declining" and trend.score_change_3d <= -10:
                alert_type = "declining"
            elif trend.score_change_1d >= self.SURGE_THRESHOLD:
                alert_type = "surge"
            elif trend.score_change_1d <= self.DECLINE_THRESHOLD:
                alert_type = "decline"
            else:
                continue
            
            alert = TrendAlert(
                alert_type=alert_type,
                severity=trend.alert_level,
                genre=trend.genre,
                platform=trend.platform,
                message=trend.alert_message,
                change_value=trend.score_change_1d,
                duration_days=0,
            )
            
            try:
                await self.alert_repo.save_alert(alert)
                alerts.append(alert)
            except Exception as e:
                logger.error(f"Failed to save alert: {e}")
        
        return alerts
    
    async def get_rising_genres(
        self,
        platform: Optional[str] = None,
        min_change: float = 5.0,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """获取正在上涨的题材"""
        # 这里简化实现：从活跃预警中获取
        all_alerts = await self.alert_repo.list_active_alerts(limit * 2)
        
        rising_alerts = [
            a for a in all_alerts
            if a.alert_type in ("rising", "surge") and a.change_value >= min_change
            and (platform is None or a.platform == platform)
        ]
        
        return [
            {
                "genre": a.genre,
                "platform": a.platform,
                "change_value": a.change_value,
                "message": a.message,
                "severity": a.severity,
                "created_at": a.created_at.isoformat(),
            }
            for a in rising_alerts[:limit]
        ]
    
    async def get_declining_genres(
        self,
        platform: Optional[str] = None,
        max_change: float = -5.0,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """获取正在下跌的题材"""
        all_alerts = await self.alert_repo.list_active_alerts(limit * 2)
        
        declining_alerts = [
            a for a in all_alerts
            if a.alert_type in ("declining", "decline") and a.change_value <= max_change
            and (platform is None or a.platform == platform)
        ]
        
        return [
            {
                "genre": a.genre,
                "platform": a.platform,
                "change_value": a.change_value,
                "message": a.message,
                "severity": a.severity,
                "created_at": a.created_at.isoformat(),
            }
            for a in declining_alerts[:limit]
        ]
    
    async def get_genre_history(
        self,
        platform: str,
        category: str,
        days: int = 30,
    ) -> Dict[str, Any]:
        """获取题材的详细历史数据"""
        history = await self.snapshot_repo.get_ranking_history(platform, category, days)
        
        history_points = []
        for snapshot in sorted(history, key=lambda s: s.snapshot_date):
            score = self._calculate_genre_score(snapshot)
            history_points.append({
                "date": snapshot.snapshot_date,
                "score": round(score, 2),
                "novel_count": snapshot.total_count,
                "top_novel": snapshot.items[0].novel_name if snapshot.items else "",
            })
        
        trend = await self.analyze_genre_trend(platform, category, days)
        
        return {
            "platform": platform,
            "genre": category,
            "days": days,
            "data_points": history_points,
            "trend": trend.to_dict() if trend else None,
        }

    async def get_dashboard(self, days: int = 30) -> Dict[str, Any]:
        """Build the trend dashboard exclusively from persisted daily snapshots."""
        series = await self.snapshot_repo.list_ranking_series(days)
        if not series:
            return {
                "days": days,
                "data_state": "empty",
                "snapshot_count": 0,
                "series_count": 0,
                "rising": [],
                "declining": [],
                "hot": [],
                "line_series": [],
                "heatmap": [],
                "hot_tags": [],
            }

        trend_rows: List[Dict[str, Any]] = []
        heatmap: List[Dict[str, Any]] = []
        tag_counter: Counter = Counter()
        snapshot_count = 0

        for item in series:
            platform = item["platform"]
            category = item["category"]
            history_points = int(item.get("history_points") or 0)
            snapshot_count += history_points
            trend = await self.analyze_genre_trend(platform, category, days)
            if not trend:
                continue

            change = trend.score_change_7d
            if history_points < 8:
                change = trend.score_change_3d if history_points >= 4 else trend.score_change_1d

            row = {
                **trend.to_dict(),
                "change_value": change,
                "history": trend.history,
            }
            trend_rows.append(row)
            heatmap.append({
                "platform": platform,
                "genre": category,
                "score": round(trend.current_score, 2),
            })

            latest = await self.snapshot_repo.get_ranking_snapshot(
                item["latest_date"], platform, category
            )
            if latest:
                for ranking in latest.items:
                    tag_counter.update(tag for tag in ranking.tags if tag and tag != category)

        rising = sorted(
            (row for row in trend_rows if row["change_value"] > 0),
            key=lambda row: row["change_value"],
            reverse=True,
        )[:5]
        declining = sorted(
            (row for row in trend_rows if row["change_value"] < 0),
            key=lambda row: row["change_value"],
        )[:5]
        hot = sorted(trend_rows, key=lambda row: row["current_score"], reverse=True)[:5]
        line_series = [
            {
                "platform": row["platform"],
                "genre": row["genre"],
                "data_points": row["history"],
            }
            for row in hot
        ]

        max_history = max((int(item.get("history_points") or 0) for item in series), default=0)
        return {
            "days": days,
            "data_state": "historical" if max_history >= 2 else "single_snapshot",
            "snapshot_count": snapshot_count,
            "series_count": len(trend_rows),
            "rising": rising,
            "declining": declining,
            "hot": hot,
            "line_series": line_series,
            "heatmap": heatmap,
            "hot_tags": [
                {"name": name, "value": count}
                for name, count in tag_counter.most_common(10)
            ],
        }
