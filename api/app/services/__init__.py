"""服务模块"""
from app.services.pdf_service import PDFParser, parse_pdf
from app.services.metadata_service import (
    CrossrefService,
    MetadataService,
    get_paper_metadata,
    search_papers,
)
from app.services.arxiv_service import (
    ArxivService,
    search_arxiv,
    get_arxiv_recent,
    get_arxiv_popular,
)
from app.services.semantic_scholar_service import (
    SemanticScholarService,
    search_semantic_scholar,
    get_trending_papers,
    get_paper_recommendations,
)
from app.services.cache_service import (
    get_cache,
    set_cache,
    clear_cache,
    get_cached_recommendations,
    set_cached_recommendations,
    get_cached_search,
    set_cached_search,
    get_cached_popular,
    set_cached_popular,
)

__all__ = [
    "PDFParser",
    "parse_pdf",
    "CrossrefService",
    "MetadataService",
    "get_paper_metadata",
    "search_papers",
    "ArxivService",
    "search_arxiv",
    "get_arxiv_recent",
    "get_arxiv_popular",
    "SemanticScholarService",
    "search_semantic_scholar",
    "get_trending_papers",
    "get_paper_recommendations",
    "get_cache",
    "set_cache",
    "clear_cache",
    "get_cached_recommendations",
    "set_cached_recommendations",
    "get_cached_search",
    "set_cached_search",
    "get_cached_popular",
    "set_cached_popular",
]
