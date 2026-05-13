"""论文缓存服务 - 缓存热门论文和搜索结果"""

import time
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

# 简单的内存缓存
_cache: Dict[str, Dict[str, Any]] = {}

# 缓存过期时间（秒）
CACHE_EXPIRY = {
    "popular": 3600,      # 热门论文缓存 1 小时
    "search": 1800,       # 搜索结果缓存 30 分钟
    "recommendations": 3600,  # 推荐论文缓存 1 小时
}


def get_cache(key: str) -> Optional[Any]:
    """获取缓存"""
    if key in _cache:
        entry = _cache[key]
        if time.time() - entry["timestamp"] < entry["expiry"]:
            logger.info(f"Cache hit: {key}")
            return entry["data"]
        else:
            # 缓存过期，删除
            del _cache[key]
            logger.info(f"Cache expired: {key}")
    return None


def set_cache(key: str, data: Any, cache_type: str = "search") -> None:
    """设置缓存"""
    expiry = CACHE_EXPIRY.get(cache_type, 1800)
    _cache[key] = {
        "data": data,
        "timestamp": time.time(),
        "expiry": expiry,
    }
    logger.info(f"Cache set: {key}, expiry: {expiry}s")


def clear_cache(key: str = None) -> None:
    """清除缓存"""
    if key:
        if key in _cache:
            del _cache[key]
    else:
        _cache.clear()


def get_cached_recommendations() -> Optional[List[Dict[str, Any]]]:
    """获取缓存的推荐论文"""
    return get_cache("daily_recommendations")


def set_cached_recommendations(papers: List[Dict[str, Any]]) -> None:
    """缓存推荐论文"""
    set_cache("daily_recommendations", papers, "recommendations")


def get_cached_search(query: str) -> Optional[List[Dict[str, Any]]]:
    """获取缓存的搜索结果"""
    return get_cache(f"search:{query.lower()}")


def set_cached_search(query: str, papers: List[Dict[str, Any]]) -> None:
    """缓存搜索结果"""
    set_cache(f"search:{query.lower()}", papers, "search")


def get_cached_popular() -> Optional[List[Dict[str, Any]]]:
    """获取缓存的热门论文"""
    return get_cache("popular_papers")


def set_cached_popular(papers: List[Dict[str, Any]]) -> None:
    """缓存热门论文"""
    set_cache("popular_papers", papers, "popular")