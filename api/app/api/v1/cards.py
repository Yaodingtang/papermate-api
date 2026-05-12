from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_db, get_current_user
from app.models import User, Paper, Card
from app.schemas import CardCreate, CardResponse, CardUpdate

router = APIRouter(prefix="/cards", tags=["卡片"])


@router.post("", response_model=CardResponse, status_code=201)
async def create_card(
    card_data: CardCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """创建知识卡片"""
    # 验证论文存在且属于用户
    result = await db.execute(
        select(Paper).where(Paper.id == card_data.paper_id, Paper.user_id == current_user.id)
    )
    paper = result.scalar_one_or_none()
    
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    card = Card(
        paper_id=card_data.paper_id,
        user_id=current_user.id,
        question=card_data.question,
        answer=card_data.answer,
        order=card_data.order,
    )
    db.add(card)
    await db.commit()
    await db.refresh(card)
    
    return card


@router.get("", response_model=list[CardResponse])
async def list_cards(
    paper_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取论文的知识卡片"""
    # 验证论文存在且属于用户
    result = await db.execute(
        select(Paper).where(Paper.id == paper_id, Paper.user_id == current_user.id)
    )
    paper = result.scalar_one_or_none()
    
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    result = await db.execute(
        select(Card).where(Card.paper_id == paper_id).order_by(Card.order)
    )
    cards = result.scalars().all()
    
    return cards


@router.patch("/{card_id}", response_model=CardResponse)
async def update_card(
    card_id: str,
    update_data: CardUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新知识卡片"""
    result = await db.execute(
        select(Card).where(Card.id == card_id, Card.user_id == current_user.id)
    )
    card = result.scalar_one_or_none()
    
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    
    if update_data.answer is not None:
        card.answer = update_data.answer
    
    await db.commit()
    await db.refresh(card)
    
    return card


@router.delete("/{card_id}")
async def delete_card(
    card_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除知识卡片"""
    result = await db.execute(
        select(Card).where(Card.id == card_id, Card.user_id == current_user.id)
    )
    card = result.scalar_one_or_none()
    
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    
    await db.delete(card)
    await db.commit()
    
    return {"message": "Card deleted successfully"}