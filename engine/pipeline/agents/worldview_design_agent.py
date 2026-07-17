"""Agent5: 世界观设计Agent"""
import logging
from typing import Dict, Any

from engine.pipeline.agents.base_agent import BaseAgent
from engine.pipeline.entities.pipeline_entities import AgentType, PipelineContext

logger = logging.getLogger(__name__)


class WorldviewDesignAgent(BaseAgent):
    """世界观设计Agent"""
    
    agent_type = AgentType.WORLDVIEW_DESIGN
    
    def get_required_inputs(self) -> list:
        return [AgentType.TOPIC_PLANNING, AgentType.CHARACTER_DESIGN]
    
    async def execute(self, context: PipelineContext) -> Dict[str, Any]:
        """执行世界观设计"""
        topic_result = context.topic_result
        character_result = context.character_result
        
        genres = topic_result.get("selected_genres", [])
        golden_fingers = topic_result.get("selected_golden_fingers", [])
        protagonist = character_result.get("protagonist", {})
        
        prompt = self._build_prompt(genres, golden_fingers, protagonist)
        
        response = await self.generate(prompt, max_tokens=4000, temperature=0.7)
        result = self.parse_json_response(response)
        
        result.setdefault("world_name", "")
        result.setdefault("power_system", "")
        result.setdefault("geography", [])
        result.setdefault("factions", [])
        result.setdefault("rules", [])
        
        return result
    
    def _build_prompt(self, genres: list, golden_fingers: list, protagonist: dict) -> str:
        return f"""你是网文世界观设定专家。请为以下小说设计世界观。

## 题材: {', '.join(genres)}
## 金手指: {', '.join(golden_fingers)}
## 主角: {protagonist.get('name', '未知')}

请设计：
1. 世界名称和背景（world_name）
2. 力量体系（power_system）
3. 重要地点（geography）
4. 势力组织（factions）
5. 世界规则/限制（rules）

以JSON格式输出：

```json
{
  "world_name": "世界名称",
  "power_system": "力量体系描述",
  "power_levels": ["等级1", "等级2"],
  "geography": [
    {"name": "地点名", "description": "描述", "significance": "重要性"}
  ],
  "factions": [
    {"name": "势力名", "description": "描述", "stance": "立场"}
  ],
  "rules": [
    "规则1",
    "规则2"
  ],
  "special_elements": ["特殊元素1"]
}
```

只输出JSON。"""