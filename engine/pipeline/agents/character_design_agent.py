"""Agent4: 人物设计Agent - 设计主角和配角"""
import logging
from typing import Dict, Any

from engine.pipeline.agents.base_agent import BaseAgent
from engine.pipeline.entities.pipeline_entities import AgentType

logger = logging.getLogger(__name__)


class CharacterDesignAgent(BaseAgent):
    """人物设计Agent"""
    
    agent_type = AgentType.CHARACTER_DESIGN
    
    def get_required_inputs(self) -> list:
        return [AgentType.TOPIC_PLANNING]
    
    async def execute(self, context: PipelineContext) -> Dict[str, Any]:
        """执行人物设计"""
        topic_result = context.topic_result
        
        genres = topic_result.get("selected_genres", [])
        golden_fingers = topic_result.get("selected_golden_fingers", [])
        core_selling_point = topic_result.get("core_selling_point", "")
        
        prompt = self._build_prompt(genres, golden_fingers, core_selling_point)
        
        response = await self.generate(prompt, max_tokens=4000, temperature=0.7)
        result = self.parse_json_response(response)
        
        result.setdefault("protagonist", {})
        result.setdefault("antagonists", [])
        result.setdefault("supporting_characters", [])
        result.setdefault("relationships", [])
        
        return result
    
    def _build_prompt(self, genres: list, golden_fingers: list, core_selling_point: str) -> str:
        return f"""你是网文人物设定专家。请为以下小说设计人物。

## 题材: {', '.join(genres)}
## 金手指: {', '.join(golden_fingers)}
## 核心卖点: {core_selling_point}

请设计：
1. 主角（protagonist）：名字、性格、动机、目标、缺陷、成长弧线
2. 反派（antagonists）：名字、动机、与主角的冲突
3. 重要配角（supporting_characters）：名字、角色、与主角关系
4. 人物关系网（relationships）

以JSON格式输出：

```json
{
  "protagonist": {
    "name": "主角名",
    "age": 25,
    "personality": ["性格1", "性格2"],
    "motivation": "核心动机",
    "goal": "目标",
    "flaw": "缺陷",
    "growth_arc": "成长弧线",
    "background": "背景故事"
  },
  "antagonists": [
    {
      "name": "反派名",
      "motivation": "动机",
      "conflict_with_protagonist": "与主角的冲突"
    }
  ],
  "supporting_characters": [
    {
      "name": "配角名",
      "role": "角色定位",
      "relationship": "与主角关系"
    }
  ],
  "relationships": [
    {"from": "人物A", "to": "人物B", "type": "关系类型"}
  ]
}
```

只输出JSON。"""