"""爆款拆书实体 - 单本小说的深度拆解"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any


@dataclass
class ChapterBeat:
    """单章节拍分析"""
    chapter_number: int
    title: str
    word_count: int = 0
    
    # 节奏分析
    pacing: str = ""              # fast / medium / slow / cliffhanger
    pacing_score: float = 0.0     # 0-10
    
    # 情绪曲线
    emotion: str = ""             # 紧张/兴奋/压抑/爽/感动/平静
    emotion_score: float = 0.0    # 0-10
    
    # 爽点
    has_cool_point: bool = False
    cool_point_type: str = ""     # 升级/打脸/收获/揭秘/重逢/反转
    cool_point_intensity: float = 0.0  # 0-10
    
    # 冲突
    has_conflict: bool = False
    conflict_type: str = ""       # 人际/生存/权力/情感/命运
    conflict_intensity: float = 0.0
    
    # 信息密度
    info_density: str = ""        # high / medium / low
    key_events: List[str] = field(default_factory=list)
    
    # 钩子
    has_hook: bool = False
    hook_type: str = ""           # 悬念/伏笔/危机/期待
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "chapter_number": self.chapter_number,
            "title": self.title,
            "word_count": self.word_count,
            "pacing": self.pacing,
            "pacing_score": self.pacing_score,
            "emotion": self.emotion,
            "emotion_score": self.emotion_score,
            "has_cool_point": self.has_cool_point,
            "cool_point_type": self.cool_point_type,
            "cool_point_intensity": self.cool_point_intensity,
            "has_conflict": self.has_conflict,
            "conflict_type": self.conflict_type,
            "conflict_intensity": self.conflict_intensity,
            "info_density": self.info_density,
            "key_events": self.key_events,
            "has_hook": self.has_hook,
            "hook_type": self.hook_type,
        }


@dataclass
class CharacterModel:
    """人物模型"""
    name: str
    role: str                        # protagonist / antagonist / supporting / love_interest
    archetype: str = ""              # 人物原型
    
    # 性格维度
    personality_traits: List[str] = field(default_factory=list)
    motivation: str = ""             # 核心动机
    goal: str = ""                   # 目标
    flaw: str = ""                   # 缺陷
    growth_arc: str = ""             # 成长弧线
    
    # 关系
    relationships: List[Dict[str, str]] = field(default_factory=list)
    
    # 出场分析
    first_appearance_chapter: int = 0
    appearance_frequency: float = 0.0  # 出场频率 0-1
    key_moments: List[int] = field(default_factory=list)  # 关键章节
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "role": self.role,
            "archetype": self.archetype,
            "personality_traits": self.personality_traits,
            "motivation": self.motivation,
            "goal": self.goal,
            "flaw": self.flaw,
            "growth_arc": self.growth_arc,
            "relationships": self.relationships,
            "first_appearance_chapter": self.first_appearance_chapter,
            "appearance_frequency": self.appearance_frequency,
            "key_moments": self.key_moments,
        }


@dataclass
class PlotStructure:
    """剧情结构分析"""
    act: str                         # Act1 / Act2a / Act2b / Act3
    start_chapter: int = 0
    end_chapter: int = 0
    description: str = ""
    key_events: List[str] = field(default_factory=list)
    turning_points: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "act": self.act,
            "start_chapter": self.start_chapter,
            "end_chapter": self.end_chapter,
            "description": self.description,
            "key_events": self.key_events,
            "turning_points": self.turning_points,
        }


@dataclass
class GoldenFingerAnalysis:
    """金手指分析"""
    name: str
    type: str                        # 系统 / 天赋 / 道具 / 传承 / 重生记忆
    awakening_chapter: int = 0       # 觉醒章节
    awakening_scene: str = ""        # 觉醒场景描述
    
    # 能力设计
    initial_power: str = ""          # 初始能力
    growth_path: str = ""            # 成长路径
    limitations: List[str] = field(default_factory=list)  # 限制/代价
    
    # 使用频率
    usage_frequency: str = ""        # 高频 / 中频 / 低频
    key_usage_chapters: List[int] = field(default_factory=list)
    
    # 与剧情的关系
    plot_driver: bool = False        # 是否是剧情核心驱动力
    cool_point_enabler: bool = False  # 是否主要用于制造爽点
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": self.type,
            "awakening_chapter": self.awakening_chapter,
            "awakening_scene": self.awakening_scene,
            "initial_power": self.initial_power,
            "growth_path": self.growth_path,
            "limitations": self.limitations,
            "usage_frequency": self.usage_frequency,
            "key_usage_chapters": self.key_usage_chapters,
            "plot_driver": self.plot_driver,
            "cool_point_enabler": self.cool_point_enabler,
        }


@dataclass
class CoolPointDistribution:
    """爽点分布"""
    cool_point_type: str
    total_count: int = 0
    chapters: List[int] = field(default_factory=list)
    avg_intensity: float = 0.0
    frequency: str = ""              # 每N章一次
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "cool_point_type": self.cool_point_type,
            "total_count": self.total_count,
            "chapters": self.chapters,
            "avg_intensity": self.avg_intensity,
            "frequency": self.frequency,
            "description": self.description,
        }


@dataclass
class ConflictDesign:
    """冲突设计"""
    conflict_type: str
    description: str = ""
    escalation_pattern: str = ""     # 升级模式
    resolution_style: str = ""       # 解决方式
    chapters: List[int] = field(default_factory=list)
    intensity_curve: List[float] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "conflict_type": self.conflict_type,
            "description": self.description,
            "escalation_pattern": self.escalation_pattern,
            "resolution_style": self.resolution_style,
            "chapters": self.chapters,
            "intensity_curve": self.intensity_curve,
        }


@dataclass
class BestsellerDNA:
    """爆款 DNA - 可复用的创作模板"""
    dna_id: str
    novel_id: str
    novel_name: str
    
    # 核心要素
    core_selling_point: str = ""     # 核心卖点
    target_audience: str = ""        # 目标读者
    emotional_resonance: str = ""    # 情感共鸣点
    
    # 可复用模式
    opening_template: str = ""       # 开局模板
    pacing_formula: str = ""         # 节奏公式
    cool_point_formula: str = ""     # 爽点公式
    conflict_formula: str = ""       # 冲突公式
    character_formula: str = ""      # 人物公式
    
    # 标签
    applicable_genres: List[str] = field(default_factory=list)
    difficulty_level: str = ""       # 简单 / 中等 / 困难
    replication_score: float = 0.0   # 可复制性 0-100
    
    # 来源
    extracted_from_chapters: int = 0
    confidence: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "dna_id": self.dna_id,
            "novel_id": self.novel_id,
            "novel_name": self.novel_name,
            "core_selling_point": self.core_selling_point,
            "target_audience": self.target_audience,
            "emotional_resonance": self.emotional_resonance,
            "opening_template": self.opening_template,
            "pacing_formula": self.pacing_formula,
            "cool_point_formula": self.cool_point_formula,
            "conflict_formula": self.conflict_formula,
            "character_formula": self.character_formula,
            "applicable_genres": self.applicable_genres,
            "difficulty_level": self.difficulty_level,
            "replication_score": self.replication_score,
            "extracted_from_chapters": self.extracted_from_chapters,
            "confidence": self.confidence,
        }


@dataclass
class NovelDeconstruction:
    """完整的小说拆解报告"""
    deconstruction_id: str
    novel_id: str
    novel_name: str
    author: str
    platform: str
    category: str
    
    # 分析范围
    analyzed_chapters: int = 0
    total_word_count: int = 0
    
    # 核心分析
    chapter_beats: List[ChapterBeat] = field(default_factory=list)
    characters: List[CharacterModel] = field(default_factory=list)
    plot_structure: List[PlotStructure] = field(default_factory=list)
    golden_fingers: List[GoldenFingerAnalysis] = field(default_factory=list)
    cool_points: List[CoolPointDistribution] = field(default_factory=list)
    conflicts: List[ConflictDesign] = field(default_factory=list)
    
    # 爆款DNA
    dna: Optional[BestsellerDNA] = None
    
    # AI总结
    ai_summary: str = ""
    ai_strengths: str = ""           # 这本书为什么火
    ai_weaknesses: str = ""          # 不足之处
    ai_replicable_elements: str = ""  # 哪些元素可以复制
    
    # 元信息
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "deconstruction_id": self.deconstruction_id,
            "novel_id": self.novel_id,
            "novel_name": self.novel_name,
            "author": self.author,
            "platform": self.platform,
            "category": self.category,
            "analyzed_chapters": self.analyzed_chapters,
            "total_word_count": self.total_word_count,
            "chapter_beats": [c.to_dict() for c in self.chapter_beats],
            "characters": [c.to_dict() for c in self.characters],
            "plot_structure": [p.to_dict() for p in self.plot_structure],
            "golden_fingers": [g.to_dict() for g in self.golden_fingers],
            "cool_points": [c.to_dict() for c in self.cool_points],
            "conflicts": [c.to_dict() for c in self.conflicts],
            "dna": self.dna.to_dict() if self.dna else None,
            "ai_summary": self.ai_summary,
            "ai_strengths": self.ai_strengths,
            "ai_weaknesses": self.ai_weaknesses,
            "ai_replicable_elements": self.ai_replicable_elements,
            "created_at": self.created_at.isoformat(),
        }