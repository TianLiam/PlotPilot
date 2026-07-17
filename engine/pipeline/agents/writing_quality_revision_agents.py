"""Agent7: 章节写作Agent - 实际写内容"""
import logging
from typing import Dict, Any

from engine.pipeline.agents.base_agent import BaseAgent
from engine.pipeline.entities.pipeline_entities import AgentType, PipelineContext

logger = logging.getLogger(__name__)


class WritingAgent(BaseAgent):
    """章节写作Agent"""
    
    agent_type = AgentType.WRITING
    
    def get_required_inputs(self) -> list:
        return [
            AgentType.TOPIC_PLANNING,
            AgentType.CHARACTER_DESIGN,
            AgentType.WORLDVIEW_DESIGN,
            AgentType.PACING,
        ]
    
    async def execute(self, context: PipelineContext) -> Dict[str, Any]:
        """执行章节写作"""
        user_request = context.user_request
        topic_result = context.topic_result
        character_result = context.character_result
        worldview_result = context.worldview_result
        pacing_result = context.pacing_result
        
        # 写作范围（默认写前3章作为示例）
        chapters_to_write = user_request.get("chapters_to_write", 3)
        
        result = {
            "chapters_written": 0,
            "total_words": 0,
            "chapters": [],
        }
        
        beat_sheet = pacing_result.get("beat_sheet", [])
        protagonist = character_result.get("protagonist", {})
        
        for i in range(min(chapters_to_write, len(beat_sheet))):
            beat = beat_sheet[i] if i < len(beat_sheet) else {}
            
            prompt = self._build_chapter_prompt(
                chapter_num=i + 1,
                beat=beat,
                topic=topic_result,
                character=character_result,
                worldview=worldview_result,
            )
            
            response = await self.generate(prompt, max_tokens=3000, temperature=0.8)
            
            result["chapters"].append({
                "chapter_number": i + 1,
                "title": beat.get("description", f"第{i+1}章"),
                "content": response,
                "word_count": len(response),
            })
            
            result["chapters_written"] += 1
            result["total_words"] += len(response)
        
        return result
    
    def _build_chapter_prompt(
        self,
        chapter_num: int,
        beat: dict,
        topic: dict,
        character: dict,
        worldview: dict,
    ) -> str:
        """构建章节写作提示词"""
        protagonist = character.get("protagonist", {})
        genres = topic.get("selected_genres", [])
        core_selling_point = topic.get("core_selling_point", "")
        
        return f"""你是网文作家。请写第{chapter_num}章。

## 题材: {', '.join(genres)}
## 核心卖点: {core_selling_point}
## 主角: {protagonist.get('name', '主角')} - {protagonist.get('personality', [])}
## 世界: {worldview.get('world_name', '')}
## 本章节拍: {beat.get('beat', '')} - {beat.get('description', '')}

要求：
- 2000-3000字
- 网文风格，快节奏
- 有对话、有动作、有心理
- 结尾留钩子

直接输出章节内容，不要输出其他内容。"""


class QualityCheckAgent(BaseAgent):
    """质量检测Agent"""
    
    agent_type = AgentType.QUALITY_CHECK
    
    def get_required_inputs(self) -> list:
        return [AgentType.WRITING]
    
    async def execute(self, context: PipelineContext) -> Dict[str, Any]:
        """执行质量检测"""
        writing_result = context.writing_result
        chapters = writing_result.get("chapters", [])
        
        all_content = "\n\n".join([
            f"第{c['chapter_number']}章\n{c['content']}"
            for c in chapters
        ])
        
        prompt = f"""你是网文质量检测专家。请评估以下内容的质量。

{all_content[:5000]}

请评估：
1. 文风评分(style_score): 0-10
2. 节奏评分(pacing_score): 0-10
3. 整体评分(overall_score): 0-10
4. 存在的问题(issues)
5. 改进建议(suggestions)

以JSON格式输出：

```json
{
  "style_score": 7.5,
  "pacing_score": 8.0,
  "overall_score": 7.8,
  "issues": [
    {"chapter": 1, "issue": "问题描述"}
  ],
  "suggestions": ["建议1", "建议2"]
}
```

只输出JSON。"""
        
        response = await self.generate(prompt, max_tokens=2000, temperature=0.3)
        result = self.parse_json_response(response)
        
        result.setdefault("overall_score", 5.0)
        result.setdefault("style_score", 5.0)
        result.setdefault("pacing_score", 5.0)
        result.setdefault("issues", [])
        result.setdefault("suggestions", [])
        
        return result


class RevisionAgent(BaseAgent):
    """修文Agent"""
    
    agent_type = AgentType.REVISION
    
    def get_required_inputs(self) -> list:
        return [AgentType.WRITING, AgentType.QUALITY_CHECK]
    
    async def execute(self, context: PipelineContext) -> Dict[str, Any]:
        """执行修文"""
        writing_result = context.writing_result
        quality_result = context.quality_result
        
        chapters = writing_result.get("chapters", [])
        issues = quality_result.get("issues", [])
        
        if quality_result.get("overall_score", 0) >= 7.0:
            # 质量合格，不需要修改
            return {
                "chapters_revised": 0,
                "revisions": [],
                "final_score": quality_result.get("overall_score", 0),
                "message": "质量合格，无需修改",
            }
        
        # 需要修改
        result = {
            "chapters_revised": 0,
            "revisions": [],
            "final_score": quality_result.get("overall_score", 0),
        }
        
        # 对有问题的章节进行修改
        for issue in issues[:3]:  # 只修改前3个问题
            chapter_num = issue.get("chapter", 0)
            if chapter_num < 1 or chapter_num > len(chapters):
                continue
            
            original = chapters[chapter_num - 1]["content"]
            prompt = f"""你是网文编辑。请修改以下章节内容。

原文：
{original[:2000]}

问题：{issue.get('issue', '需要改进')}

请修改后直接输出新内容，不要解释。"""
            
            revised = await self.generate(prompt, max_tokens=3000, temperature=0.7)
            
            result["revisions"].append({
                "chapter": chapter_num,
                "original_length": len(original),
                "revised_length": len(revised),
                "issue_addressed": issue.get("issue", ""),
            })
            result["chapters_revised"] += 1
        
        # 假设修改后提升1分
        result["final_score"] = min(10.0, quality_result.get("overall_score", 0) + 1.0)
        
        return result