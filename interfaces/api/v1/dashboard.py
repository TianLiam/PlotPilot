"""Dashboard API - 首页数据接口"""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from interfaces.api.dependencies import (
    get_novel_repository,
    get_chapter_repository,
    get_foreshadowing_repository,
)
from domain.novel.value_objects.novel_id import NovelId

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/dashboard", tags=["dashboard"])


class ReminderItem(BaseModel):
    type: str
    text: str
    action: str


class ActivityItem(BaseModel):
    time: str
    text: str
    type: str


class DashboardDataResponse(BaseModel):
    reminders: List[ReminderItem]
    activities: List[ActivityItem]


def _get_reminders(novel_id: Optional[str]) -> List[ReminderItem]:
    if not novel_id:
        return []

    reminders = []

    try:
        foreshadow_repo = get_foreshadowing_repository()
        chapter_repo = get_chapter_repository()

        registry = foreshadow_repo.get_by_novel_id(NovelId(novel_id))
        if registry:
            pending_entries = [e for e in registry.subtext_entries if e.status == "pending"]
            if pending_entries:
                reminders.append(
                    ReminderItem(
                        type="warning",
                        text=f"有 {len(pending_entries)} 个伏笔尚未回收",
                        action="foreshadow",
                    )
                )

        chapters = chapter_repo.list_by_novel(NovelId(novel_id))
        if chapters:
            recent_chapters = sorted(chapters, key=lambda ch: ch.number, reverse=True)[:5]
            if len(recent_chapters) >= 2:
                reminders.append(
                    ReminderItem(
                        type="success",
                        text=f"已完成 {len(chapters)} 章，继续保持创作节奏",
                        action="workbench",
                    )
                )

    except Exception as e:
        logger.warning(f"Failed to get reminders: {e}")

    if not reminders:
        reminders.append(
            ReminderItem(
                type="info",
                text="暂无 AI 提醒",
                action="workbench",
            )
        )

    return reminders


def _get_activities(novel_id: Optional[str]) -> List[ActivityItem]:
    if not novel_id:
        return []

    activities = []

    try:
        chapter_repo = get_chapter_repository()
        chapters = chapter_repo.list_by_novel(NovelId(novel_id))
        sorted_chapters = sorted(chapters, key=lambda ch: (ch.created_at or datetime.min), reverse=True)

        for ch in sorted_chapters[:3]:
            time_str = "刚刚"
            if ch.created_at:
                now = datetime.now()
                diff = now - ch.created_at
                if diff.days > 0:
                    time_str = f"{diff.days} 天前"
                elif diff.seconds > 3600:
                    time_str = f"{diff.seconds // 3600} 小时前"
                elif diff.seconds > 60:
                    time_str = f"{diff.seconds // 60} 分钟前"

            activities.append(
                ActivityItem(
                    time=time_str,
                    text=f"完成了第 {ch.number} 章《{ch.title or ''}》",
                    type="write",
                )
            )

    except Exception as e:
        logger.warning(f"Failed to get activities: {e}")

    if not activities:
        activities.append(
            ActivityItem(
                time="刚刚",
                text="创建了新作品",
                type="create",
            )
        )

    return activities


@router.get("/data", response_model=DashboardDataResponse)
@router.get("/data/", response_model=DashboardDataResponse)
async def get_dashboard_data(
    novel_id: Optional[str] = None,
):
    """
    获取首页 Dashboard 数据

    返回 AI 提醒和最近活动列表
    """
    try:
        reminders = await asyncio.to_thread(_get_reminders, novel_id)
        activities = await asyncio.to_thread(_get_activities, novel_id)
        return DashboardDataResponse(
            reminders=reminders[:3],
            activities=activities[:3],
        )
    except Exception as e:
        logger.error(f"Failed to get dashboard data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch dashboard data")