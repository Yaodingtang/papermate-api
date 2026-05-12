from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from app.core.database import create_db_and_tables
from app.api.v1 import auth, papers, annotations, cards, ai, daily, stats

# 创建应用
app = FastAPI(
    title="PaperMate Pro API",
    description="智能论文管理平台后端 API",
    version="1.0.0"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api/v1", tags=["认证"])
app.include_router(papers.router, prefix="/api/v1/papers", tags=["论文"])
app.include_router(annotations.router, prefix="/api/v1", tags=["批注"])
app.include_router(cards.router, prefix="/api/v1/cards", tags=["知识卡片"])
app.include_router(ai.router, prefix="/api/v1/ai", tags=["AI功能"])
app.include_router(daily.router, prefix="/api/v1/daily", tags=["每日推送"])
app.include_router(stats.router, prefix="/api/v1/stats", tags=["统计"])


@app.on_event("startup")
async def on_startup():
    """应用启动时创建数据库"""
    await create_db_and_tables()


@app.get("/")
async def root():
    return {
        "message": "PaperMate Pro API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}