"""Agent3: 题材策划Agent - 确定题材和金手指"""
import logging
from typing import Dict, Any

from engine.pipeline.agents.base_agent import BaseAgent
from engine.pipeline.entities.pipeline_entities import AgentType, PipelineContext

logger = logging.getLogger(__name__)


class TopicPlanningAgent(BaseAgent):
    """题材策划Agent
    
    基于趋势分析结果，确定题材、金手指、核心卖点。
    """
    
    agent_type = AgentType.TOPIC_PLANNING
    
    def get_required_inputs(self) -> list:
        return [AgentType.SCAN_RANKING, AgentType.TREND_ANALYSIS]
    
    async def execute(self, context: PipelineContext) -> Dict[str, Any]:
        """执行题材策划"""
        scan_result = context.scan_result
        trend_result = context.trend_result
        user_request = context.user_request
        
        # 用户预设的题材偏好
        preferred_genres = user_request.get("genres", [])
        preferred_gfs = user_request.get("golden_fingers", [])
        
        # 构建提示词
        prompt = self._build_prompt(scan_result, trend_result, preferred_genres, preferred_gfs)
        
        # 调用LLM策划
        response = await self.generate(prompt, max_tokens=3000, temperature=0.7)
        
        # 解析结果
        result = self.parse_json_response(response)
        
        # 确保必要字段
        result.setdefault("selected_genres", preferred_genres)
        result.setdefault("selected_golden_fingers", preferred_gfs)
        result.setdefault("core_selling_point", "")
        result.setdefault("target_audience", "")
        result.setdefault("differentiation_strategy", "")
        result.setdefault("success_prediction", 0.5)
        
        return result
    
    def _build_prompt(
        self,
        scan_result: Dict[str, Any],
        trend_result: Dict[str, Any],
        preferred_genres: list,
        preferred_gfs: list,
    ) -> str:
        """构建题材策划提示词"""
        rising = trend_result.get("rising_genres", [])
        opportunities = trend_result.get("opportunities", [])
        
        rising_str = ", ".join([g.get("genre", "") for g in rising[:5]])
        opp_str = "\n".join([f"- {o.get('opportunity', '')}" for o in opportunities[:3]])
        
        user_pref = ""
        if preferred_genres:
            user_pref = f"\n用户偏好题材: {', '.join(preferred_genres)}"
        if preferred_gfs:
            user_pref += f"\n用户偏好金手指: {', '.join(preferred_gfs)}"
        
        return f"""你是一位资深的网文策划编辑。请基于市场趋势，策划一部有爆款潜力的小说。

## 市场趋势
上升题材: {rising_str}

## 创作机会
{opp_str}
{user_pref}

请策划：
1. 选择题材组合（selected_genres）
2. 选择金手指组合（selected_golden_fingers）
3. 确定核心卖点（core_selling_point）
4. 目标读者（target_audience）
5. 差异化策略（differentiation_strategy）
6. 预测成功率（success_prediction, 0-1）

以JSON格式输出：

```json
{
  "selected_genres": ["题材1", "题材2"],
  "selected_golden_fingers": ["金手指1", "金手指2"],
  "core_selling_point": "核心卖点描述",
  "target_audience": "目标读者描述",
  "differentiation_strategy": "如何与同类作品区分",
  "success_prediction": 0.75,
  "rationale": "选择理由"
}
```

只输出JSON。"""