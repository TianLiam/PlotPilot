"""创作前研究 - 领域实体"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum


class ResearchStatus(str, Enum):
    """研究状态"""
    PENDING = "pending"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    FAILED = "failed"


class GenreElement(str, Enum):
    """题材元素"""
    URBAN = "urban"                  # 都市
    XIANXIA = "xianxia"              # 仙侠
    FANTASY = "fantasy"              # 玄幻
    ROMANCE = "romance"              # 言情
    SCIFI = "scifi"                  # 科幻
    APOCALYPSE = "apocalypse"        # 末日
    SYSTEM = "system"                # 系统流
    FARMING = "farming"              # 种田
    REBORN = "reborn"                # 重生
    DUNGEON = "dungeon"              # 副本
    SIGN_IN = "sign_in"              # 签到流
    REGRESSION = "regression"        # 回归流
    INVINCIBLE = "invincible"        # 无敌流
    FACE_SLAP = "face_slap"          # 打脸流
    STOREROOM = "storeroom"          # 仓库流
    TIME_TRAVEL = "time_travel"      # 穿越


@dataclass
class GenreRequest:
    """用户输入的题材请求"""
    genres: List[str] = field(default_factory=list)        # 题材列表
    golden_fingers: List[str] = field(default_factory=list)  # 金手指列表
    keywords: List[str] = field(default_factory=list)     # 关键词
    target_word_count: int = 0                            # 目标字数
    target_chapter_count: int = 0                         # 目标章节数
    additional_notes: str = ""                            # 额外说明
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "genres": self.genres,
            "golden_fingers": self.golden_fingers,
            "keywords": self.keywords,
            "target_word_count": self.target_word_count,
            "target_chapter_count": self.target_chapter_count,
            "additional_notes": self.additional_notes,
        }


@dataclass
class HistoricalSample:
    """历史样本小说"""
    novel_id: str
    novel_name: str
    author: str
    platform: str
    category: str
    
    # 基本统计
    word_count: int = 0
    chapter_count: int = 0
    popularity: int = 0
    avg_chapter_words: int = 0
    
    # 元素标记
    golden_fingers: List[str] = field(default_factory=list)  # 金手指标签
    genre_tags: List[str] = field(default_factory=list)     # 题材标签
    opening_type: str = ""                                  # 开局类型
    is_successful: bool = False                             # 是否成功（高排名）
    peak_rank: int = 999                                    # 最高排名
    days_on_chart: int = 0                                  # 在榜天数
    trend_direction: str = "stable"                         # 趋势方向


@dataclass
class GenreStats:
    """题材统计数据"""
    genre: str
    
    # 基础数据
    total_novels: int = 0                  # 总小说数
    successful_novels: int = 0              # 成功小说数
    success_rate: float = 0.0               # 成功率
    
    # 字数分布
    avg_word_count: int = 0                 # 平均字数
    median_word_count: int = 0              # 中位数
    word_count_std: float = 0.0             # 字数标准差
    
    # 章节分布
    avg_chapter_count: int = 0              # 平均章节数
    avg_chapter_words: int = 0              # 平均章节字数
    optimal_chapter_words: int = 2000       # 推荐章节字数
    
    # 表现
    avg_peak_rank: float = 0.0              # 平均最高排名
    avg_popularity: float = 0.0             # 平均热度
    avg_days_on_chart: float = 0.0          # 平均在榜天数
    
    # 趋势
    trend: str = "stable"                   # 当前趋势
    trend_change: float = 0.0               # 趋势变化
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "genre": self.genre,
            "total_novels": self.total_novels,
            "successful_novels": self.successful_novels,
            "success_rate": round(self.success_rate, 4),
            "avg_word_count": self.avg_word_count,
            "median_word_count": self.median_word_count,
            "word_count_std": round(self.word_count_std, 2),
            "avg_chapter_count": self.avg_chapter_count,
            "avg_chapter_words": self.avg_chapter_words,
            "optimal_chapter_words": self.optimal_chapter_words,
            "avg_peak_rank": round(self.avg_peak_rank, 2),
            "avg_popularity": round(self.avg_popularity, 2),
            "avg_days_on_chart": round(self.avg_days_on_chart, 2),
            "trend": self.trend,
            "trend_change": round(self.trend_change, 2),
        }


@dataclass
class OpeningPattern:
    """开局模式"""
    name: str                               # 模式名称
    description: str                        # 描述
    success_count: int = 0                  # 成功使用次数
    total_count: int = 0                    # 总使用次数
    success_rate: float = 0.0               # 成功率
    avg_popularity: float = 0.0             # 平均热度
    sample_novels: List[str] = field(default_factory=list)  # 样例小说
    chapter_range: str = ""                 # 章节范围
    key_points: List[str] = field(default_factory=list)  # 关键点


@dataclass
class RecommendationItem:
    """建议项"""
    type: str                                # recommend / avoid / caution
    title: str
    description: str
    confidence: float = 0.0                  # 置信度 0-1
    reason: str = ""                         # 推荐/避免原因
    references: List[str] = field(default_factory=list)  # 参考样例


@dataclass
class NovelResearch:
    """完整的小说创作前研究报告"""
    research_id: str
    user_request: GenreRequest
    status: ResearchStatus = ResearchStatus.PENDING
    
    # 分析结果
    sample_count: int = 0                     # 样本数量
    genre_stats: List[GenreStats] = field(default_factory=list)
    opening_patterns: List[OpeningPattern] = field(default_factory=list)
    recommendations: List[RecommendationItem] = field(default_factory=list)
    
    # AI生成内容
    ai_summary: str = ""                      # AI总结
    ai_suggestions: str = ""                  # AI建议
    ai_warnings: str = ""                     # AI警告
    
    # 风险评估
    overall_score: float = 0.0                # 总体评分 0-100
    risk_level: str = "low"                   # low / medium / high
    risk_factors: List[str] = field(default_factory=list)
    
    # 时机分析
    timing_score: float = 0.0                 # 时机评分
    timing_advice: str = ""                   # 时机建议
    
    # 元信息
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "research_id": self.research_id,
            "user_request": self.user_request.to_dict(),
            "status": self.status.value,
            "sample_count": self.sample_count,
            "genre_stats": [g.to_dict() for g in self.genre_stats],
            "opening_patterns": [
                {
                    "name": p.name,
                    "description": p.description,
                    "success_count": p.success_count,
                    "total_count": p.total_count,
                    "success_rate": round(p.success_rate, 4),
                    "avg_popularity": round(p.avg_popularity, 2),
                    "sample_novels": p.sample_novels,
                    "chapter_range": p.chapter_range,
                    "key_points": p.key_points,
                } for p in self.opening_patterns
            ],
            "recommendations": [
                {
                    "type": r.type,
                    "title": r.title,
                    "description": r.description,
                    "confidence": round(r.confidence, 2),
                    "reason": r.reason,
                    "references": r.references,
                } for r in self.recommendations
            ],
            "ai_summary": self.ai_summary,
            "ai_suggestions": self.ai_suggestions,
            "ai_warnings": self.ai_warnings,
            "overall_score": round(self.overall_score, 2),
            "risk_level": self.risk_level,
            "risk_factors": self.risk_factors,
            "timing_score": round(self.timing_score, 2),
            "timing_advice": self.timing_advice,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }