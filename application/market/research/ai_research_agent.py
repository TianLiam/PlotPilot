"""AI研究Agent - 使用LLM生成完整创作前研究报告"""
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
import uuid

from domain.market.entities.novel_research import (
    GenreRequest,
    NovelResearch,
    ResearchStatus,
    GenreStats,
    OpeningPattern,
    RecommendationItem,
    HistoricalSample,
)
from infrastructure.ai.llm_client import LLMClient

logger = logging.getLogger(__name__)


RESEARCH_SYSTEM_PROMPT = """你是一位资深的网文策划编辑，擅长创作前的市场调研和策略分析。

你的任务是基于用户提供的数据，为用户即将创作的小说生成一份完整的「创作前研究报告」。

报告需要包含：

1. **市场可行性评估**：
   - 题材组合的可行性（基于历史数据）
   - 预期成功率
   - 风险等级

2. **最佳设定建议**：
   - 推荐采用的开局模式
   - 推荐采用的金手指组合
   - 推荐的人物设定方向
   - 推荐的世界观元素
   - 推荐的目标字数和章节长度

3. **应避免的陷阱**：
   - 已经被过度使用的套路
   - 正在退潮的元素
   - 内在矛盾的设定
   - 容易引发读者弃书的雷区

4. **时机分析**：
   - 现在进入该题材是合适的时机吗？
   - 是否有上升趋势？
   - 市场窗口期预计多久？

5. **竞品分析**：
   - 同类成功作品分析
   - 它们的共同特点
   - 如何差异化竞争

6. **完整建议总结**：
   - 用 200-300 字给出最终建议
   - 包括：是否值得写、核心卖点、关键风险、下一步行动

请以 JSON 格式输出：

```json
{
  "feasibility": {
    "score": 0-100,
    "level": "high/medium/low",
    "summary": "可行性总结"
  },
  "recommendations": {
    "opening": "推荐的开局模式描述",
    "golden_finger": "推荐的金手指组合描述",
    "character": "推荐的人物设定方向",
    "worldview": "推荐的世界观元素",
    "target_words": 推荐字数,
    "chapter_length": 推荐章节字数
  },
  "avoid": [
    {
      "item": "应避免的元素",
      "reason": "原因"
    }
  ],
  "timing": {
    "is_good_timing": true/false,
    "trend": "rising/stable/declining",
    "window_months": 6,
    "advice": "时机建议"
  },
  "competitors": {
    "sample_novels": ["参考作品1", "参考作品2"],
    "common_features": ["共同特点1", "共同特点2"],
    "differentiation": "差异化建议"
  },
  "summary": "完整建议总结（200-300字）",
  "warnings": ["重要警告1", "重要警告2"]
}
```

注意：
- 只输出 JSON，不要输出其他内容
- 建议要具体、可操作
- 基于提供的数据，避免空泛描述
- 风险要清晰，不要夸大也不要忽视"""


