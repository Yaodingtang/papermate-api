"""论文元数据服务 - 从 Crossref 等学术数据库获取元数据"""

import httpx
from typing import Optional, List, Dict, Any
from datetime import datetime
import re


class CrossrefService:
    """Crossref API 服务"""
    
    BASE_URL = "https://api.crossref.org"
    
    def __init__(self, email: Optional[str] = None):
        """初始化 Crossref 服务
        
        Args:
            email: 提供邮箱可以获得更高的 API 速率限制
        """
        self.email = email
        self.headers = {"User-Agent": f"PaperMate/1.0 (mailto:{email})" if email else "PaperMate/1.0"}
    
    async def get_work_by_doi(self, doi: str) -> Optional[Dict[str, Any]]:
        """通过 DOI 获取论文信息"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.BASE_URL}/works/{doi}",
                    headers=self.headers,
                    timeout=30.0
                )
                if response.status_code == 200:
                    data = response.json()
                    return self._parse_work(data.get("message", {}))
                return None
            except Exception as e:
                print(f"Crossref API 错误: {e}")
                return None
    
    async def search_works(
        self,
        query: str,
        limit: int = 10,
        offset: int = 0,
        filter_params: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """搜索论文"""
        params = {
            "query": query,
            "rows": limit,
            "offset": offset,
        }
        
        if filter_params:
            filter_str = ",".join(f"{k}:{v}" for k, v in filter_params.items())
            params["filter"] = filter_str
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.BASE_URL}/works",
                    params=params,
                    headers=self.headers,
                    timeout=30.0
                )
                if response.status_code == 200:
                    data = response.json()
                    items = data.get("message", {}).get("items", [])
                    total = data.get("message", {}).get("total-results", 0)
                    return {
                        "items": [self._parse_work(item) for item in items],
                        "total": total,
                        "offset": offset,
                        "limit": limit,
                    }
                return {"items": [], "total": 0}
            except Exception as e:
                print(f"Crossref 搜索错误: {e}")
                return {"items": [], "total": 0}
    
    def _parse_work(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """解析 Crossref 返回的工作数据"""
        # 解析作者
        authors = []
        for author in data.get("author", []):
            given = author.get("given", "")
            family = author.get("family", "")
            authors.append({
                "name": f"{given} {family}".strip(),
                "given": given,
                "family": family,
                "affiliation": author.get("affiliation", [{}])[0].get("name", "") if author.get("affiliation") else "",
                "orcid": author.get("ORCID", ""),
            })
        
        # 解析日期
        published = data.get("published-print") or data.get("published-online") or data.get("created")
        year = None
        if published:
            date_parts = published.get("date-parts", [[]])[0]
            if date_parts:
                year = date_parts[0]
        
        # 解析期刊信息
        container = data.get("container-title", [])
        journal = container[0] if container else ""
        
        # 解析 DOI
        doi = data.get("DOI", "")
        
        # 解析标题
        title_list = data.get("title", [])
        title = title_list[0] if title_list else ""
        
        # 解析摘要（Crossref 通常不提供摘要）
        abstract = data.get("abstract", "")
        
        # 解析引用数
        is_referenced_by_count = data.get("is-referenced-by-count", 0)
        references_count = data.get("references-count", 0)
        
        # 解析关键词
        subjects = data.get("subject", [])
        
        # 解析 URL
        url = data.get("URL", "")
        
        # 解析类型
        type_ = data.get("type", "")
        
        return {
            "doi": doi,
            "title": title,
            "authors": authors,
            "year": year,
            "journal": journal,
            "abstract": abstract,
            "keywords": subjects,
            "type": type_,
            "url": url,
            "citation_count": is_referenced_by_count,
            "reference_count": references_count,
            "publisher": data.get("publisher", ""),
            "issn": data.get("ISSN", [""])[0] if data.get("ISSN") else "",
            "volume": data.get("volume", ""),
            "issue": data.get("issue", ""),
            "page": data.get("page", ""),
        }
    
    async def get_citations(self, doi: str, limit: int = 20) -> List[Dict[str, Any]]:
        """获取引用该论文的文献列表"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.BASE_URL}/works/{doi}",
                    params={"select": "is-referenced-by"},
                    headers=self.headers,
                    timeout=30.0
                )
                if response.status_code == 200:
                    data = response.json()
                    # Crossref 不直接提供引用列表，需要额外查询
                    # 这里返回简化信息
                    message = data.get("message", {})
                    count = message.get("is-referenced-by-count", 0)
                    return {
                        "count": count,
                        "doi": doi,
                        "note": "使用 get_work_by_doi 获取详细信息",
                    }
                return []
            except Exception as e:
                print(f"获取引用列表错误: {e}")
                return []
    
    async def get_references(self, doi: str) -> List[Dict[str, Any]]:
        """获取该论文引用的文献列表"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.BASE_URL}/works/{doi}",
                    params={"select": "reference"},
                    headers=self.headers,
                    timeout=30.0
                )
                if response.status_code == 200:
                    data = response.json()
                    refs = data.get("message", {}).get("reference", [])
                    return [
                        {
                            "doi": ref.get("DOI", ""),
                            "title": ref.get("unstructured", "") or ref.get("article-title", ""),
                            "year": ref.get("year"),
                            "author": ref.get("author", ""),
                        }
                        for ref in refs
                    ]
                return []
            except Exception as e:
                print(f"获取参考文献列表错误: {e}")
                return []


class MetadataService:
    """论文元数据服务 - 整合多个数据源"""
    
    def __init__(self, crossref_email: Optional[str] = None):
        self.crossref = CrossrefService(email=crossref_email)
    
    async def enrich_from_doi(self, doi: str) -> Dict[str, Any]:
        """通过 DOI 丰富元数据"""
        crossref_data = await self.crossref.get_work_by_doi(doi)
        if crossref_data:
            return {
                "source": "crossref",
                "data": crossref_data,
            }
        return {"source": "none", "data": {}}
    
    async def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """搜索论文"""
        result = await self.crossref.search_works(query, limit=limit)
        return result.get("items", [])
    
    async def extract_doi_from_text(self, text: str) -> Optional[str]:
        """从文本中提取 DOI"""
        # DOI 正则模式
        doi_pattern = r'10\.\d{4,}/[^\s]+'
        match = re.search(doi_pattern, text)
        if match:
            return match.group(0).rstrip('.,;')  # 移除末尾标点
        return None
    
    async def get_citation_chain(self, doi: str, depth: int = 1) -> Dict[str, Any]:
        """获取引用链"""
        result = {
            "doi": doi,
            "citations": [],
            "references": [],
        }
        
        # 获取引用该论文的文献
        citations = await self.crossref.get_citations(doi)
        result["citations"] = citations
        
        # 获取该论文引用的文献
        references = await self.crossref.get_references(doi)
        result["references"] = references
        
        return result


# 便捷函数
async def get_paper_metadata(doi: str) -> Optional[Dict[str, Any]]:
    """获取论文元数据"""
    service = MetadataService()
    result = await service.enrich_from_doi(doi)
    return result.get("data")


async def search_papers(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """搜索论文"""
    service = MetadataService()
    return await service.search(query, limit)
