"""短篇创作 API 路由 — 知乎盐选/番茄短故事"""
from __future__ import annotations

import logging
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from application.core.short_story_templates import (
    load_yanxuan_templates,
    get_template_by_id,
    build_premise_from_template,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/short-story", tags=["short-story"])


@router.get("/templates")
async def list_templates() -> List[Dict[str, Any]]:
    """获取知乎盐选短篇题材模板列表"""
    try:
        return load_yanxuan_templates()
    except Exception as e:
        logger.error("加载短篇模板失败: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"加载模板失败: {str(e)}")


@router.get("/templates/{template_id}")
async def get_template(template_id: str) -> Dict[str, Any]:
    """获取单个题材模板详情"""
    tpl = get_template_by_id(template_id)
    if not tpl:
        raise HTTPException(status_code=404, detail=f"模板不存在: {template_id}")
    return tpl


class BuildPremiseRequest(BaseModel):
    """根据模板生成 premise"""
    template_id: str
    user_idea: str = ""


@router.post("/build-premise")
async def build_premise(req: BuildPremiseRequest) -> Dict[str, str]:
    """根据模板 + 用户创意生成 premise 文本"""
    tpl = get_template_by_id(req.template_id)
    if not tpl:
        raise HTTPException(status_code=404, detail=f"模板不存在: {req.template_id}")
    premise = build_premise_from_template(req.template_id, req.user_idea)
    return {"premise": premise, "template_name": tpl.get("name", "")}


class SubmissionMetaResponse(BaseModel):
    """投稿元信息"""
    hook_quote: str = ""  # 15-25 字吸睛金句
    short_intro: str = ""  # 100-150 字简介
    synopsis: str = ""  # 300-500 字梗概
    tags: List[str] = []  # 3-5 个题材标签
    title_suggestion: str = ""  # 带关键词的标题建议
    opening_optimization: str = ""  # 开篇 300 字优化建议


@router.post("/{novel_id}/submission-meta")
async def generate_submission_meta(novel_id: str) -> SubmissionMetaResponse:
    """生成知乎盐选投稿必填项（金句/简介/梗概/标签）

    读取短篇全文，调用 LLM 生成投稿所需的元信息。
    """
    try:
        from interfaces.api.dependencies import get_novel_repository, get_chapter_repository
        from domain.novel.value_objects.novel_id import NovelId

        novel_repo = get_novel_repository()
        chapter_repo = get_chapter_repository()

        novel = novel_repo.get_by_id(NovelId(novel_id))
        if not novel:
            raise HTTPException(status_code=404, detail=f"小说不存在: {novel_id}")

        chapters = chapter_repo.list_by_novel(NovelId(novel_id))
        chapters.sort(key=lambda x: x.number)

        if not chapters:
            raise HTTPException(status_code=400, detail="短篇还没有内容，无法生成投稿元信息")

        # 拼接全文
        full_content = f"标题。{novel.title}\n\n"
        for ch in chapters:
            full_content += f"【{ch.number}】{ch.title or ''}\n{ch.content or ''}\n\n"

        # 调用 LLM 生成投稿元信息
        meta = await _call_llm_for_submission_meta(full_content, novel.premise or "")
        return meta

    except HTTPException:
        raise
    except Exception as e:
        logger.error("生成投稿元信息失败: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"生成失败: {str(e)}")


async def _call_llm_for_submission_meta(full_content: str, premise: str) -> SubmissionMetaResponse:
    """调用 LLM 生成投稿元信息"""
    try:
        # 通过 PromptRegistry 渲染 CPMS 提示词节点
        from infrastructure.ai.prompt_registry import get_prompt_registry

        registry = get_prompt_registry()
        prompt = registry.render_to_prompt(
            "short-story-submission-meta",
            {
                "full_content": full_content[:8000],  # 截断防止超长
                "genre": premise[:200] if premise else "通用",
            },
        )

        if not prompt:
            logger.warning("CPMS 提示词节点 short-story-submission-meta 不可用，返回空值")
            return SubmissionMetaResponse()

        # 调用 LLM
        from infrastructure.ai.llm_client import LLMClient

        client = LLMClient()
        raw = await client.generate(
            prompt.user,
            system_prompt=prompt.system,
            temperature=0.7,
            max_tokens=2000,
        )

        # 解析 JSON 响应
        import json
        import re

        raw_text = raw if isinstance(raw, str) else str(raw)
        # 提取 JSON
        json_match = re.search(r'\{[\s\S]*\}', raw_text)
        if json_match:
            data = json.loads(json_match.group())
            return SubmissionMetaResponse(
                hook_quote=data.get("hook_quote", ""),
                short_intro=data.get("short_intro", ""),
                synopsis=data.get("synopsis", ""),
                tags=data.get("tags", []) or [],
                title_suggestion=data.get("title_suggestion", ""),
                opening_optimization=data.get("opening_optimization", ""),
            )

        return SubmissionMetaResponse()

    except Exception as e:
        logger.warning("LLM 生成投稿元信息失败，返回空值: %s", e)
        return SubmissionMetaResponse()
