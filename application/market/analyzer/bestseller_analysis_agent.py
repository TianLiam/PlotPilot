"""爆款分析Agent - 使用LLM分析热门小说并提取模板"""
import logging
import json
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime

from domain.market.entities.dynamic_template import (
    TemplatePattern,
    TemplateType,
    TrendDirection,
    SourceNovel,
    DiscoveredTemplate,
)
from domain.market.repositories.dynamic_template_repository import DynamicTemplateRepository
from infrastructure.ai.llm_client import LLMClient

logger = logging.getLogger(__name__)


class BestsellerAnalysisAgent:
    """爆款分析Agent"""
    
    def __init__(
        self,
        template_repo: DynamicTemplateRepository,
        llm_client: Optional[LLMClient] = None,
    ):
        self.template_repo = template_repo
        self.llm_client = llm_client or LLMClient()
    
    async def analyze_novel(
        self,
        novel_text: str,
        novel_info: Dict[str, Any],
    ) -> Dict[str, Any]:
        """分析小说并提取模板
        
        Args:
            novel_text: 小说文本
            novel_info: 小说基本信息
        
        Returns:
            分析结果
        """
        try:
            # 调用LLM
            from infrastructure.ai.prompt_registry import get_prompt_registry

            registry = get_prompt_registry()
            prompt = registry.render_to_prompt("market-bestseller-analysis", {
                "novel_text": novel_text[:30000],
                "genre": novel_info.get("category") or "通用",
                "book_title": novel_info.get("book_name") or "",
            })
            response = await self.llm_client.generate(
                prompt.user,
                system_prompt=prompt.system,
                require_real_provider=True,
                max_tokens=8000,
                temperature=0.3,
            )
            
            # 解析结果
            analysis_result = self._parse_analysis_response(response)
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Failed to analyze novel: {e}")
            return {"error": str(e)}
    
    def _parse_analysis_response(self, response: str) -> Dict[str, Any]:
        """解析LLM响应"""
        try:
            # 尝试提取JSON
            json_match = response
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                json_match = response[start:end].strip()
            elif "```" in response:
                start = response.find("```") + 3
                end = response.find("```", start)
                json_match = response[start:end].strip()
            
            result = json.loads(json_match)
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.debug(f"Response was: {response[:500]}")
            return {"error": "Failed to parse analysis result", "raw_response": response}
    
    async def extract_templates_from_analysis(
        self,
        analysis_result: Dict[str, Any],
        novel_info: Dict[str, Any],
    ) -> List[DiscoveredTemplate]:
        """从分析结果中提取模板
        
        Args:
            analysis_result: 分析结果
            novel_info: 小说信息
        
        Returns:
            发现的模板列表
        """
        templates = []
        
        # 创建来源小说信息
        source_novel = SourceNovel(
            platform=novel_info.get("platform", "unknown"),
            novel_id=novel_info.get("book_id", ""),
            novel_name=novel_info.get("book_name", ""),
            author=novel_info.get("author", ""),
            rank=novel_info.get("rank", 0),
            category=novel_info.get("category", ""),
            word_count=novel_info.get("total_chapters", 0),
            popularity=novel_info.get("popularity", 0),
            score=novel_info.get("score", 0.0),
        )
        
        # 提取金手指模板
        golden_fingers = analysis_result.get("golden_fingers", [])
        for gf in golden_fingers:
            template = self._create_template(
                pattern_type=TemplateType.GOLDEN_FINGER,
                pattern_data=gf,
                source_novel=source_novel,
                novel_info=novel_info,
            )
            templates.append(template)
        
        # 提取开局模式
        openings = analysis_result.get("opening_patterns", [])
        for op in openings:
            template = self._create_template(
                pattern_type=TemplateType.OPENING,
                pattern_data=op,
                source_novel=source_novel,
                novel_info=novel_info,
            )
            templates.append(template)
        
        # 提取人物原型
        characters = analysis_result.get("character_archetypes", [])
        for ch in characters:
            template = self._create_template(
                pattern_type=TemplateType.CHARACTER,
                pattern_data=ch,
                source_novel=source_novel,
                novel_info=novel_info,
            )
            templates.append(template)
        
        # 提取世界观元素
        worldviews = analysis_result.get("worldview_elements", [])
        for wv in worldviews:
            template = self._create_template(
                pattern_type=TemplateType.WORLDVIEW,
                pattern_data=wv,
                source_novel=source_novel,
                novel_info=novel_info,
            )
            templates.append(template)
        
        # 提取爽点设计
        cool_points = analysis_result.get("cool_point_designs", [])
        for cp in cool_points:
            template = self._create_template(
                pattern_type=TemplateType.COOL_POINT,
                pattern_data=cp,
                source_novel=source_novel,
                novel_info=novel_info,
            )
            templates.append(template)
        
        # 提取剧情结构
        pacing = analysis_result.get("pacing_analysis", {})
        if pacing:
            template = self._create_template(
                pattern_type=TemplateType.PACING,
                pattern_data={
                    "name": f"{novel_info.get('book_name', '')}节奏模式",
                    "description": pacing.get("overall", ""),
                    "genre": novel_info.get("category", ""),
                    "content": json.dumps(pacing, ensure_ascii=False),
                },
                source_novel=source_novel,
                novel_info=novel_info,
            )
            templates.append(template)
        
        return templates
    
    def _create_template(
        self,
        pattern_type: TemplateType,
        pattern_data: Dict[str, Any],
        source_novel: SourceNovel,
        novel_info: Dict[str, Any],
    ) -> DiscoveredTemplate:
        """创建模板实体"""
        name = pattern_data.get("name", "未命名模板")
        
        pattern = TemplatePattern(
            name=name,
            description=pattern_data.get("description", ""),
            pattern_type=pattern_type,
            genre=pattern_data.get("genre", novel_info.get("category", "")),
            content=pattern_data.get("content", json.dumps(pattern_data, ensure_ascii=False)),
            source_novels=[source_novel],
            occurrence_count=1,
            avg_rank=float(novel_info.get("rank", 0)),
            trend=TrendDirection.STABLE,
            confidence_score=0.5,  # 初始置信度
            tags=pattern_data.get("tags", []),
            metadata={
                "frequency": pattern_data.get("frequency"),
                "key_points": pattern_data.get("key_points", []),
                "traits": pattern_data.get("traits", []),
            },
        )
        
        template_id = f"template-{uuid.uuid4().hex[:12]}"
        
        return DiscoveredTemplate(
            id=template_id,
            pattern=pattern,
            status="active",
        )
    
    async def save_templates(
        self,
        templates: List[DiscoveredTemplate]
    ) -> int:
        """保存模板到数据库
        
        Returns:
            保存的模板数量
        """
        saved_count = 0
        
        for template in templates:
            try:
                # 检查是否已存在相同名称和类型的模板
                existing = await self.template_repo.get_by_name_and_type(
                    template.pattern.name,
                    template.pattern.pattern_type
                )
                
                if existing:
                    # 合并来源小说，增加出现次数
                    existing.pattern.occurrence_count += 1
                    existing.pattern.source_novels.extend(template.pattern.source_novels)
                    existing.pattern.avg_rank = (
                        existing.pattern.avg_rank * (existing.pattern.occurrence_count - 1) +
                        template.pattern.avg_rank
                    ) / existing.pattern.occurrence_count
                    existing.pattern.confidence_score = min(1.0, existing.pattern.occurrence_count * 0.15)
                    existing.pattern.updated_at = datetime.utcnow()
                    await self.template_repo.save(existing)
                    logger.debug(f"Updated existing template: {template.pattern.name}")
                else:
                    # 保存新模板
                    await self.template_repo.save(template)
                    logger.debug(f"Saved new template: {template.pattern.name}")
                
                saved_count += 1
                
            except Exception as e:
                logger.error(f"Failed to save template {template.pattern.name}: {e}")
        
        return saved_count
