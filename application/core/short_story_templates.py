"""短篇题材模板加载服务"""
from __future__ import annotations
import os
import yaml
from typing import Any, Dict, List, Optional
from pathlib import Path

_TEMPLATE_CACHE: Optional[List[Dict[str, Any]]] = None
_TEMPLATE_PATH = Path(__file__).parent.parent.parent / "shared" / "taxonomy" / "yanxuan_templates.yaml"


def load_yanxuan_templates() -> List[Dict[str, Any]]:
    """加载知乎盐选题材模板"""
    global _TEMPLATE_CACHE
    if _TEMPLATE_CACHE is not None:
        return _TEMPLATE_CACHE
    if not _TEMPLATE_PATH.exists():
        return []
    with open(_TEMPLATE_PATH, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    _TEMPLATE_CACHE = data.get("templates", []) if data else []
    return _TEMPLATE_CACHE


def get_template_by_id(template_id: str) -> Optional[Dict[str, Any]]:
    """按 ID 获取模板"""
    for t in load_yanxuan_templates():
        if t.get("id") == template_id:
            return t
    return None


def build_premise_from_template(template_id: str, user_idea: str = "") -> str:
    """根据模板生成 premise 文本"""
    tpl = get_template_by_id(template_id)
    if not tpl:
        return user_idea
    parts = [f"【题材：{tpl['name']}】"]
    if user_idea:
        parts.append(user_idea)
    else:
        parts.append(f"核心爽点：{tpl['core_appeal']}")
        parts.append(f"经典桥段：{', '.join(tpl['classic_tropes'][:2])}")
        parts.append(f"反转设计：{tpl['twist_design']}")
    parts.append(f"目标字数：{tpl['recommended_words']}字，{tpl['recommended_sections']}节")
    return "\n".join(parts)
