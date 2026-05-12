from fastapi import APIRouter, Depends
from typing import List
from datetime import datetime, timedelta

from app.models import StatsOverview
from app.api.deps import get_current_user

router = APIRouter()


@router.get("/overview")
async def get_stats_overview(
    period: str = "week",
    user = Depends(get_current_user)
):
    """获取统计数据概览"""
    
    # 模拟统计数据
    return {
        "papers_read": 15,
        "reading_time": 1200,  # 分钟
        "annotations": 45,
        "cards_created": 12,
        "field_distribution": [
            {"field": "NLP", "count": 10, "percentage": 40},
            {"field": "Computer Vision", "count": 8, "percentage": 32},
            {"field": "Machine Learning", "count": 5, "percentage": 20},
            {"field": "Reinforcement Learning", "count": 2, "percentage": 8}
        ],
        "keyword_cloud": [
            {"keyword": "Transformer", "count": 25},
            {"keyword": "Attention", "count": 20},
            {"keyword": "BERT", "count": 15},
            {"keyword": "GPT", "count": 12},
            {"keyword": "Fine-tuning", "count": 10},
            {"keyword": "Pre-training", "count": 8},
            {"keyword": "Neural Network", "count": 6}
        ],
        "weekly_trend": [
            {"date": "2024-05-06", "papers": 2, "time": 120},
            {"date": "2024-05-07", "papers": 3, "time": 180},
            {"date": "2024-05-08", "papers": 1, "time": 60},
            {"date": "2024-05-09", "papers": 4, "time": 240},
            {"date": "2024-05-10", "papers": 2, "time": 150},
            {"date": "2024-05-11", "papers": 3, "time": 200},
            {"date": "2024-05-12", "papers": 0, "time": 0}
        ],
        "goals": {
            "daily_papers": {"target": 3, "current": 2},
            "weekly_papers": {"target": 15, "current": 15},
            "monthly_papers": {"target": 50, "current": 32}
        },
        "achievements": [
            {"id": 1, "name": "初学者", "description": "阅读第一篇论文", "unlocked": True},
            {"id": 2, "name": "勤奋者", "description": "连续7天阅读", "unlocked": True},
            {"id": 3, "name": "学者", "description": "阅读100篇论文", "unlocked": False, "progress": 32}
        ]
    }


@router.get("/reading-history")
async def get_reading_history(
    days: int = 30,
    user = Depends(get_current_user)
):
    """获取阅读历史"""
    
    history = []
    for i in range(days):
        date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        history.append({
            "date": date,
            "papers_read": 2 + (i % 4),
            "reading_time": 60 + (i % 3) * 30,
            "annotations": 3 + (i % 5)
        })
    
    return {"history": history}


@router.get("/achievements")
async def get_achievements(user = Depends(get_current_user)):
    """获取成就列表"""
    
    return {
        "achievements": [
            {"id": 1, "name": "初学者", "description": "阅读第一篇论文", "icon": "book", "unlocked": True, "unlocked_at": "2024-01-01"},
            {"id": 2, "name": "勤奋者", "description": "连续7天阅读", "icon": "fire", "unlocked": True, "unlocked_at": "2024-02-15"},
            {"id": 3, "name": "批注达人", "description": "创建100条批注", "icon": "pen", "unlocked": True, "unlocked_at": "2024-03-01"},
            {"id": 4, "name": "学者", "description": "阅读100篇论文", "icon": "graduate", "unlocked": False, "progress": 32},
            {"id": 5, "name": "知识大师", "description": "创建500张知识卡片", "icon": "brain", "unlocked": False, "progress": 45},
            {"id": 6, "name": "社交达人", "description": "加入10个团队", "icon": "users", "unlocked": False, "progress": 2}
        ],
        "total_points": 350,
        "level": 5
    }