"""导出服务：生成真实可打开的 DOCX / EPUB / PDF / Markdown。"""
from __future__ import annotations

import html
import io
import logging
import os
import re
import tempfile
from typing import List, Optional, Tuple

from domain.novel.repositories.novel_repository import NovelRepository
from domain.novel.repositories.chapter_repository import ChapterRepository
from domain.novel.entities.novel import Novel
from domain.novel.entities.chapter import Chapter
from domain.novel.value_objects.novel_id import NovelId
from domain.novel.value_objects.chapter_id import ChapterId
from infrastructure.export.font_environment import ExportFontEnvironmentSettings

logger = logging.getLogger(__name__)


def _safe_filename_stem(title: str, max_len: int = 80) -> str:
    t = (title or "novel").strip()
    t = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", t)
    t = t.replace(" ", "_").strip("._") or "novel"
    if len(t) > max_len:
        t = t[:max_len]
    return t


def _novel_id_str(novel: Novel) -> str:
    nid = novel.id
    return nid.value if hasattr(nid, "value") else str(nid)


def _chapter_display_title(ch: Chapter) -> str:
    if ch.title and str(ch.title).strip():
        return str(ch.title).strip()
    return f"第 {ch.number} 章"


def _content_to_html_paragraphs(text: str) -> str:
    raw = (text or "").replace("\r\n", "\n").replace("\r", "\n")
    parts: List[str] = []
    for block in raw.split("\n"):
        line = block.strip()
        if line:
            parts.append(f"<p>{html.escape(line)}</p>")
    if not parts:
        return "<p></p>"
    return "\n".join(parts)


class ExportService:
    """导出服务"""

    def __init__(
        self,
        novel_repository: NovelRepository,
        chapter_repository: ChapterRepository,
        *,
        font_settings: ExportFontEnvironmentSettings | None = None,
    ):
        self.novel_repository = novel_repository
        self.chapter_repository = chapter_repository
        self.font_settings = font_settings or ExportFontEnvironmentSettings.from_env()

    def export_novel(self, novel_id: str, format: str) -> Tuple[bytes, str, str]:
        try:
            logger.info("开始导出小说: %s, 格式: %s", novel_id, format)
            novel = self.novel_repository.get_by_id(NovelId(novel_id))
            if not novel:
                raise ValueError(f"小说不存在: {novel_id}")
            chapters = self.chapter_repository.list_by_novel(NovelId(novel_id))
            chapters.sort(key=lambda x: x.number)
            logger.info("导出: %s, 章节数 %s", novel.title, len(chapters))
            if format == "epub":
                result = self._export_to_epub(novel, chapters)
            elif format == "pdf":
                result = self._export_to_pdf(novel, chapters)
            elif format == "docx":
                result = self._export_to_docx(novel, chapters)
            elif format == "markdown":
                result = self._export_to_markdown(novel, chapters)
            elif format == "zhihu":
                result = self._export_to_zhihu(novel, chapters)
            elif format == "fanqie":
                result = self._export_to_fanqie(novel, chapters)
            else:
                raise ValueError(f"不支持的导出格式: {format}")
            logger.info("导出成功，%s 字节", len(result[0]))
            return result
        except ValueError:
            raise
        except Exception as e:
            logger.error("导出小说失败: %s", e, exc_info=True)
            raise

    def export_chapter(self, chapter_id: str, format: str) -> Tuple[bytes, str, str]:
        try:
            logger.info("开始导出章节: %s, 格式: %s", chapter_id, format)
            chapter = self.chapter_repository.get_by_id(ChapterId(chapter_id))
            if not chapter:
                raise ValueError(f"章节不存在: {chapter_id}")
            novel_id = chapter.novel_id.value if hasattr(chapter.novel_id, "value") else chapter.novel_id
            novel = self.novel_repository.get_by_id(NovelId(novel_id))
            if not novel:
                raise ValueError(f"小说不存在: {novel_id}")
            if format == "epub":
                result = self._export_to_epub(novel, [chapter])
            elif format == "pdf":
                result = self._export_to_pdf(novel, [chapter])
            elif format == "docx":
                result = self._export_to_docx(novel, [chapter])
            elif format == "markdown":
                result = self._export_to_markdown(novel, [chapter])
            elif format == "zhihu":
                result = self._export_to_zhihu(novel, [chapter])
            elif format == "fanqie":
                result = self._export_to_fanqie(novel, [chapter])
            else:
                raise ValueError(f"不支持的导出格式: {format}")
            data, mime, _ = result
            ext = {"epub": "epub", "pdf": "pdf", "docx": "docx", "markdown": "md", "zhihu": "txt", "fanqie": "txt"}[format]
            chapter_stem = _safe_filename_stem(
                f"{novel.title or 'novel'}-第{chapter.number}章"
            )
            logger.info("导出成功，%s 字节", len(data))
            return data, mime, f"{chapter_stem}.{ext}"
        except ValueError:
            raise
        except Exception as e:
            logger.error("导出章节失败: %s", e, exc_info=True)
            raise

    def _export_to_epub(self, novel: Novel, chapters: list[Chapter]) -> Tuple[bytes, str, str]:
        from ebooklib import epub

        book = epub.EpubBook()
        uid = _novel_id_str(novel)
        book.set_identifier(f"plotpilot:{uid}")
        book.set_title(novel.title or "未命名")
        book.set_language("zh")
        book.add_author(novel.author or "未知作者")

        intro = epub.EpubHtml(
            title="简介",
            file_name="intro.xhtml",
            lang="zh",
        )
        premise = html.escape((novel.premise or "").strip() or "（无简介）")
        intro.content = f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" lang="zh">
