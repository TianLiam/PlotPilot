"""拆书服务 - 协调爬取、分析、存储"""
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any

from domain.market.entities.novel_deconstruction import NovelDeconstruction
from domain.market.repositories.dynamic_template_repository import DynamicTemplateRepository
from infrastructure.persistence.database.connection import DatabaseConnection
from infrastructure.crawler.novel_content_crawler import NovelContentCrawler
from application.market.deconstruction.novel_deconstruction_agent import NovelDeconstructionAgent
from application.market.discovery.template_discovery_service import TemplateDiscoveryService

logger = logging.getLogger(__name__)


class NovelDeconstructionService:
    """拆书服务"""
    
    def __init__(
        self,
        db: DatabaseConnection,
        content_crawler: Optional[NovelContentCrawler] = None,
        deconstruction_agent: Optional[NovelDeconstructionAgent] = None,
        template_repo: Optional[DynamicTemplateRepository] = None,
    ):
        self.db = db
        self.content_crawler = content_crawler or NovelContentCrawler()
        self.agent = deconstruction_agent or NovelDeconstructionAgent()
        self.template_repo = template_repo
        self._ensure_tables()
    
    def _ensure_tables(self):
        """创建拆书存储表"""
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS novel_deconstructions (
                deconstruction_id TEXT PRIMARY KEY,
                novel_id TEXT NOT NULL,
                novel_name TEXT,
                author TEXT,
                platform TEXT,
                category TEXT,
                analyzed_chapters INTEGER,
                total_word_count INTEGER,
                data_json TEXT,
                created_at TEXT
            )
        """)
        self.db.execute("""
            CREATE INDEX IF NOT EXISTS idx_decon_novel 
            ON novel_deconstructions(novel_id, platform)
        """)
        self.db.commit()
    
    async def deconstruct_novel(
        self,
        platform: str,
        book_id: str,
        max_chapters: int = 30,
        max_words: int = 30000,
    ) -> NovelDeconstruction:
        """拆解小说（完整流程）
        
        1. 爬取免费章节
        2. AI深度拆解
        3. 保存结果
        4. 沉淀爆款DNA到模板库
        """
        logger.info(f"Deconstructing {platform}/{book_id}")
        
        # 1. 爬取章节
        novel_data = await self.content_crawler.crawl_novel_for_analysis(
            platform=platform,
            book_id=book_id,
            max_chapters=max_chapters,
        )
        
        if not novel_data or not novel_data.get("chapters"):
            raise ValueError(f"Failed to crawl novel: {platform}/{book_id}")
        
        # 2. 准备分析文本
        analysis_text = await self.content_crawler.get_novel_text_for_analysis(
            novel_data,
            max_words=max_words,
        )
        
        novel_info = {
            **novel_data,
            "platform": platform,
        }
        
        # 3. AI拆解
        deconstruction = await self.agent.deconstruct(
            analysis_text,
            novel_info,
            max_chapters=max_chapters,
        )
        
        # 4. 保存
        await self._save_deconstruction(deconstruction)
        
        # 5. DNA沉淀（如果启用了模板库）
        if self.template_repo and deconstruction.dna:
            await self._deposit_dna(deconstruction)
        
        logger.info(f"Deconstruction completed: {deconstruction.deconstruction_id}")
        
        return deconstruction
    
    async def _save_deconstruction(self, decon: NovelDeconstruction):
        """保存拆书结果"""
        import json
        self.db.execute("""
            INSERT INTO novel_deconstructions
            (deconstruction_id, novel_id, novel_name, author, platform, category,
             analyzed_chapters, total_word_count, data_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            decon.deconstruction_id,
            decon.novel_id,
            decon.novel_name,
            decon.author,
            decon.platform,
            decon.category,
            decon.analyzed_chapters,
            decon.total_word_count,
            json.dumps(decon.to_dict(), ensure_ascii=False),
            datetime.utcnow().isoformat(),
        ))
        self.db.commit()
    
    async def get_deconstruction(self, deconstruction_id: str) -> Optional[NovelDeconstruction]:
        """获取拆书结果"""
        import json
        row = self.db.fetch_one(
            "SELECT data_json FROM novel_deconstructions WHERE deconstruction_id = ?",
            (deconstruction_id,)
        )
        if not row:
            return None
        data = json.loads(row["data_json"])
        # 简化：直接返回字典，实际应反序列化为实体
        return data
    
    async def list_deconstructions(
        self,
        platform: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """列出拆书结果"""
        conditions = ["1=1"]
        params = []
        if platform:
            conditions.append("platform = ?")
            params.append(platform)
        if category:
            conditions.append("category = ?")
            params.append(category)
        params.append(limit)
        
        rows = self.db.fetch_all(
            f"""SELECT deconstruction_id, novel_id, novel_name, author, platform, category,
                analyzed_chapters, total_word_count, created_at
                FROM novel_deconstructions
                WHERE {' AND '.join(conditions)}
                ORDER BY created_at DESC
                LIMIT ?""",
            params
        )
        
        return [
            {
                "deconstruction_id": r["deconstruction_id"],
                "novel_id": r["novel_id"],
                "novel_name": r["novel_name"],
                "author": r["author"],
                "platform": r["platform"],
                "category": r["category"],
                "analyzed_chapters": r["analyzed_chapters"],
                "total_word_count": r["total_word_count"],
                "created_at": r["created_at"],
            }
            for r in rows
        ]
    
    async def _deposit_dna(self, decon: NovelDeconstruction):
        """将爆款DNA沉淀到动态模板库"""
        from domain.market.entities.dynamic_template import (
            DiscoveredTemplate,
            TemplatePattern,
            TemplateType,
            TrendDirection,
            SourceNovel,
        )
        import uuid
        
        dna = decon.dna
        if not dna:
            return
        
        templates = []
        
        # 开局模板
        if dna.opening_template:
            templates.append(DiscoveredTemplate(
                id=f"dna-{uuid.uuid4().hex[:12]}",
                pattern=TemplatePattern(
                    name=f"[拆书]{decon.novel_name[:10]}开局模式",
                    description=dna.opening_template,
                    pattern_type=TemplateType.OPENING,
                    genre=decon.category,
                    content=dna.opening_template,
                    source_novels=[SourceNovel(
                        platform=decon.platform,
                        novel_id=decon.novel_id,
                        novel_name=decon.novel_name,
                        author=decon.author,
                        rank=1,
                        category=decon.category,
                    )],
                    occurrence_count=1,
                    confidence_score=0.7,
                    trend=TrendDirection.STABLE,
                ),
            ))
        
        # 爽点模板
        if dna.cool_point_formula:
            templates.append(DiscoveredTemplate(
                id=f"dna-{uuid.uuid4().hex[:12]}",
                pattern=TemplatePattern(
                    name=f"[拆书]{decon.novel_name[:10]}爽点模式",
                    description=dna.cool_point_formula,
                    pattern_type=TemplateType.COOL_POINT,
                    genre=decon.category,
                    content=dna.cool_point_formula,
                    source_novels=[SourceNovel(
                        platform=decon.platform,
                        novel_id=decon.novel_id,
                        novel_name=decon.novel_name,
                        author=decon.author,
                        rank=1,
                        category=decon.category,
                    )],
                    occurrence_count=1,
                    confidence_score=0.7,
                    trend=TrendDirection.STABLE,
                ),
            ))
        
        # 人物模板
        if dna.character_formula:
            templates.append(DiscoveredTemplate(
                id=f"dna-{uuid.uuid4().hex[:12]}",
                pattern=TemplatePattern(
                    name=f"[拆书]{decon.novel_name[:10]}人物模式",
                    description=dna.character_formula,
                    pattern_type=TemplateType.CHARACTER,
                    genre=decon.category,
                    content=dna.character_formula,
                    source_novels=[SourceNovel(
                        platform=decon.platform,
                        novel_id=decon.novel_id,
                        novel_name=decon.novel_name,
                        author=decon.author,
                        rank=1,
                        category=decon.category,
                    )],
                    occurrence_count=1,
                    confidence_score=0.7,
                    trend=TrendDirection.STABLE,
                ),
            ))
        
        for t in templates:
            try:
                await self.template_repo.save(t)
            except Exception as e:
                logger.error(f"Failed to deposit DNA template: {e}")
    
    async def get_dna_library(self, limit: int = 50) -> List[Dict[str, Any]]:
        """获取DNA库（从拆书结果中提取）"""
        import json
        rows = self.db.fetch_all(
            """SELECT data_json FROM novel_deconstructions
               WHERE data_json LIKE '%dna%'
               ORDER BY created_at DESC
               LIMIT ?""",
            (limit,)
        )
        
        dnas = []
        for row in rows:
            data = json.loads(row["data_json"])
            if data.get("dna"):
                dnas.append(data["dna"])
        
        return dnas