class AIResearchAgent:
    """AI研究Agent"""
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm_client = llm_client or LLMClient()
    
    async def generate_research_report(
        self,
        user_request: GenreRequest,
        historical_data: Dict[str, Any],
    ) -> NovelResearch:
        """生成完整研究报告
        
        Args:
            user_request: 用户请求
            historical_data: 历史数据（包括成功率、开局模式、冲突检测结果等）
        
        Returns:
            完整的研究报告
        """
        research_id = f"research-{uuid.uuid4().hex[:12]}"
        
        research = NovelResearch(
            research_id=research_id,
            user_request=user_request,
            status=ResearchStatus.ANALYZING,
            sample_count=historical_data.get("total_samples", 0),
            genre_stats=historical_data.get("genre_stats", []),
            opening_patterns=historical_data.get("opening_patterns", []),
        )
        
        try:
            # 构建提示词
            prompt = self._build_research_prompt(user_request, historical_data)
            
            # 调用LLM
            response = await self.llm_client.generate(
                prompt,
                system_prompt=RESEARCH_SYSTEM_PROMPT,
                require_real_provider=True,
                max_tokens=6000,
                temperature=0.5,
            )
            
            # 解析结果
            result = self._parse_response(response)
            
            # 填充研究报告
            self._populate_research(research, result, historical_data)
            
            research.status = ResearchStatus.COMPLETED
            research.completed_at = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Failed to generate research: {e}")
            research.status = ResearchStatus.FAILED
            research.ai_warnings = f"AI分析失败: {str(e)}"
        
        return research
    
    def _build_research_prompt(
        self,
        user_request: GenreRequest,
        historical_data: Dict[str, Any],
    ) -> str:
        """构建提示词"""
        
        # 题材统计
        genre_stats_text = ""
        for stats in historical_data.get("genre_stats", []):
            genre_stats_text += f"""
- {stats.genre}:
  - 样本数: {stats.total_novels} (成功: {stats.successful_novels})
  - 成功率: {stats.success_rate:.1%}
  - 平均字数: {stats.avg_word_count:,}
  - 平均章节数: {stats.avg_chapter_count}
  - 推荐章节字数: {stats.optimal_chapter_words}
  - 趋势: {stats.trend} ({stats.trend_change:+.1f}%)
"""
        
        # 开局模式
        openings_text = ""
        for p in historical_data.get("opening_patterns", []):
            openings_text += f"""
- {p.name}: 成功率 {p.success_rate:.1%}, 平均热度 {p.avg_popularity:,.0f}
  关键点: {', '.join(p.key_points[:3])}
  样例: {', '.join(p.sample_novels[:3])}
"""
        
        # 金手指冲突
        conflicts_text = ""
        conflicts = historical_data.get("conflicts", [])
        if conflicts:
            conflicts_text = "\n".join([
                f"- [{c.get('severity', 'info')}] {c.get('golden_finger', '')}: {c.get('message', '')}"
                for c in conflicts
            ])
        else:
            conflicts_text = "无明显冲突"
        
        # 饱和度
        saturation = historical_data.get("saturation", {})
        saturation_text = f"""
- 饱和度等级: {saturation.get('level', 'unknown')}
- 饱和度评分: {saturation.get('score', 0):.0%}
- 说明: {saturation.get('message', '')}
"""
        
        # 趋势信息
        timing = historical_data.get("timing", {})
        timing_text = f"""
- 当前时机评分: {timing.get('timing_score', 0):.0f}/100
- 时机建议: {timing.get('timing_advice', '')}
"""
        
        prompt = f"""# 创作前研究数据

## 用户请求
- 题材: {', '.join(user_request.genres) if user_request.genres else '未指定'}
- 金手指: {', '.join(user_request.golden_fingers) if user_request.golden_fingers else '未指定'}
- 关键词: {', '.join(user_request.keywords) if user_request.keywords else '无'}
- 目标字数: {user_request.target_word_count or '未指定'}
- 目标章节: {user_request.target_chapter_count or '未指定'}
- 额外说明: {user_request.additional_notes or '无'}

## 历史样本统计
- 总样本数: {historical_data.get('total_samples', 0)}
- 成功样本数: {historical_data.get('successful_samples', 0)}
- 综合成功率: {historical_data.get('success_rate', 0):.1%}

## 题材详细统计
{genre_stats_text if genre_stats_text else '暂无数据'}

## 成功开局模式
{openings_text if openings_text else '暂无数据'}

## 金手指冲突检测
{conflicts_text}

## 市场饱和度
{saturation_text}

## 时机分析
{timing_text}

## 同类成功作品
{', '.join(historical_data.get('sample_novels', [])[:10]) if historical_data.get('sample_novels') else '无'}

---

基于以上数据，生成完整的创作前研究报告。"""
        
        return prompt
    
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
            return {}
    
    def _populate_research(
        self,
        research: NovelResearch,
        result: Dict[str, Any],
        historical_data: Dict[str, Any],
    ):
        """填充研究报告"""
        # 可行性评分
        feasibility = result.get("feasibility", {})
        research.overall_score = feasibility.get("score", 0)
        research.risk_level = self._calculate_risk_level(feasibility.get("score", 0))
        
        # AI生成内容
        research.ai_summary = result.get("summary", "")
        research.ai_warnings = "\n".join(result.get("warnings", []))
        
        # 时机
        timing = result.get("timing", {})
        research.timing_score = timing.get("window_months", 0) * 10  # 简化
        research.timing_advice = timing.get("advice", "")
        
        # 构建建议
        recommendations = result.get("recommendations", {})
        avoid_items = result.get("avoid", [])
        
        # 推荐的设定
        if recommendations:
            research.recommendations.append(RecommendationItem(
                type="recommend",
                title="推荐设定",
                description=self._format_recommendations(recommendations),
                confidence=0.85,
                reason="基于AI综合分析",
                references=historical_data.get("sample_novels", [])[:5],
            ))
        
        # 应避免的元素
        for item in avoid_items:
            research.recommendations.append(RecommendationItem(
                type="avoid",
                title=item.get("item", ""),
                description=item.get("reason", ""),
                confidence=0.8,
                reason="已识别风险",
            ))
        
        # 风险因素
        research.risk_factors = [item.get("item", "") for item in avoid_items]
        
        # AI建议
        research.ai_suggestions = self._format_suggestions(result)
    
    def _calculate_risk_level(self, score: float) -> str:
        """根据评分计算风险等级"""
        if score >= 70:
            return "low"
        elif score >= 50:
            return "medium"
        else:
            return "high"
    
    def _format_recommendations(self, recommendations: Dict) -> str:
        """格式化推荐设定"""
        parts = []
        if recommendations.get("opening"):
            parts.append(f"**开局模式**：{recommendations['opening']}")
        if recommendations.get("golden_finger"):
            parts.append(f"**金手指**：{recommendations['golden_finger']}")
        if recommendations.get("character"):
            parts.append(f"**人物设定**：{recommendations['character']}")
        if recommendations.get("worldview"):
            parts.append(f"**世界观**：{recommendations['worldview']}")
        if recommendations.get("target_words"):
            parts.append(f"**目标字数**：{recommendations['target_words']:,}")
        if recommendations.get("chapter_length"):
            parts.append(f"**章节字数**：{recommendations['chapter_length']}")
        return "\n\n".join(parts)
    
    def _format_suggestions(self, result: Dict) -> str:
        """格式化建议"""
        parts = []
        
        competitors = result.get("competitors", {})
        if competitors:
            parts.append("## 竞品分析")
            if competitors.get("sample_novels"):
                parts.append(f"参考作品：{', '.join(competitors['sample_novels'])}")
            if competitors.get("common_features"):
                parts.append(f"共同特点：{', '.join(competitors['common_features'])}")
            if competitors.get("differentiation"):
                parts.append(f"差异化建议：{competitors['differentiation']}")
        
        return "\n\n".join(parts)