<head><title>简介</title><meta charset="utf-8"/></head>
<body>
<h1>{html.escape(novel.title or "未命名")}</h1>
<p>作者：{html.escape(novel.author or "—")}</p>
<p>{premise}</p>
</body>
</html>"""
        book.add_item(intro)

        spine_items: List[epub.EpubHtml] = [intro]
        for i, ch in enumerate(chapters):
            fname = f"chap_{i + 1:03d}.xhtml"
            title_txt = _chapter_display_title(ch)
            title_esc = html.escape(title_txt)
            body = _content_to_html_paragraphs(ch.content or "")
            item = epub.EpubHtml(title=title_txt, file_name=fname, lang="zh")
            item.content = f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="zh">
<head><title>{title_esc}</title><meta charset="utf-8"/></head>
<body>
<h1>{title_esc}</h1>
{body}
</body>
</html>"""
            book.add_item(item)
            spine_items.append(item)

        book.toc = tuple([intro] + spine_items[1:])
        book.add_item(epub.EpubNcx())
        # 不使用空 EpubNav（ebooklib 生成 nav 时会解析正文，空文档会触发 lxml Document is empty）
        book.spine = spine_items

        tmp_path: Optional[str] = None
        try:
            fd, tmp_path = tempfile.mkstemp(suffix=".epub")
            os.close(fd)
            epub.write_epub(tmp_path, book, {})
            with open(tmp_path, "rb") as f:
                data = f.read()
        finally:
            if tmp_path and os.path.isfile(tmp_path):
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass

        stem = _safe_filename_stem(novel.title)
        return data, "application/epub+zip", f"{stem}.epub"

    def _try_register_cjk_font(self, pdf) -> bool:
        for path in self.font_settings.cjk_font_paths():
            if not path.is_file():
                continue
            try:
                pdf.add_font("PlotExportCJK", "", str(path), uni=True)
                return True
            except Exception as e:
                logger.debug("PDF 跳过字体 %s: %s", path, e)
        return False

    def _export_to_pdf(self, novel: Novel, chapters: list[Chapter]) -> Tuple[bytes, str, str]:
        from fpdf import FPDF

        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=14)
        font = "Helvetica"
        if self._try_register_cjk_font(pdf):
            font = "PlotExportCJK"

        def add_text(size: float, text: str, line_h: float) -> None:
            pdf.set_font(font, size=size)
            body = (text or "").strip() or " "
            try:
                pdf.multi_cell(0, line_h, body, new_x="LMARGIN", new_y="NEXT")
            except Exception as e:
                logger.warning("PDF multi_cell 回退: %s", e)
                pdf.set_font("Helvetica", size=size)
                safe = (text or "").encode("ascii", errors="replace").decode("ascii")
                pdf.multi_cell(0, line_h, safe or " ", new_x="LMARGIN", new_y="NEXT")

        pdf.add_page()
        add_text(16, novel.title or "未命名", 9)
        pdf.ln(2)
        add_text(
            11,
            f"作者：{novel.author or '—'}\n简介：{(novel.premise or '').strip() or '—'}",
            6,
        )
        pdf.ln(4)

        for ch in chapters:
            add_text(14, _chapter_display_title(ch), 8)
            pdf.ln(1)
            add_text(11, (ch.content or "").strip() or "（无正文）", 6)
            pdf.ln(6)

        out = pdf.output()
        if isinstance(out, str):
            data = out.encode("latin-1")
        elif isinstance(out, bytearray):
            data = bytes(out)
        else:
            data = out
        stem = _safe_filename_stem(novel.title)
        return data, "application/pdf", f"{stem}.pdf"

    def _export_to_docx(self, novel: Novel, chapters: list[Chapter]) -> Tuple[bytes, str, str]:
        from docx import Document

        doc = Document()
        doc.add_heading(novel.title or "未命名", level=0)
        doc.add_paragraph(f"作者：{novel.author or '—'}")
        p_pre = doc.add_paragraph()
        p_pre.add_run("简介：").bold = True
        p_pre.add_run((novel.premise or "").strip() or "（无）")

        for ch in chapters:
            doc.add_heading(_chapter_display_title(ch), level=1)
            content = ch.content or ""
            if not content.strip():
                doc.add_paragraph("（无正文）")
                continue
            for line in content.splitlines():
                doc.add_paragraph(line)

        buf = io.BytesIO()
        doc.save(buf)
        stem = _safe_filename_stem(novel.title)
        return (
            buf.getvalue(),
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            f"{stem}.docx",
        )

    def _export_to_markdown(self, novel: Novel, chapters: list[Chapter]) -> Tuple[bytes, str, str]:
        lines: List[str] = [
            f"# {novel.title or '未命名'}",
            "",
            f"**作者**: {novel.author or '—'}",
            "",
            "## 简介",
            "",
            (novel.premise or "").strip() or "（无）",
            "",
        ]
        for ch in chapters:
            lines.append(f"## {_chapter_display_title(ch)}")
            lines.append("")
            lines.append((ch.content or "").strip() or "（无正文）")
            lines.append("")
        text = "\n".join(lines)
        stem = _safe_filename_stem(novel.title)
        return text.encode("utf-8"), "text/markdown; charset=utf-8", f"{stem}.md"

    @staticmethod
    def _strip_markdown_marks(text: str) -> str:
        """移除常见的 markdown 标记：粗体/斜体/标题/列表/链接等。"""
        out = text or ""
        # 图片和链接，保留链接文本
        out = re.sub(r"!\[([^\]]*)\]\([^)]*\)", r"\1", out)
        out = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", out)
        # 行内代码
        out = re.sub(r"`([^`]+)`", r"\1", out)
        # 粗体+斜体
        out = re.sub(r"\*\*\*([^*]+)\*\*\*", r"\1", out)
        # 粗体
        out = re.sub(r"\*\*([^*]+)\*\*", r"\1", out)
        out = re.sub(r"__([^_]+)__", r"\1", out)
        # 斜体
        out = re.sub(r"\*([^*]+)\*", r"\1", out)
        out = re.sub(r"_([^_]+)_", r"\1", out)
        # 删除线
        out = re.sub(r"~~([^~]+)~~", r"\1", out)
        # 行首的标题井号
        out = re.sub(r"(?m)^\s{0,3}#{1,6}\s+", "", out)
        # 行首的列表标记（- 、* 、+ 、数字. ）
        out = re.sub(r"(?m)^\s*[-*+]\s+", "", out)
        out = re.sub(r"(?m)^\s*\d+\.\s+", "", out)
        # 行首的引用 >
        out = re.sub(r"(?m)^\s*>\s?", "", out)
        # 行首的水平分隔线（--- / *** / ___）
        out = re.sub(r"(?m)^\s*([-*_])\1{2,}\s*$", "", out)
        return out

    @staticmethod
    def _quotes_to_dash(text: str) -> str:
        """把引号包裹的对话转成破折号开头：双引号/中文引号/方括号引号 → ——xxx。"""
        out = text or ""
        # 中文弯引号 “…”
        out = re.sub(r"“([^”]*)”", r"——\1", out)
        # 直双引号 "…"
        out = re.sub(r'"([^"]*)"', r"——\1", out)
        # 中文直角引号「…」
        out = re.sub(r"「([^」]*)」", r"——\1", out)
        # 单引号配对（避免误伤撇号，要求成对出现且非空）
        out = re.sub(r"'([^']+)'", r"——\1", out)
        # 『…』
        out = re.sub(r"‘([^’]*)’", r"——\1", out)
        return out

    def _export_to_zhihu(self, novel: Novel, chapters: list[Chapter]) -> Tuple[bytes, str, str]:
        """导出为知乎盐选格式（纯文本，符合盐选排版规范）"""
        sep = "———"  # 章节分隔线，3 个以上破折号
        blocks: List[str] = []
        # 标题行：纯文本，不加 markdown 标记
        blocks.append(str(novel.title or "未命名").strip())
        # 标题后空两行
        blocks.append("")
        blocks.append("")

        chapter_blocks: List[str] = []
        for ch in chapters:
            title = _chapter_display_title(ch)
            # 章节标题用 【N】标题 格式
            chapter_lines: List[str] = [f"【{ch.number}】{title}", ""]
            content = ch.content or ""
            # 1) 先把对话引号转成破折号
            content = self._quotes_to_dash(content)
            # 2) 移除 markdown 标记
            content = self._strip_markdown_marks(content)
            # 3) 段落顶格、段落之间空一行
            raw = content.replace("\r\n", "\n").replace("\r", "\n")
            paragraphs = [line.strip() for line in raw.split("\n")]
            paragraphs = [p for p in paragraphs if p]
            if not paragraphs:
                paragraphs = ["（无正文）"]
            chapter_lines.extend(paragraphs)
            chapter_blocks.append("\n".join(chapter_lines))

        # 章节之间用分隔线分隔
        body = f"\n\n{sep}\n\n".join(chapter_blocks)
        full = "\n".join(blocks) + body + "\n"
        stem = _safe_filename_stem(novel.title)
        return full.encode("utf-8"), "text/plain; charset=utf-8", f"{stem}.txt"

    def _export_to_fanqie(self, novel: Novel, chapters: list[Chapter]) -> Tuple[bytes, str, str]:
        """导出为番茄短故事格式"""
        blocks: List[str] = []
        # 标题行（保留 markdown 粗体也允许，这里用纯文本标题）
        blocks.append(str(novel.title or "未命名").strip())
        blocks.append("")

        chapter_blocks: List[str] = []
        for ch in chapters:
            title = _chapter_display_title(ch)
            chapter_lines: List[str] = [f"第{ch.number}章 {title}", ""]
            content = ch.content or ""
            # 番茄格式保留对话原样，支持粗体；只做段落顶格与空行规整
            raw = content.replace("\r\n", "\n").replace("\r", "\n")
            paragraphs = [line.strip() for line in raw.split("\n")]
            paragraphs = [p for p in paragraphs if p]
            if not paragraphs:
                paragraphs = ["（无正文）"]
            chapter_lines.extend(paragraphs)
            chapter_blocks.append("\n".join(chapter_lines))

        # 章节之间空两行分隔
        body = "\n\n\n".join(chapter_blocks)
        full = "\n".join(blocks) + body + "\n"
        stem = _safe_filename_stem(novel.title)
        return full.encode("utf-8"), "text/plain; charset=utf-8", f"{stem}.txt"
