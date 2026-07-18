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


# 分析提示词模板
ANALYSIS_SYSTEM_PROMPT = """你是一个专业的网文分析师，擅长从热门小说中提取爆款元素和创作规律。

你的任务是从给定的小说文本中分析并提取以下内容：

1. **金手指设定**：主角的特殊能力、系统、神器等设定
2. **开局节奏**：前几章的节奏安排、爽点分布
3. **人物设定**：主要人物的性格、特点、关系
4. **世界观设定**：故事背景、力量体系、社会结构
5. **爽点设计**：让读者感到爽快的设计模式
6. **冲突设计**：矛盾冲突的设计方式
7. **剧情结构**：主线推进方式、支线安排

请以JSON格式输出分析结果，格式如下：

```json
{
  "golden_fingers": [
    {
      "name": "金手指名称",
      "description": "详细描述",
      "genre": "适用题材",
      "content": "具体设定内容",
      "tags": ["标签1", "标签2"]
    }
  ],
  "opening_patterns": [
    {
      "name": "开局模式名称",
      "description": "描述",
      "genre": "适用题材",
      "content": "具体内容",
      "key_points": ["关键点1", "关键点2"],
      "chapter_range": "1-3章"
    }
  ],
  "character_archetypes": [
    {
      "name": "人物原型名称",
      "description": "描述",
      "genre": "适用题材",
      "content": "人物设定模板",
      "traits": ["特点1", "特点2"]
    }
  ],
  "worldview_elements": [
    {
      "name": "世界观元素名称",
      "description": "描述",
      "genre": "适用题材",
      "content": "具体设定",
      "power_system": "力量体系描述"
    }
  ],
  "cool_point_designs": [
    {
      "name": "爽点设计名称",
      "description": "描述",
      "genre": "适用题材",
      "content": "具体设计",
      "frequency": "出现频率"
    }
  ],
  "conflict_patterns": [
    {
      "name": "冲突模式名称",
      "description": "描述",
      "content": "具体设计"
    }
  ],
  "pacing_analysis": {
    "opening": "开局节奏分析",
    "development": "发展节奏分析",
    "climax": "高潮节奏分析",
    "overall": "整体节奏评价"
  },
  "summary": "整体分析总结"
}
```

注意：
1. 只输出JSON，不要输出其他内容
2. 每个元素都要有实际内容，不要空洞的描述
3. 提取的内容要具体、可复用
4. 标注适用的题材类型"""


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
            # 构建提示词
            prompt = f"""请分析以下小说内容，提取爆款元素：

## 小说信息
- 书名：{novel_info.get('book_name', '未知')}
- 作者：{novel_info.get('author', '未知')}
- 分类：{novel_info.get('category', '未知')}
- 章节数：{novel_info.get('crawled_chapters', 0)}

## 小说内容
{novel_text}

---

请按照系统提示的JSON格式输出分析结果。"""

            # 调用LLM
            response = await self.llm_client.generate(
                prompt,
                system_prompt=ANALYSIS_SYSTEM_PROMPT,
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
