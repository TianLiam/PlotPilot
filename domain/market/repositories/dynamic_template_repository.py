"""动态模板仓储接口"""
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from domain.market.entities.dynamic_template import (
    DiscoveredTemplate,
    TemplateType,
    TrendDirection,
)


class DynamicTemplateRepository(ABC):
    """动态模板仓储接口"""
    
    @abstractmethod
    async def save(self, template: DiscoveredTemplate) -> DiscoveredTemplate:
        """保存模板"""
        pass
    
    @abstractmethod
    async def get_by_id(self, template_id: str) -> Optional[DiscoveredTemplate]:
        """根据ID获取模板"""
        pass
    
    @abstractmethod
    async def get_by_name_and_type(
        self, 
        name: str, 
        pattern_type: TemplateType
    ) -> Optional[DiscoveredTemplate]:
        """根据名称和类型获取模板"""
        pass
    
    @abstractmethod
    async def list_by_type(
        self, 
        pattern_type: TemplateType,
        limit: int = 20
    ) -> List[DiscoveredTemplate]:
        """按类型列出模板"""
        pass
    
    @abstractmethod
    async def list_by_genre(
        self, 
        genre: str,
        limit: int = 20
    ) -> List[DiscoveredTemplate]:
        """按题材列出模板"""
        pass
    
    @abstractmethod
    async def list_trending(self, limit: int = 10) -> List[DiscoveredTemplate]:
        """获取热门模板"""
        pass
    
    @abstractmethod
    async def list_recent(self, days: int = 7, limit: int = 20) -> List[DiscoveredTemplate]:
        """获取最近发现的模板"""
        pass
    
    @abstractmethod
    async def update_usage(self, template_id: str) -> None:
        """更新使用次数"""
        pass
    
    @abstractmethod
    async def update_trend(
        self, 
        template_id: str, 
        trend: TrendDirection,
        trend_value: float
    ) -> None:
        """更新趋势"""
        pass
    
    @abstractmethod
    async def delete_old(self, days: int = 30) -> int:
        """删除旧模板（deprecated超过指定天数）"""
        pass
    
    @abstractmethod
    async def search(
        self,
        keyword: str,
        pattern_type: Optional[TemplateType] = None,
        genre: Optional[str] = None,
        limit: int = 20
    ) -> List[DiscoveredTemplate]:
        """搜索模板"""
        pass