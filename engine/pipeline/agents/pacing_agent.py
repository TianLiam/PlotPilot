"""Agent6: 节奏安排Agent - 规划故事节奏"""
import logging
from typing import Dict, Any

from engine.pipeline.agents.base_agent import BaseAgent
from engine.pipeline.entities.pipeline_entities import AgentType

logger = logging.getLogger(__name__)


class PacingAgent(BaseAgent):
    """节奏安排Agent"""
    
    agent_type = AgentType.PACING
    
    def get_required_inputs(self) -> list:
        return [AgentType.TOPIC_PLANNING, AgentType.CHARACTER_DESIGN, AgentType.WORLDVIEW_DESIGN]
    
    async def execute(self, context: PipelineContext) -> Dict[str, Any]:
        """执行节奏规划"""
        user_request = context.user_request
        topic_result = context.topic_result
        character_result = context.character_result
        
        target_words = user_request.get("target_words", 500000)
        genres = topic_result.get("selected_genres", [])
        protagonist = character_result.get("protagonist", {}).get("name", "")
        
        prompt = self._build_prompt(target_words, genres, protagonist)
        
        response = await self.generate(prompt, max_tokens=4000, temperature=0.6)
        result = self.parse_json_response(response)
        
        result.setdefault("total_chapters", 0)
        result.setdefault("act_structure", [])
        result.setdefault("beat_sheet", [])
        result.setdefault("cool_point_schedule", [])
        result.setdefault("conflict_schedule", [])
        
        return result
    
    def _build_prompt(self, target_words: int, genres: list, protagonist: str) -> str:
        chapter_count = target_words // 2000  # 假设每章2000字
        
        return f"""你是网文节奏专家。请为一部{target_words}字的小说规划节奏。

## 目标字数: {target_words}
## 预计章节: {chapter_count}
## 题材: {', '.join(genres)}
## 主角: {protagonist}

请规划：
1. 幕结构（act_structure）：Act1/Act2a/Act2b/Act3
2. 节拍表（beat_sheet）：关键事件时间线
3. 爽点分布（cool_point_schedule）：爽点类型和章节
4. 冲突升级（conflict_schedule）：冲突设计

以JSON格式输出：

```json
{
  "total_chapters": {chapter_count},
  "act_structure": [
    {"act": "Act1", "chapters": "1-20", "description": "描述", "key_events": ["事件"]}
  ],
  "beat_sheet": [
    {"chapter": 1, "beat": "开局", "description": "描述"}
  ],
  "cool_point_schedule": [
    {"chapter": 3, "type": "觉醒", "intensity": 9}
  ],
  "conflict_schedule": [
    {"chapter": 5, "type": "人际", "description": "描述"}
  ],
  "hook_schedule": [
    {"chapter": 1, "type": "悬念", "description": "描述"}
  ]
}
```

只输出JSON。"""