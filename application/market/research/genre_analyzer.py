"""题材成功率分析器 - 基于历史样本分析"""
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from statistics import mean, median, stdev
from collections import Counter

from domain.market.entities.novel_research import (
    HistoricalSample,
    GenreStats,
    OpeningPattern,
)
from domain.market.entities.dynamic_template import DiscoveredTemplate, TemplateType
from domain.market.repositories.dynamic_template_repository import DynamicTemplateRepository
from infrastructure.persistence.database.market.sqlite_historical_sample_repository import HistoricalSampleRepository

logger = logging.getLogger(__name__)


class GenreSuccessAnalyzer:
    """题材成功率分析器
    
    核心功能：
    1. 成功率统计：基于历史样本的成功率
    2. 字数/章节分布：推荐最佳字数和章节长度
    3. 表现分析：平均排名、热度、在榜天数
    4. 开局模式提取：哪些开局最成功
    """
    
    # 成功标准
    SUCCESS_RANK_THRESHOLD = 100        # 进入前100名算成功
    SUCCESS_POPULARITY_THRESHOLD = 10000  # 热度超过1万算成功
    SUCCESS_DAYS_THRESHOLD = 7          # 在榜超过7天算稳定
    
    def __init__(self, sample_repo: HistoricalSampleRepository):
        self.sample_repo = sample_repo
    
    async def analyze_genre(self, genre: str) -> Optional[GenreStats]:
        """分析单题材统计"""
        try:
            all_samples = await self.sample_repo.find_by_genre(
                genres=[genre],
                successful_only=False,
                limit=500,
            )
            
            if not all_samples:
                return None
            
            successful = [s for s in all_samples if s.is_successful]
            
            word_counts = [s.word_count for s in successful if s.word_count > 0]
            chapter_counts = [s.chapter_count for s in successful if s.chapter_count > 0]
            chapter_word_counts = [s.avg_chapter_words for s in successful if s.avg_chapter_words > 0]
            peak_ranks = [s.peak_rank for s in successful if s.peak_rank < 999]
            popularities = [s.popularity for s in successful if s.popularity > 0]
            days_on_chart = [s.days_on_chart for s in successful if s.days_on_chart > 0]
            
            # 字数标准差
            wc_std = stdev(word_counts) if len(word_counts) > 1 else 0.0
            
            # 推荐章节字数（取中位数）
            optimal_chapter_words = int(median(chapter_word_counts)) if chapter_word_counts else 2000
            
            # 趋势判断
            trend_counter = Counter(s.trend_direction for s in all_samples)
            most_common_trend = trend_counter.most_common(1)[0][0] if trend_counter else "stable"
            
            # 趋势变化（简化：基于上升/下降比例）
            trend_change = 0.0
            if all_samples:
                rising_count = sum(1 for s in all_samples if s.trend_direction == "rising")
                declining_count = sum(1 for s in all_samples if s.trend_direction == "declining")
                trend_change = (rising_count - declining_count) / len(all_samples) * 100
            
            return GenreStats(
                genre=genre,
                total_novels=len(all_samples),
                successful_novels=len(successful),
                success_rate=len(successful) / len(all_samples) if all_samples else 0.0,
                avg_word_count=int(mean(word_counts)) if word_counts else 0,
                median_word_count=int(median(word_counts)) if word_counts else 0,
                word_count_std=wc_std,
                avg_chapter_count=int(mean(chapter_counts)) if chapter_counts else 0,
                avg_chapter_words=int(mean(chapter_word_counts)) if chapter_word_counts else 0,
                optimal_chapter_words=optimal_chapter_words,
                avg_peak_rank=mean(peak_ranks) if peak_ranks else 0,
                avg_popularity=mean(popularities) if popularities else 0,
                avg_days_on_chart=mean(days_on_chart) if days_on_chart else 0,
                trend=most_common_trend,
                trend_change=trend_change,
            )
            
        except Exception as e:
            logger.error(f"Failed to analyze genre {genre}: {e}")
            return None
    
    async def analyze_multiple_genres(
        self,
        genres: List[str],
    ) -> List[GenreStats]:
        """分析多题材"""
        results = []
        for genre in genres:
            stats = await self.analyze_genre(genre)
            if stats:
                results.append(stats)
        return results
    
    async def extract_opening_patterns(
        self,
        genre: str,
        top_n: int = 5,
    ) -> List[OpeningPattern]:
        """提取成功开局模式"""
        samples = await self.sample_repo.find_by_genre(
            genres=[genre],
            successful_only=True,
            limit=200,
        )
        
        if not samples:
            return []
        
        # 按opening_type分组
        opening_groups: Dict[str, List[HistoricalSample]] = {}
        for sample in samples:
            ot = sample.opening_type or "未知"
            if ot not in opening_groups:
                opening_groups[ot] = []
            opening_groups[ot].append(sample)
        
        patterns = []
        for opening_type, group_samples in opening_groups.items():
            if opening_type == "未知":
                continue
            
            popularities = [s.popularity for s in group_samples if s.popularity > 0]
            
            # 提取关键点（简化：基于金手指和标签的统计）
            all_gfs = []
            for s in group_samples:
                all_gfs.extend(s.golden_fingers)
            gf_counter = Counter(all_gfs)
            key_points = [f"使用 {gf[0]}" for gf in gf_counter.most_common(3)]
            
            pattern = OpeningPattern(
                name=opening_type,
                description=f"{genre}题材中常见的{opening_type}开局",
                success_count=len(group_samples),
                total_count=len(samples),
                success_rate=len(group_samples) / len(samples),
                avg_popularity=mean(popularities) if popularities else 0,
                sample_novels=[s.novel_name for s in group_samples[:5]],
                chapter_range="1-3",
                key_points=key_points,
            )
            patterns.append(pattern)
        
        # 按成功率排序
        patterns.sort(key=lambda p: p.success_rate, reverse=True)
        return patterns[:top_n]
    
    async def compute_combination_success(
        self,
        genres: List[str],
        golden_fingers: List[str] = None,
    ) -> Dict[str, Any]:
        """计算题材组合的成功率
        
        Args:
            genres: 题材列表
            golden_fingers: 金手指列表（可选）
        
        Returns:
            组合分析结果
        """
        # 查找符合所有题材的样本
        samples = await self.sample_repo.find_by_tags(
            tags=genres,
            successful_only=False,
            limit=500,
        )
        
        # 进一步按金手指筛选
        if golden_fingers:
            filtered = []
            for s in samples:
                if any(gf in s.golden_fingers for gf in golden_fingers):
                    filtered.append(s)
            samples = filtered
        
        if not samples:
            return {
                "total_samples": 0,
                "success_rate": 0.0,
                "message": "暂无样本数据",
            }
        
        successful = [s for s in samples if s.is_successful]
        success_rate = len(successful) / len(samples) if samples else 0.0
        
        # 字数统计
        if successful:
            word_counts = [s.word_count for s in successful if s.word_count > 0]
            avg_words = int(mean(word_counts)) if word_counts else 0
        else:
            avg_words = 0
        
        return {
            "total_samples": len(samples),
            "successful_samples": len(successful),
            "success_rate": round(success_rate, 4),
            "avg_word_count": avg_words,
            "sample_novels": [s.novel_name for s in successful[:10]],
            "platforms": list(set(s.platform for s in samples)),
            "common_golden_fingers": self._most_common(
                [gf for s in successful for gf in s.golden_fingers],
                top_n=5
            ),
            "common_openings": self._most_common(
                [s.opening_type for s in successful if s.opening_type],
                top_n=3
            ),
        }
    
    def _most_common(self, items: List[str], top_n: int = 5) -> List[Dict[str, Any]]:
        """统计最常见的项"""
        counter = Counter(items)
        return [
            {"name": item, "count": count}
            for item, count in counter.most_common(top_n)
        ]


