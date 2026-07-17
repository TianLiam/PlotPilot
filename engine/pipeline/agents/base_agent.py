"""Agent基类"""
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, Optional

from engine.pipeline.entities.pipeline_entities import (
    AgentType,
    AgentStatus,
    AgentOutput,
    PipelineContext,
)
from infrastructure.ai.llm_client import LLMClient

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Agent基类
    
    所有Agent继承此基类，实现具体的execute方法。
    """
    
    agent_type: AgentType
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm_client = llm_client or LLMClient()
        self.output: AgentOutput = AgentOutput(agent_type=self.agent_type)
    
    async def run(self, context: PipelineContext) -> AgentOutput:
        """运行Agent
        
        Args:
            context: 流水线上下文（包含所有前置Agent的输出）
        
        Returns:
            Agent输出
        """
        self.output = AgentOutput(agent_type=self.agent_type)
        self.output.status = AgentStatus.RUNNING
        self.output.started_at = datetime.utcnow()
        
        try:
            # 执行具体逻辑
            result = await self.execute(context)
            
            self.output.data = result
            self.output.status = AgentStatus.COMPLETED
            self.output.completed_at = datetime.utcnow()
            self.output.duration_seconds = (
                self.output.completed_at - self.output.started_at
            ).total_seconds()
            
            # 更新上下文
            context.set_agent_output(self.agent_type, result)
            
            logger.info(
                f"Agent {self.agent_type.value} completed in "
                f"{self.output.duration_seconds:.2f}s"
            )
            
        except Exception as e:
            logger.error(f"Agent {self.agent_type.value} failed: {e}")
            self.output.status = AgentStatus.FAILED
            self.output.error = str(e)
            self.output.completed_at = datetime.utcnow()
            self.output.duration_seconds = (
                self.output.completed_at - self.output.started_at
            ).total_seconds()
        
        return self.output
    
    @abstractmethod
    async def execute(self, context: PipelineContext) -> Dict[str, Any]:
        """执行Agent的具体逻辑（子类实现）"""
        pass
    
    def get_required_inputs(self) -> list:
        """获取此Agent需要的前置输入（子类可覆写）"""
        return []
    
    def can_run(self, context: PipelineContext) -> bool:
        """检查是否可以运行（前置条件是否满足）"""
        required = self.get_required_inputs()
        for agent_type in required:
            output = context.get_agent_output(agent_type)
            if not output:
                return False
        return True
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """调用LLM生成"""
        response = await self.llm_client.generate(
            prompt,
            max_tokens=kwargs.get("max_tokens", 4000),
            temperature=kwargs.get("temperature", 0.7),
        )
        return response
    
    def parse_json_response(self, response: str) -> Dict[str, Any]:
        """解析JSON响应"""
        import json
        import re
        
        json_match = response
        if "```json" in response:
            start = response.find("```json") + 7
            end = response.find("```", start)
            json_match = response[start:end].strip()
        elif "```" in response:
            start = response.find("```") + 3
            end = response.find("```", start)
            json_match = response[start:end].strip()
        
        try:
            return json.loads(json_match)
        except json.JSONDecodeError:
            # 尝试提取 JSON 对象
            match = re.search(r'\{.*\}', json_match, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except:
                    pass
            return {}