"""引流钩子提取服务

按 40% 比例提取短篇前半部分作为知乎免费引流章节。
卡点必须在钩子位置（章节结尾的悬念/反转），不能是平滑剧情的中段。
"""
from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Optional, Tuple

from domain.novel.entities.chapter import Chapter

logger = logging.getLogger(__name__)

# 默认引流比例
DEFAULT_HOOK_RATIO = 0.4
# 比例浮动范围（寻找最佳卡点）
RATIO_TOLERANCE = 0.1  # 允许在 30%-50% 之间寻找最佳卡点
# 最小引流字数
MIN_HOOK_WORDS = 2000
# 最大引流字数
MAX_HOOK_WORDS = 6000


class HookExtractorService:
    """引流钩子提取器"""

    def extract_hook(
        self,
        chapters: List[Chapter],
        ratio: float = DEFAULT_HOOK_RATIO,
        novel_title: str = "",
    ) -> Dict[str, Any]:
        """提取引流钩子

        Args:
            chapters: 按 chapter.number 排序的章节列表
            ratio: 引流比例（默认 0.4）
            novel_title: 小说标题

        Returns:
            {
                "hook_content": str,         # 引流正文
                "hook_word_count": int,       # 引流字数
                "hook_end_chapter": int,      # 引流到第几节
                "total_word_count": int,      # 全文字数
                "actual_ratio": float,        # 实际比例
                "hook_type": str,             # 钩子类型（悬念/反转/情绪/冲突）
                "hook_snippet": str,          # 卡点最后 100 字（供前端预览）
                "paywall_chapter": int,       # 付费墙从第几节开始
            }
        """
        if not chapters:
            return self._empty_result()

        # 按 number 排序
        sorted_chapters = sorted(chapters, key=lambda c: c.number)
        total_words = sum(self._count_words(ch.content or "") for ch in sorted_chapters)

        if total_words == 0:
            return self._empty_result()

        # 计算目标引流字数
        target_hook_words = int(total_words * ratio)
        target_hook_words = max(MIN_HOOK_WORDS, min(MAX_HOOK_WORDS, target_hook_words))

        # 寻找最佳卡点：在 30%-50% 区间内，找最后一个有强钩子的章节结尾
        best_chapter_index = self._find_best_hook_point(
            sorted_chapters, target_hook_words, total_words
        )

        # 提取引流内容
        hook_chapters = sorted_chapters[: best_chapter_index + 1]
        hook_content = self._format_hook_content(hook_chapters, novel_title)
        hook_word_count = sum(self._count_words(ch.content or "") for ch in hook_chapters)

        # 识别钩子类型
        last_chapter = hook_chapters[-1]
        hook_type = self._identify_hook_type(last_chapter.content or "")
        hook_snippet = self._extract_snippet(last_chapter.content or "", 100)

        return {
            "hook_content": hook_content,
            "hook_word_count": hook_word_count,
            "hook_end_chapter": last_chapter.number,
            "total_word_count": total_words,
            "actual_ratio": round(hook_word_count / total_words, 3),
            "hook_type": hook_type,
            "hook_snippet": hook_snippet,
            "paywall_chapter": last_chapter.number + 1,
        }

    def _find_best_hook_point(
        self,
        chapters: List[Chapter],
        target_words: int,
        total_words: int,
    ) -> int:
        """在 30%-50% 区间内寻找最佳卡点章节

        优先级：
        1. 章节结尾是强钩子（悬念/反转）
        2. 累计字数最接近目标字数
        """
        min_ratio = DEFAULT_HOOK_RATIO - RATIO_TOLERANCE  # 0.3
        max_ratio = DEFAULT_HOOK_RATIO + RATIO_TOLERANCE  # 0.5

        min_words = int(total_words * min_ratio)
        max_words = int(total_words * max_ratio)

        best_index = 0
        best_score = -1.0
        cumulative_words = 0

        for idx, ch in enumerate(chapters):
            cumulative_words += self._count_words(ch.content or "")

            # 必须在 30%-50% 区间内
            if cumulative_words < min_words:
                # 即使不到 30%，也记录最后一个，防止章节太少
                best_index = idx
                continue
            if cumulative_words > max_words and best_index >= 0:
                # 超过 50%，停止搜索（已找到候选）
                break

            # 评估这个章节作为卡点的得分
            hook_score = self._score_chapter_as_hook(ch)
            # 字数接近度（越接近目标越高）
            word_proximity = 1.0 - abs(cumulative_words - target_words) / target_words
            # 综合得分：钩子强度权重 0.7，字数接近度权重 0.3
            total_score = hook_score * 0.7 + word_proximity * 0.3

            if total_score > best_score:
                best_score = total_score
                best_index = idx

        return best_index

    def _score_chapter_as_hook(self, chapter: Chapter) -> float:
        """评估章节作为卡点的得分（0-1）

        强钩子特征：
        - 结尾有问句
        - 结尾有省略号
        - 结尾有未完成的动作
        - 结尾出现"但""却""直到"等转折词
        - 结尾有具体悬念词（监控/短信/日记/照片/电话）
        """
        content = (chapter.content or "").strip()
        if not content:
            return 0.0

        # 取最后 200 字
        ending = content[-200:] if len(content) > 200 else content

        score = 0.0

        # 问句结尾 +0.3
        if re.search(r"[？?]\s*$", ending):
            score += 0.3

        # 省略号结尾 +0.2
        if re.search(r"[…。.]{2,}\s*$", ending):
            score += 0.2

        # 转折词 +0.2
        if re.search(r"(但是|可是|然而|却|直到|直到那时|直到第二天|原来)", ending):
            score += 0.2

        # 悬念关键词 +0.2
        suspense_words = ["监控", "短信", "日记", "照片", "电话", "录音", "门铃", "敲门", "黑屏", "消失", "不见", "错位", "挪动", "异常"]
        for word in suspense_words:
            if word in ending:
                score += 0.2
                break

        # 未完成动作 +0.1
        if re.search(r"(正要|刚要|还没|来不及|正准备)", ending):
            score += 0.1

        return min(score, 1.0)

    def _identify_hook_type(self, content: str) -> str:
        """识别钩子类型"""
        if not content:
            return "未知"

        ending = content[-200:] if len(content) > 200 else content

        if re.search(r"[？?]\s*$", ending):
            return "悬念钩"
        if re.search(r"(原来|其实|真相|没想到|不料)", ending):
            return "反转钩"
        if re.search(r"(但是|可是|然而|却|直到)", ending):
            return "冲突钩"
        return "情绪钩"

    def _format_hook_content(self, chapters: List[Chapter], title: str) -> str:
        """格式化引流内容（知乎盐选格式）"""
        parts = []
        if title:
            parts.append(title)
            parts.append("")
            parts.append("")

        for ch in chapters:
            # 章节标注
            parts.append(f"【{ch.number}】{ch.title or ''}")
            parts.append("")
            # 正文
            content = ch.content or ""
            # 引号转破折号
            content = self._quotes_to_dash(content)
            # 段落顶格
            parts.append(content.strip())
            parts.append("")
            parts.append("———")
            parts.append("")

        # 引流结尾提示
        parts.append("——后续内容已锁定，开通会员继续阅读——")

        return "\n".join(parts)

    def _quotes_to_dash(self, text: str) -> str:
        """引号转破折号"""
        # 中文引号
        text = re.sub(r'"([^"]+)"', r'——\1', text)
        text = re.sub(r'"([^"]+)"', r'——\1', text)
        text = re.sub(r'「([^」]+)」', r'——\1', text)
        return text

    def _extract_snippet(self, content: str, length: int = 100) -> str:
        """提取最后 N 字作为预览"""
        if not content:
            return ""
        content = content.strip()
        if len(content) <= length:
            return content
        return content[-length:]

    def _count_words(self, text: str) -> int:
        """统计字数（中文按字，英文按词）"""
        if not text:
            return 0
        # 简单统计：非空白字符数
        return len(re.sub(r"\s+", "", text))

    def _empty_result(self) -> Dict[str, Any]:
        return {
            "hook_content": "",
            "hook_word_count": 0,
            "hook_end_chapter": 0,
            "total_word_count": 0,
            "actual_ratio": 0.0,
            "hook_type": "未知",
            "hook_snippet": "",
            "paywall_chapter": 1,
        }
