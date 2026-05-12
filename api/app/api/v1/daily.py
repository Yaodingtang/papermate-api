from fastapi import APIRouter, Depends
from typing import List
from datetime import datetime, timedelta

from app.models import (
    DailyRecommendation, DailySettings, DailyInterests,
    StatsOverview
)
from app.api.deps import get_current_user

router = APIRouter()


@router.get("/recommendations")
async def get_daily_recommendations(user = Depends(get_current_user)):
    """获取每日推荐论文"""
    
    # 模拟推荐数据
    recommendations = [
        {
            "id": 1,
            "title": "Mixture of Experts Meets Instruction Tuning",
            "authors": "Wang et al.",
            "year": 2024,
            "venue": "arXiv",
            "reason": "基于你关注的大语言模型领域",
            "relevance": 95
        },
        {
            "id": 2,
            "title": "Efficient Long-Context Transformers",
            "authors": "Chen et al.",
            "year": 2024,
            "venue": "ICLR 2024",
            "reason": "与你最近阅读的 Transformer 相关",
            "relevance": 88
        },
        {
            "id": 3,
            "title": "Multimodal Foundation Models: A Survey",
            "authors": "Li et al.",
            "year": 2024,
            "venue": "arXiv",
            "reason": "热门综述论文",
            "relevance": 82
        },
        {
            "id": 4,
            "title": "Self-Play Reinforcement Learning for LLM Reasoning",
            "authors": "Zhang et al.",
            "year": 2024,
            "venue": "NeurIPS 2024",
            "reason": "新方法，可能启发你的研究",
            "relevance": 78
        },
        {
            "id": 5,
            "title": "Parameter-Efficient Fine-Tuning: A Comprehensive Study",
            "authors": "Liu et al.",
            "year": 2024,
            "venue": "ACL 2024",
            "reason": "与你收藏的 LoRA 相关",
            "relevance": 75
        }
    ]
    
    return {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "papers": recommendations
    }


@router.patch("/settings")
async def update_daily_settings(
    settings: DailySettings,
    user = Depends(get_current_user)
):
    """更新推送设置"""
    
    return {
        "message": "设置已更新",
        "settings": settings
    }


@router.patch("/interests")
async def update_research_interests(
    interests: DailyInterests,
    user = Depends(get_current_user)
):
    """更新研究兴趣"""
    
    return {
        "message": "研究兴趣已更新",
        "interests": interests.interests
    }


@router.get("/history")
async def get_push_history(
    days: int = 7,
    user = Depends(get_current_user)
):
    """获取推送历史"""
    
    history = []
    for i in range(days):
        date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        history.append({
            "date": date,
            "count": 5,
            "read": 3 - (i % 3),
            "saved": 2 - (i % 2)
        })
    
    return {"history": history}