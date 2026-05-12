from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.api.deps import get_db, get_current_user
from app.models import User, Paper
from app.schemas import UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["用户"])


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    """获取当前用户信息"""
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_current_user(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新当前用户信息"""
    if update_data.name is not None:
        current_user.name = update_data.name
    if update_data.avatar_url is not None:
        current_user.avatar_url = update_data.avatar_url
    if update_data.settings is not None:
        current_user.settings = update_data.settings
    
    await db.commit()
    await db.refresh(current_user)
    
    return current_user


@router.get("/me/stats")
async def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取用户统计数据"""
    # 论文统计
    total_papers = await db.execute(
        select(func.count(Paper.id)).where(Paper.user_id == current_user.id)
    )
    
    reading_papers = await db.execute(
        select(func.count(Paper.id)).where(
            Paper.user_id == current_user.id,
            Paper.status == "reading",
        )
    )
    
    completed_papers = await db.execute(
        select(func.count(Paper.id)).where(
            Paper.user_id == current_user.id,
            Paper.status == "completed",
        )
    )
    
    return {
        "total_papers": total_papers.scalar(),
        "reading_papers": reading_papers.scalar(),
        "completed_papers": completed_papers.scalar(),
    }