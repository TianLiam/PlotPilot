from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import logging

from application.market.recommender.template_recommender_service import TemplateRecommenderService
from domain.market.entities.template import Template
from infrastructure.persistence.database.connection import get_database
from infrastructure.persistence.database.market.sqlite_template_repository import SqliteTemplateRepository
from uuid import uuid4

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/market/templates", tags=["market-templates"])


def get_template_recommender_service() -> TemplateRecommenderService:
    repo = SqliteTemplateRepository(get_database())
    return TemplateRecommenderService(repo)


class CreateTemplateRequest(BaseModel):
    name: str = Field(..., description="模板名称")
    template_type: str = Field(..., description="模板类型")
    genre: str = Field(..., description="适用题材")
    content: str = Field(..., description="模板内容")
    description: str = Field("", description="模板描述")


class UpdateTemplateRequest(BaseModel):
    name: Optional[str] = Field(None, description="模板名称")
    template_type: Optional[str] = Field(None, description="模板类型")
    genre: Optional[str] = Field(None, description="适用题材")
    content: Optional[str] = Field(None, description="模板内容")
    description: Optional[str] = Field(None, description="模板描述")


@router.get("/golden-fingers")
async def get_golden_fingers(
    genre: str = "",
    limit: int = 10,
    service: TemplateRecommenderService = Depends(get_template_recommender_service)
):
    try:
        templates = service.get_golden_fingers(genre, limit)
        return templates
    except Exception as e:
        logger.error(f"Failed to get golden fingers: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get golden fingers: {str(e)}")


@router.get("/characters")
async def get_characters(
    genre: str = "",
    limit: int = 10,
    service: TemplateRecommenderService = Depends(get_template_recommender_service)
):
    try:
        templates = service.get_characters(genre, limit)
        return templates
    except Exception as e:
        logger.error(f"Failed to get characters: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get characters: {str(e)}")


@router.get("/worldviews")
async def get_worldviews(
    genre: str = "",
    limit: int = 10,
    service: TemplateRecommenderService = Depends(get_template_recommender_service)
):
    try:
        templates = service.get_worldviews(genre, limit)
        return templates
    except Exception as e:
        logger.error(f"Failed to get worldviews: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get worldviews: {str(e)}")


@router.get("/cool-points")
async def get_cool_points(
    genre: str = "",
    limit: int = 10,
    service: TemplateRecommenderService = Depends(get_template_recommender_service)
):
    try:
        templates = service.get_cool_points(genre, limit)
        return templates
    except Exception as e:
        logger.error(f"Failed to get cool points: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get cool points: {str(e)}")


@router.get("/search")
async def search_templates(
    keyword: str,
    service: TemplateRecommenderService = Depends(get_template_recommender_service)
):
    try:
        templates = service.search_templates(keyword)
        return templates
    except Exception as e:
        logger.error(f"Failed to search templates: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to search templates: {str(e)}")


@router.get("/{template_id}")
async def get_template_detail(
    template_id: str,
    service: TemplateRecommenderService = Depends(get_template_recommender_service)
):
    try:
        template = service.get_template_detail(template_id)
        if not template:
            raise HTTPException(status_code=404, detail=f"Template not found: {template_id}")
        return template
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get template detail: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get template detail: {str(e)}")


@router.post("/")
async def create_template(
    request: CreateTemplateRequest,
    service: TemplateRecommenderService = Depends(get_template_recommender_service)
):
    try:
        template = Template(
            id=str(uuid4()),
            name=request.name,
            template_type=request.template_type,
            genre=request.genre,
            content=request.content,
            description=request.description
        )
        service.template_repository.save(template)
        return {"id": template.id, "name": template.name, "message": "Template created successfully"}
    except Exception as e:
        logger.error(f"Failed to create template: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create template: {str(e)}")


@router.put("/{template_id}")
async def update_template(
    template_id: str,
    request: UpdateTemplateRequest,
    service: TemplateRecommenderService = Depends(get_template_recommender_service)
):
    try:
        template = service.template_repository.get_by_id(template_id)
        if not template:
            raise HTTPException(status_code=404, detail=f"Template not found: {template_id}")
        
        if request.name is not None:
            template.name = request.name
        if request.template_type is not None:
            template.template_type = request.template_type
        if request.genre is not None:
            template.genre = request.genre
        if request.content is not None:
            template.content = request.content
        if request.description is not None:
            template.description = request.description
        
        service.template_repository.save(template)
        return {"id": template.id, "name": template.name, "message": "Template updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update template: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update template: {str(e)}")


@router.post("/{template_id}/use")
async def use_template(
    template_id: str,
    service: TemplateRecommenderService = Depends(get_template_recommender_service)
):
    try:
        success = service.use_template(template_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"Failed to use template: {template_id}")
        return {"message": "Template usage incremented"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to use template: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to use template: {str(e)}")


@router.delete("/{template_id}")
async def delete_template(
    template_id: str,
    service: TemplateRecommenderService = Depends(get_template_recommender_service)
):
    try:
        service.template_repository.delete(template_id)
        return {"message": "Template deleted successfully"}
    except Exception as e:
        logger.error(f"Failed to delete template: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete template: {str(e)}")