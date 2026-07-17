"""动态模板发现模块"""
from domain.market.entities.dynamic_template import (
    DiscoveredTemplate,
    TemplatePattern,
    TemplateType,
    TrendDirection,
    SourceNovel,
)
from domain.market.repositories.dynamic_template_repository import DynamicTemplateRepository
from infrastructure.persistence.database.market.sqlite_dynamic_template_repository import SqliteDynamicTemplateRepository
from application.market.analyzer.bestseller_analysis_agent import BestsellerAnalysisAgent
from application.market.discovery.template_discovery_service import TemplateDiscoveryService

__all__ = [
    "DiscoveredTemplate",
    "TemplatePattern",
    "TemplateType",
    "TrendDirection",
    "SourceNovel",
    "DynamicTemplateRepository",
    "SqliteDynamicTemplateRepository",
    "BestsellerAnalysisAgent",
    "TemplateDiscoveryService",
]