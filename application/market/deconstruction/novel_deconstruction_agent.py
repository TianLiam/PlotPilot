"""爆款拆书Agent - 使用LLM对单本小说进行深度拆解"""
import json
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

from domain.market.entities.novel_deconstruction import (
    NovelDeconstruction,
    ChapterBeat,
    CharacterModel,
    PlotStructure,
    GoldenFingerAnalysis,
    CoolPointDistribution,
    ConflictDesign,
    BestsellerDNA,
)
from infrastructure.ai.llm_client import LLMClient

logger = logging.getLogger(__name__)


class NovelDeconstructionAgent:
    """爆款拆书Agent"""
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm_client = llm_client or LLMClient()
    
    async def deconstruct(
        self,
        novel_text: str,
        novel_info: Dict[str, Any],
        max_chapters: int = 30,
    ) -> NovelDeconstruction:
        """拆解小说
        
        Args:
            novel_text: 小说文本（合并后的章节）
            novel_info: 小说基本信息
            max_chapters: 最大分析章节数
        
        Returns:
            完整的拆书报告
        """
        deconstruction_id = f"decon-{uuid.uuid4().hex[:12]}"
        
        chapters = self._split_into_chapters(novel_text)
        analyzed_chapters = min(len(chapters), max_chapters)
        
        analysis_text = self._prepare_analysis_text(chapters[:analyzed_chapters])

        from infrastructure.ai.prompt_registry import get_prompt_registry

        registry = get_prompt_registry()
        prompt = registry.render_to_prompt("market-novel-deconstruction", {
            "novel_text": analysis_text,
            "book_title": novel_info.get("book_name") or "",
            "genre": novel_info.get("category") or "通用",
            "chapter_count": analyzed_chapters,
        })

        response = await self.llm_client.generate(
            prompt.user,
            system_prompt=prompt.system,
            require_real_provider=True,
            max_tokens=8000,
            temperature=0.3,
        )
        
        result = self._parse_response(response)
        
        return self._build_deconstruction(
            deconstruction_id=deconstruction_id,
            novel_info=novel_info,
            result=result,
            analyzed_chapters=analyzed_chapters,
            chapters=chapters[:analyzed_chapters],
        )
    
    def _split_into_chapters(self, novel_text: str) -> list:
        """将小说文本分割为章节"""
        import re
        
        patterns = [
            r'## 第[一二三四五六七八九十\d]+章',
            r'第[一二三四五六七八九十\d]+章',
            r'Chapter \d+',
        ]
        
        for pattern in patterns:
            splits = re.split(f'(?={pattern})', novel_text)
            if len(splits) > 2:
                return [s.strip() for s in splits if s.strip()]
        
        chunk_size = 2000
        return [novel_text[i:i+chunk_size] for i in range(0, len(novel_text), chunk_size)]
    
    def _prepare_analysis_text(self, chapters: list) -> str:
        """准备分析文本（限制长度）"""
        max_chars = 15000
        text = "\n\n".join(chapters)
        
        if len(text) > max_chars:
            head = text[:max_chars // 3]
            tail = text[-max_chars // 3:]
            text = f"{head}\n\n...[中间章节省略]...\n\n{tail}"
        
        return text
    
    def _build_prompt(
        self,
        novel_text: str,
        novel_info: Dict[str, Any],
        chapter_count: int,
    ) -> str:
        """构建拆书提示词"""
        return f"""# 小说信息
- 书名：{novel_info.get('book_name', '未知')}
- 作者：{novel_info.get('author', '未知')}
- 分类：{novel_info.get('category', '未知')}
- 分析章节：前{chapter_count}章

# 小说内容
{novel_text}

---

请对以上小说进行深度拆解分析，按系统提示的JSON格式输出完整报告。"""
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """解析LLM响应"""
        try:
            json_match = response
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                json_match = response[start:end].strip()
            elif "```" in response:
                start = response.find("```") + 3
                end = response.find("```", start)
                json_match = response[start:end].strip()
            
            return json.loads(json_match)
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            try:
                last_brace = response.rfind("}")
                if last_brace > 0:
                    fixed = response[:last_brace+1]
                    return json.loads(fixed)
            except:
                pass
            return {}
    
    def _build_deconstruction(
        self,
        deconstruction_id: str,
        novel_info: Dict[str, Any],
        result: Dict[str, Any],
        analyzed_chapters: int,
        chapters: list,
    ) -> NovelDeconstruction:
        """从解析结果构建拆书实体"""
        
        chapter_beats = []
        for cb in result.get("chapter_beats", []):
            chapter_beats.append(ChapterBeat(
                chapter_number=cb.get("chapter_number", 0),
                title=cb.get("title", ""),
                word_count=cb.get("word_count", len(chapters[cb.get("chapter_number", 1)-1]) if cb.get("chapter_number", 1) <= len(chapters) else 0),
                pacing=cb.get("pacing", ""),
                pacing_score=cb.get("pacing_score", 0.0),
                emotion=cb.get("emotion", ""),
                emotion_score=cb.get("emotion_score", 0.0),
                has_cool_point=cb.get("has_cool_point", False),
                cool_point_type=cb.get("cool_point_type", ""),
                cool_point_intensity=cb.get("cool_point_intensity", 0.0),
                has_conflict=cb.get("has_conflict", False),
                conflict_type=cb.get("conflict_type", ""),
                conflict_intensity=cb.get("conflict_intensity", 0.0),
                info_density=cb.get("info_density", ""),
                key_events=cb.get("key_events", []),
                has_hook=cb.get("has_hook", False),
                hook_type=cb.get("hook_type", ""),
            ))
        
        characters = []
        for ch in result.get("characters", []):
            characters.append(CharacterModel(
                name=ch.get("name", ""),
                role=ch.get("role", "supporting"),
                archetype=ch.get("archetype", ""),
                personality_traits=ch.get("personality_traits", []),
                motivation=ch.get("motivation", ""),
                goal=ch.get("goal", ""),
                flaw=ch.get("flaw", ""),
                growth_arc=ch.get("growth_arc", ""),
                relationships=ch.get("relationships", []),
                first_appearance_chapter=ch.get("first_appearance_chapter", 0),
                appearance_frequency=ch.get("appearance_frequency", 0.0),
                key_moments=ch.get("key_moments", []),
            ))
        
        plot_structure = []
        for ps in result.get("plot_structure", []):
            plot_structure.append(PlotStructure(
                act=ps.get("act", ""),
                start_chapter=ps.get("start_chapter", 0),
                end_chapter=ps.get("end_chapter", 0),
                description=ps.get("description", ""),
                key_events=ps.get("key_events", []),
                turning_points=ps.get("turning_points", []),
            ))
        
        golden_fingers = []
        for gf in result.get("golden_fingers", []):
            golden_fingers.append(GoldenFingerAnalysis(
                name=gf.get("name", ""),
                type=gf.get("type", ""),
                awakening_chapter=gf.get("awakening_chapter", 0),
                awakening_scene=gf.get("awakening_scene", ""),
                initial_power=gf.get("initial_power", ""),
                growth_path=gf.get("growth_path", ""),
                limitations=gf.get("limitations", []),
                usage_frequency=gf.get("usage_frequency", ""),
                key_usage_chapters=gf.get("key_usage_chapters", []),
                plot_driver=gf.get("plot_driver", False),
                cool_point_enabler=gf.get("cool_point_enabler", False),
            ))
        
        cool_points = []
        for cp in result.get("cool_points", []):
            cool_points.append(CoolPointDistribution(
                cool_point_type=cp.get("cool_point_type", ""),
                total_count=cp.get("total_count", 0),
                chapters=cp.get("chapters", []),
                avg_intensity=cp.get("avg_intensity", 0.0),
                frequency=cp.get("frequency", ""),
                description=cp.get("description", ""),
            ))
        
        conflicts = []
        for cf in result.get("conflicts", []):
            conflicts.append(ConflictDesign(
                conflict_type=cf.get("conflict_type", ""),
                description=cf.get("description", ""),
                escalation_pattern=cf.get("escalation_pattern", ""),
                resolution_style=cf.get("resolution_style", ""),
                chapters=cf.get("chapters", []),
                intensity_curve=cf.get("intensity_curve", []),
            ))
        
        dna_data = result.get("dna", {})
        dna = BestsellerDNA(
            dna_id=f"dna-{uuid.uuid4().hex[:12]}",
            novel_id=novel_info.get("book_id", ""),
            novel_name=novel_info.get("book_name", ""),
            core_selling_point=dna_data.get("core_selling_point", ""),
            target_audience=dna_data.get("target_audience", ""),
            emotional_resonance=dna_data.get("emotional_resonance", ""),
            opening_template=dna_data.get("opening_template", ""),
            pacing_formula=dna_data.get("pacing_formula", ""),
            cool_point_formula=dna_data.get("cool_point_formula", ""),
            conflict_formula=dna_data.get("conflict_formula", ""),
            character_formula=dna_data.get("character_formula", ""),
            applicable_genres=dna_data.get("applicable_genres", []),
            difficulty_level=dna_data.get("difficulty_level", ""),
            replication_score=dna_data.get("replication_score", 0.0),
            extracted_from_chapters=analyzed_chapters,
            confidence=0.8,
        ) if dna_data else None
        
        total_word_count = sum(len(c) for c in chapters)
        
        return NovelDeconstruction(
            deconstruction_id=deconstruction_id,
            novel_id=novel_info.get("book_id", ""),
            novel_name=novel_info.get("book_name", ""),
            author=novel_info.get("author", ""),
            platform=novel_info.get("platform", ""),
            category=novel_info.get("category", ""),
            analyzed_chapters=analyzed_chapters,
            total_word_count=total_word_count,
            chapter_beats=chapter_beats,
            characters=characters,
            plot_structure=plot_structure,
            golden_fingers=golden_fingers,
            cool_points=cool_points,
            conflicts=conflicts,
            dna=dna,
            ai_summary=result.get("ai_summary", ""),
            ai_strengths=result.get("ai_strengths", ""),
            ai_weaknesses=result.get("ai_weaknesses", ""),
            ai_replicable_elements=result.get("ai_replicable_elements", ""),
        )
