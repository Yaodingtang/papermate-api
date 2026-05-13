"""Semantic Scholar API 服务 - 从 Semantic Scholar 获取论文"""

import httpx
from typing import Optional, List, Dict, Any
from datetime import datetime


class SemanticScholarService:
    """Semantic Scholar API 服务"""

    BASE_URL = "https://api.semanticscholar.org/graph/v1"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.headers = {"User-Agent": "PaperMate/1.0"}
        if api_key:
            self.headers["x-api-key"] = api_key

    async def search(
        self,
        query: str,
        limit: int = 10,
        year: Optional[str] = None,
        venue: Optional[str] = None,
        fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """搜索论文

        Args:
            query: 搜索关键词
            limit: 返回数量
            year: 年份范围 (如 "2020-2024", "2023-")
            venue: 发表 venue
            fields: 返回字段
        """
        if fields is None:
            fields = [
                "paperId", "title", "abstract", "year", "authors",
                "venue", "citationCount", "referenceCount", "url",
                "publicationDate", "journal", "externalIds"
            ]

        params = {
            "query": query,
            "limit": limit,
            "fields": ",".join(fields),
        }

        if year:
            params["year"] = year
        if venue:
            params["venue"] = venue

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.BASE_URL}/paper/search",
                    params=params,
                    headers=self.headers,
                    timeout=30.0
                )
                if response.status_code == 200:
                    data = response.json()
                    items = [self._parse_paper(p) for p in data.get("data", [])]
                    return {
                        "items": items,
                        "total": data.get("total", len(items)),
                    }
                return {"items": [], "total": 0}
            except Exception as e:
                print(f"Semantic Scholar API 错误: {e}")
                return {"items": [], "total": 0}

    async def get_paper(self, paper_id: str) -> Optional[Dict[str, Any]]:
        """获取单篇论文详情"""
        fields = [
            "paperId", "title", "abstract", "year", "authors",
            "venue", "citationCount", "referenceCount", "url",
            "publicationDate", "journal", "externalIds",
            "citations.citationCount", "references.referenceCount"
        ]

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.BASE_URL}/paper/{paper_id}",
                    params={"fields": ",".join(fields)},
                    headers=self.headers,
                    timeout=30.0
                )
                if response.status_code == 200:
                    data = response.json()
                    return self._parse_paper(data)
                return None
            except Exception as e:
                print(f"获取论文详情错误: {e}")
                return None

    async def get_trending(
        self,
        query: str = "machine learning",
        limit: int = 10,
        min_citations: int = 50
    ) -> List[Dict[str, Any]]:
        """获取热门论文（高引用）"""
        result = await self.search(
            query=query,
            limit=limit * 2,  # 获取更多，然后过滤
            year="2023-",  # 最近两年
        )

        items = result.get("items", [])
        # 按引用数排序
        items.sort(key=lambda x: x.get("citation_count", 0), reverse=True)

        # 过滤低引用
        filtered = [p for p in items if p.get("citation_count", 0) >= min_citations]
        return filtered[:limit]

    async def get_recommendations(
        self,
        paper_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """获取推荐论文（基于某篇论文）"""
        fields = [
            "paperId", "title", "abstract", "year", "authors",
            "venue", "citationCount", "url"
        ]

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.BASE_URL}/recommendations/v1/papers/forpaper/{paper_id}",
                    params={
                        "limit": limit,
                        "fields": ",".join(fields),
                    },
                    headers=self.headers,
                    timeout=30.0
                )
                if response.status_code == 200:
                    data = response.json()
                    return [self._parse_paper(p) for p in data.get("recommendedPapers", [])]
                return []
            except Exception as e:
                print(f"获取推荐论文错误: {e}")
                return []

    async def get_author_papers(
        self,
        author_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """获取作者的论文"""
        fields = [
            "paperId", "title", "abstract", "year", "venue",
            "citationCount", "url", "publicationDate"
        ]

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.BASE_URL}/author/{author_id}/papers",
                    params={
                        "limit": limit,
                        "fields": ",".join(fields),
                    },
                    headers=self.headers,
                    timeout=30.0
                )
                if response.status_code == 200:
                    data = response.json()
                    return [self._parse_paper(p) for p in data.get("data", [])]
                return []
            except Exception as e:
                print(f"获取作者论文错误: {e}")
                return []

    def _parse_paper(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """解析论文数据"""
        # 解析作者
        authors = []
        for author in data.get("authors", []):
            authors.append({
                "name": author.get("name", ""),
                "id": author.get("authorId", ""),
            })

        # 解析外部 ID
        external_ids = data.get("externalIds", {})
        doi = external_ids.get("DOI", "")
        arxiv_id = external_ids.get("ArXiv", "")

        # 解析年份
        year = data.get("year")

        return {
            "paper_id": data.get("paperId", ""),
            "title": data.get("title", ""),
            "abstract": data.get("abstract", ""),
            "year": year,
            "authors": authors,
            "venue": data.get("venue", "") or data.get("journal", ""),
            "citation_count": data.get("citationCount", 0),
            "reference_count": data.get("referenceCount", 0),
            "url": data.get("url", ""),
            "publication_date": data.get("publicationDate", ""),
            "doi": doi,
            "arxiv_id": arxiv_id,
            "type": "paper",
        }


# 便捷函数
async def search_semantic_scholar(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """搜索 Semantic Scholar 论文"""
    service = SemanticScholarService()
    result = await service.search(query, limit=limit)
    return result.get("items", [])


async def get_trending_papers(limit: int = 10) -> List[Dict[str, Any]]:
    """获取热门论文"""
    service = SemanticScholarService()
    return await service.get_trending(limit=limit)


async def get_paper_recommendations(paper_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """获取论文推荐"""
    service = SemanticScholarService()
    return await service.get_recommendations(paper_id, limit=limit)
