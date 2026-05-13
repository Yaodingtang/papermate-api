"""arXiv API 服务 - 从 arXiv 获取论文"""

import httpx
from typing import Optional, List, Dict, Any
from datetime import datetime
import xml.etree.ElementTree as ET
import re


class ArxivService:
    """arXiv API 服务"""

    BASE_URL = "http://export.arxiv.org/api/query"

    def __init__(self):
        self.headers = {"User-Agent": "PaperMate/1.0"}

    async def search(
        self,
        query: str,
        limit: int = 10,
        category: Optional[str] = None,
        sort_by: str = "relevance"
    ) -> Dict[str, Any]:
        """搜索 arXiv 论文

        Args:
            query: 搜索关键词
            limit: 返回数量
            category: arXiv 分类 (如 cs.AI, cs.LG, cs.CL)
            sort_by: 排序方式 (relevance, lastUpdatedDate, submittedDate)
        """
        # 构建搜索查询
        search_query = f"all:{query}"
        if category:
            search_query = f"cat:{category} AND all:{query}"

        # 排序参数
        sort_map = {
            "relevance": ("relevance", "descending"),
            "recent": ("submittedDate", "descending"),
            "updated": ("lastUpdatedDate", "descending"),
        }
        sort_key, sort_order = sort_map.get(sort_by, ("relevance", "descending"))

        params = {
            "search_query": search_query,
            "start": 0,
            "max_results": limit,
            "sortBy": sort_key,
            "sortOrder": sort_order,
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    self.BASE_URL,
                    params=params,
                    headers=self.headers,
                    timeout=30.0
                )
                if response.status_code == 200:
                    return self._parse_response(response.text)
                return {"items": [], "total": 0}
            except Exception as e:
                print(f"arXiv API 错误: {e}")
                return {"items": [], "total": 0}

    async def get_recent(
        self,
        category: str = "cs.AI",
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """获取某分类的最新论文"""
        params = {
            "search_query": f"cat:{category}",
            "start": 0,
            "max_results": limit,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    self.BASE_URL,
                    params=params,
                    headers=self.headers,
                    timeout=30.0
                )
                if response.status_code == 200:
                    result = self._parse_response(response.text)
                    return result.get("items", [])
                return []
            except Exception as e:
                print(f"arXiv API 错误: {e}")
                return []

    async def get_popular(
        self,
        categories: List[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """获取热门论文（基于最近更新）"""
        if categories is None:
            categories = ["cs.AI", "cs.LG", "cs.CL", "cs.CV"]

        all_papers = []
        for cat in categories[:3]:  # 限制并发查询的分类数
            papers = await self.get_recent(category=cat, limit=limit // 2 + 2)
            all_papers.extend(papers)

        # 按日期排序并去重
        seen = set()
        unique_papers = []
        for paper in all_papers:
            if paper.get("arxiv_id") not in seen:
                seen.add(paper.get("arxiv_id"))
                unique_papers.append(paper)

        # 按更新时间排序
        unique_papers.sort(key=lambda x: x.get("updated", ""), reverse=True)
        return unique_papers[:limit]

    def _parse_response(self, xml_text: str) -> Dict[str, Any]:
        """解析 arXiv API 的 XML 响应"""
        try:
            root = ET.fromstring(xml_text)

            # 定义命名空间
            ns = {
                "atom": "http://www.w3.org/2005/Atom",
                "arxiv": "http://arxiv.org/schemas/atom",
            }

            items = []
            for entry in root.findall("atom:entry", ns):
                paper = self._parse_entry(entry, ns)
                if paper:
                    items.append(paper)

            # 获取总数
            total = root.find("atom:totalResults", ns)
            total_count = int(total.text) if total is not None else len(items)

            return {"items": items, "total": total_count}
        except Exception as e:
            print(f"解析 arXiv 响应错误: {e}")
            return {"items": [], "total": 0}

    def _parse_entry(self, entry, ns: dict) -> Optional[Dict[str, Any]]:
        """解析单个论文条目"""
        try:
            # 标题
            title_elem = entry.find("atom:title", ns)
            title = title_elem.text.strip() if title_elem is not None else ""

            # 摘要
            summary_elem = entry.find("atom:summary", ns)
            abstract = summary_elem.text.strip() if summary_elem is not None else ""

            # 作者列表
            authors = []
            for author in entry.findall("atom:author", ns):
                name_elem = author.find("atom:name", ns)
                if name_elem is not None:
                    authors.append({"name": name_elem.text})

            # arXiv ID
            id_elem = entry.find("atom:id", ns)
            arxiv_url = id_elem.text if id_elem is not None else ""
            arxiv_id = arxiv_url.split("/abs/")[-1] if "/abs/" in arxiv_url else ""

            # PDF 链接
            pdf_url = ""
            for link in entry.findall("atom:link", ns):
                if link.get("type") == "application/pdf":
                    pdf_url = link.get("href", "")
                    break

            # 发布日期
            published_elem = entry.find("atom:published", ns)
            published = published_elem.text if published_elem is not None else ""

            # 更新日期
            updated_elem = entry.find("atom:updated", ns)
            updated = updated_elem.text if updated_elem is not None else ""

            # 分类
            categories = []
            for cat in entry.findall("atom:category", ns):
                term = cat.get("term", "")
                if term:
                    categories.append(term)

            # 主分类
            primary_category = entry.find("arxiv:primary_category", ns)
            primary_cat = primary_category.get("term", "") if primary_category is not None else ""

            # 解析年份
            year = None
            if published:
                year_match = re.match(r"(\d{4})", published)
                if year_match:
                    year = int(year_match.group(1))

            return {
                "arxiv_id": arxiv_id,
                "title": title,
                "authors": authors,
                "abstract": abstract,
                "year": year,
                "published": published,
                "updated": updated,
                "categories": categories,
                "primary_category": primary_cat,
                "pdf_url": pdf_url,
                "arxiv_url": arxiv_url,
                "doi": f"arXiv:{arxiv_id}",
                "venue": "arXiv",
                "type": "preprint",
            }
        except Exception as e:
            print(f"解析论文条目错误: {e}")
            return None


# 便捷函数
async def search_arxiv(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """搜索 arXiv 论文"""
    service = ArxivService()
    result = await service.search(query, limit=limit)
    return result.get("items", [])


async def get_arxiv_recent(category: str = "cs.AI", limit: int = 10) -> List[Dict[str, Any]]:
    """获取 arXiv 最新论文"""
    service = ArxivService()
    return await service.get_recent(category=category, limit=limit)


async def get_arxiv_popular(limit: int = 10) -> List[Dict[str, Any]]:
    """获取 arXiv 热门论文"""
    service = ArxivService()
    return await service.get_popular(limit=limit)
