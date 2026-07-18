"""小说内容爬虫 - 爬取免费章节"""
import logging
import re
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

from lxml import html as lxml_html

from infrastructure.crawler.base_crawler import BaseCrawler

logger = logging.getLogger(__name__)


class NovelContentCrawler(BaseCrawler):
    """小说内容爬虫 - 爬取免费章节"""
    
    # 番茄小说API
    FANQIE_CHAPTER_LIST_API = "https://fanqienovel.com/api/novel/v1/chapter/list"
    FANQIE_CHAPTER_CONTENT_API = "https://fanqienovel.com/api/novel/v1/chapter/content"
    
    QIDIAN_BASE_URL = "https://m.qidian.com"
    QIDIAN_MOBILE_USER_AGENT = (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
    )
    
    async def crawl_fanqie_free_chapters(
        self, 
        book_id: str, 
        max_chapters: int = 30
    ) -> Dict[str, Any]:
        """爬取番茄小说免费章节
        
        Args:
            book_id: 小说ID
            max_chapters: 最大章节数（默认30章，通常是免费范围）
        
        Returns:
            {
                "book_id": str,
                "book_name": str,
                "author": str,
                "category": str,
                "total_chapters": int,
                "crawled_chapters": int,
                "chapters": [
                    {
                        "chapter_id": str,
                        "chapter_number": int,
                        "title": str,
                        "content": str,
                        "word_count": int,
                    }
                ],
                "collected_at": str,
            }
        """
        result = {
            "book_id": book_id,
            "book_name": "",
            "author": "",
            "category": "",
            "total_chapters": 0,
            "crawled_chapters": 0,
            "chapters": [],
            "collected_at": datetime.utcnow().isoformat(),
        }
        
        try:
            # 1. 获取章节列表
            headers = self._get_default_headers(referer=f"https://fanqienovel.com/book/{book_id}")
            
            chapter_list = []
            page = 1
            page_size = 100
            
            while len(chapter_list) < max_chapters:
                params = {
                    "bookId": book_id,
                    "page": page,
                    "pageSize": page_size,
                    "expand": "bookId",
                }
                
                response = await self.safe_request(
                    "get", 
                    self.FANQIE_CHAPTER_LIST_API,
                    params=params,
                    headers=headers
                )
                
                if response is None:
                    break
                
                data = response.json()
                
                if data.get("code") != 0 or not data.get("data"):
                    logger.warning(f"Fanqie chapter list API error: {data}")
                    break
                
                chapter_items = data["data"].get("chapterList", [])
                
                if not chapter_items:
                    break
                
                for item in chapter_items:
                    # 只爬取免费章节（isFree = True 或 price = 0）
                    if item.get("isFree", False) or item.get("price", 0) == 0:
                        chapter_list.append({
                            "chapter_id": str(item.get("chapterId")),
                            "chapter_number": item.get("index", len(chapter_list) + 1),
                            "title": self.clean_text(item.get("title")),
                            "word_count": item.get("wordCount", 0),
                            "is_free": True,
                        })
                
                # 获取书籍基本信息
                if page == 1:
                    book_info = data["data"].get("bookInfo", {})
                    result["book_name"] = self.clean_text(book_info.get("bookName", ""))
                    result["author"] = self.clean_text(book_info.get("authorName", ""))
                    result["category"] = self.clean_text(book_info.get("category", ""))
                    result["total_chapters"] = book_info.get("totalChapterNum", 0)
                
                page += 1
                
                # 避免请求过于频繁
                await self._delay()
                
                # 如果返回的章节数少于页大小，说明已经到底了
                if len(chapter_items) < page_size:
                    break
            
            # 限制章节数量
            chapter_list = chapter_list[:max_chapters]
            
            # 2. 获取章节内容
            for chapter_info in chapter_list:
                try:
                    content_params = {
                        "chapterId": chapter_info["chapter_id"],
                    }
                    
                    content_response = await self.safe_request(
                        "get",
                        self.FANQIE_CHAPTER_CONTENT_API,
                        params=content_params,
                        headers=headers
                    )
                    
                    if content_response is None:
                        continue
                    
                    content_data = content_response.json()
                    
                    if content_data.get("code") != 0:
                        logger.warning(f"Failed to get chapter content: {content_data}")
                        continue
                    
                    content = content_data.get("data", {}).get("content", "")
                    
                    # 清理内容
                    content = self._clean_novel_content(content)
                    
                    if content:
                        chapter_info["content"] = content
                        chapter_info["word_count"] = len(content)
                        result["chapters"].append(chapter_info)
                        result["crawled_chapters"] += 1
                    
                    # 避免请求过于频繁
                    await self._delay()
                    
                except Exception as e:
                    logger.error(f"Failed to crawl chapter {chapter_info['chapter_id']}: {e}")
                    continue
            
            logger.info(f"Crawled {result['crawled_chapters']} chapters from Fanqie book {book_id}")
            
        except Exception as e:
            logger.error(f"Failed to crawl Fanqie novel {book_id}: {e}")
        
        return result
    
    def _clean_novel_content(self, content: str) -> str:
        """清理小说内容"""
        if not content:
            return ""
        
        # 移除HTML标签
        content = re.sub(r'<[^>]+>', '', content)
        
        # 移除特殊字符
        content = content.replace('\r', '').replace('\t', ' ')
        
        # 规范化换行
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # 移除多余的空格
        content = re.sub(r' {2,}', ' ', content)
        
        return content.strip()
    
    async def crawl_qidian_free_chapters(
        self,
        book_id: str,
        max_chapters: int = 20
    ) -> Dict[str, Any]:
        """从起点移动站目录和章节页抓取明确标记为免费的正文。"""
        result = {
            "book_id": book_id,
            "book_name": "",
            "author": "",
            "category": "",
            "total_chapters": 0,
            "crawled_chapters": 0,
            "chapters": [],
            "collected_at": datetime.utcnow().isoformat(),
            "platform": "qidian",
        }
        
        try:
            catalog_url = f"{self.QIDIAN_BASE_URL}/book/{book_id}/catalog/"
            headers = self._get_default_headers(referer=f"{self.QIDIAN_BASE_URL}/book/{book_id}.html")
            headers["User-Agent"] = self.QIDIAN_MOBILE_USER_AGENT
            response = await self.safe_request("get", catalog_url, headers=headers, max_retries=2)
            if response is None:
                return result

            document = lxml_html.fromstring(response.content.decode("utf-8", errors="replace"))
            page_title = self.clean_text(document.xpath("string(//title)"))
            result["book_name"] = re.split(r"最新章节|全部章节", page_title, maxsplit=1)[0].strip()
            result["author"] = self.clean_text(
                document.xpath("string(//meta[@property='og:novel:author']/@content)")
            )

            links = [
                node for node in document.xpath("//a[@href]")
                if "_chapterItem_" in (node.get("class") or "")
                and "/chapter/" in (node.get("href") or "")
            ]
            result["total_chapters"] = len(links)

            free_links = []
            content_started = False
            for node in links:
                raw_title = " ".join(node.text_content().split())
                if not content_started and re.match(r"^第一章(?:\s|[:：])", raw_title):
                    content_started = True
                if not content_started or "免费" not in raw_title:
                    continue
                free_links.append((node, re.sub(r"\s*免费\s*$", "", raw_title).strip()))
                if len(free_links) >= max_chapters:
                    break

            if not free_links:
                self.last_error = f"No readable free chapters found for Qidian book {book_id}"
                return result

            for chapter_number, (node, title) in enumerate(free_links, 1):
                chapter_url = node.get("href") or ""
                if chapter_url.startswith("//"):
                    chapter_url = f"https:{chapter_url}"
                chapter_response = await self.safe_request(
                    "get", chapter_url, headers=headers, max_retries=2
                )
                if chapter_response is None:
                    continue

                chapter_document = lxml_html.fromstring(
                    chapter_response.content.decode("utf-8", errors="replace")
                )
                main_nodes = chapter_document.xpath("//main")
                if not main_nodes:
                    continue
                main = main_nodes[0]
                paragraphs = [
                    " ".join(node.text_content().split())
                    for node in main.xpath(".//p")
                    if " ".join(node.text_content().split())
                ]
                content = "\n".join(paragraphs) if paragraphs else main.text_content()
                content = self._clean_novel_content(content)
                if not content:
                    continue

                chapter_id_match = re.search(r"/chapter/\d+/(\d+)/?", chapter_url)
                result["chapters"].append({
                    "chapter_id": chapter_id_match.group(1) if chapter_id_match else chapter_url,
                    "chapter_number": chapter_number,
                    "title": title,
                    "content": content,
                    "word_count": len(content),
                    "is_free": True,
                })
                result["crawled_chapters"] += 1
                await self._delay()

            logger.info(
                "Crawled %s verified free chapters from Qidian book %s",
                result["crawled_chapters"],
                book_id,
            )
        except Exception as e:
            self.last_error = f"{type(e).__name__}: {e}"
            logger.error(f"Failed to crawl Qidian novel {book_id}: {e}")

        return result
    
    async def crawl_novel_for_analysis(
        self,
        platform: str,
        book_id: str,
        max_chapters: int = 30
    ) -> Optional[Dict[str, Any]]:
        """爬取小说用于分析
        
        Args:
            platform: 平台（fanqie, qidian）
            book_id: 小说ID
            max_chapters: 最大章节数
        
        Returns:
            小说数据字典，包含章节内容
        """
        if platform == "fanqie":
            return await self.crawl_fanqie_free_chapters(book_id, max_chapters)
        elif platform == "qidian":
            return await self.crawl_qidian_free_chapters(book_id, max_chapters)
        else:
            logger.warning(f"Unknown platform: {platform}")
            return None
    
    async def get_novel_text_for_analysis(
        self,
        novel_data: Dict[str, Any],
        max_words: int = 50000
    ) -> str:
        """获取用于分析的文本（合并章节）
        
        Args:
            novel_data: 小说数据
            max_words: 最大字数（避免超出LLM上下文）
        
        Returns:
            合并后的文本
        """
        chapters = novel_data.get("chapters", [])
        
        combined_text = f"# {novel_data.get('book_name', '未知')}\n\n"
        combined_text += f"作者：{novel_data.get('author', '未知')}\n"
        combined_text += f"分类：{novel_data.get('category', '未知')}\n\n"
        combined_text += "---\n\n"
        
        total_words = 0
        
        for chapter in chapters:
            title = chapter.get("title", "")
            content = chapter.get("content", "")
            
            chapter_text = f"## 第{chapter.get('chapter_number', '?')}章 {title}\n\n{content}\n\n"
            
            # 检查字数限制
            if total_words + len(chapter_text) > max_words:
                break
            
            combined_text += chapter_text
            total_words += len(chapter_text)
        
        return combined_text