class GoldenFingerConflictDetector:
    """金手指冲突检测器
    
    检测用户输入的金手指是否存在与当前热门金手指的冲突
    """
    
    # 已知的金手指类型
    KNOWN_GOLDEN_FINGERS = {
        "系统": ["签到系统", "神级系统", "强化系统", "抽奖系统", "升级系统", "反派系统"],
        "重生": ["重生回过去", "重生到未来", "重生到异世界"],
        "穿越": ["穿越到古代", "穿越到异世界", "穿越到未来", "魂穿", "身穿"],
        "无敌": ["开局无敌", "隐藏实力", "扮猪吃虎"],
        "签到": ["每日签到", "地点签到", "事件签到"],
        "仓库": ["随身仓库", "空间仓库", "系统仓库"],
        "鉴宝": ["古玩鉴宝", "赌石鉴宝", "异能鉴宝"],
        "神医": ["神医传承", "医仙系统", "异能神医"],
        "兵王": ["特种兵王", "雇佣兵王", "保镖兵王"],
        "神豪": ["神豪系统", "神豪重生", "逆袭神豪"],
    }
    
    def __init__(self, template_repo: DynamicTemplateRepository):
        self.template_repo = template_repo
    
    async def detect_conflicts(
        self,
        user_golden_fingers: List[str],
        platform: Optional[str] = None,
    ) -> Dict[str, Any]:
        """检测金手指冲突
        
        Returns:
            {
                "user_gfs": 用户输入的金手指,
                "current_hot_gfs": 当前热门金手指,
                "conflicts": 冲突的金手指,
                "saturation": 饱和度分析,
                "recommendations": 建议,
            }
        """
        # 获取当前热门金手指模板
        hot_gfs = await self.template_repo.list_by_type(
            TemplateType.GOLDEN_FINGER,
            limit=50,
        )
        
        current_hot = [
            g.pattern.name for g in hot_gfs
            if g.pattern.trend.value in ("rising", "stable")
        ]
        
        # 冲突检测
        conflicts = []
        for user_gf in user_golden_fingers:
            # 检测1：完全重复（用户选了一个已经很饱和的设定）
            if user_gf in current_hot:
                conflicts.append({
                    "type": "saturation",
                    "golden_finger": user_gf,
                    "message": f"金手指「{user_gf}」非常热门，但也意味着竞争激烈",
                    "severity": "info",
                })
            
            # 检测2：已被证伪/退潮
            for g in hot_gfs:
                if g.pattern.name == user_gf and g.pattern.trend.value == "declining":
                    conflicts.append({
                        "type": "declining",
                        "golden_finger": user_gf,
                        "message": f"金手指「{user_gf}」正在退潮（趋势：下降）",
                        "severity": "warning",
                    })
            
            # 检测3：内在矛盾（例如同时"无敌"和"成长"）
            if self._has_internal_conflict(user_gf):
                conflicts.append({
                    "type": "internal_conflict",
                    "golden_finger": user_gf,
                    "message": f"金手指「{user_gf}」存在内在矛盾",
                    "severity": "warning",
                })
        
        # 饱和度分析
        saturation = await self._analyze_saturation(user_golden_fingers, current_hot)
        
        # 生成建议
        recommendations = self._generate_recommendations(
            user_golden_fingers, current_hot, conflicts
        )
        
        return {
            "user_golden_fingers": user_golden_fingers,
            "current_hot_golden_fingers": current_hot[:10],
            "conflicts": conflicts,
            "saturation": saturation,
            "recommendations": recommendations,
        }
    
    def _has_internal_conflict(self, golden_finger: str) -> bool:
        """检测金手指的内在矛盾"""
        # 简化：基于关键词
        gf_lower = golden_finger.lower()
        
        if "无敌" in gf_lower and "成长" in gf_lower:
            return True
        if "最强" in gf_lower and "升级" in gf_lower:
            return True
        if "无敌" in gf_lower and "修炼" in gf_lower:
            return True
        
        return False
    
    async def _analyze_saturation(
        self,
        user_golden_fingers: List[str],
        current_hot: List[str],
    ) -> Dict[str, Any]:
        """分析市场饱和度"""
        if not user_golden_fingers:
            return {"level": "unknown", "score": 0.0}
        
        # 计算用户选择与热门的重叠度
        overlap = sum(1 for gf in user_golden_fingers if gf in current_hot)
        overlap_rate = overlap / len(user_golden_fingers) if user_golden_fingers else 0
        
        if overlap_rate >= 0.7:
            level = "high"
            message = "高度饱和 - 市场上有大量同类作品"
        elif overlap_rate >= 0.4:
            level = "medium"
            message = "中等饱和 - 有一定竞争但仍有空间"
        else:
            level = "low"
            message = "低饱和 - 差异化较强"
        
        return {
            "level": level,
            "score": round(overlap_rate, 2),
            "message": message,
            "overlap_count": overlap,
            "total_count": len(user_golden_fingers),
        }
    
    def _generate_recommendations(
        self,
        user_golden_fingers: List[str],
        current_hot: List[str],
        conflicts: List[Dict],
    ) -> List[Dict[str, str]]:
        """生成金手指建议"""
        recommendations = []
        
        # 基于饱和度建议
        saturation_conflicts = [c for c in conflicts if c["type"] == "saturation"]
        if len(saturation_conflicts) > 1:
            recommendations.append({
                "type": "diversify",
                "message": "考虑加入差异化元素来与热门金手指区分",
                "priority": "high",
            })
        
        # 基于退潮建议
        declining_conflicts = [c for c in conflicts if c["type"] == "declining"]
        if declining_conflicts:
            for c in declining_conflicts:
                recommendations.append({
                    "type": "avoid",
                    "message": f"建议避免使用 {c['golden_finger']}，或加入创新元素",
                    "priority": "high",
                })
        
        # 基于内在矛盾建议
        internal_conflicts = [c for c in conflicts if c["type"] == "internal_conflict"]
        if internal_conflicts:
            for c in internal_conflicts:
                recommendations.append({
                    "type": "reconsider",
                    "message": f"建议重新设计 {c['golden_finger']}，消除矛盾",
                    "priority": "medium",
                })
        
        # 默认建议
        if not recommendations:
            recommendations.append({
                "type": "info",
                "message": "金手指设定合理，无明显冲突",
                "priority": "low",
            })
        
        return recommendations